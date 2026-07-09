import pandas as pd
from sqlalchemy.orm import Session

from app import crud
from app.schemas.indicadores import (
    BollingerSchema,
    IndicadoresTecnicosSchema,
    MACDSchema,
    MediasMoveisSchema,
)
from app.services.indicators import technical
from app.services.market_data_service import normalizar_ticker


class IndicatorsService:
    """
    Orquestra o calculo de indicadores tecnicos a partir do historico
    JA SALVO no banco de dados (o ativo precisa ter sido sincronizado
    antes via POST /ativos/{ticker}/sincronizar).
    """

    def calcular(self, db: Session, ticker: str) -> IndicadoresTecnicosSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        ativo = crud.ativo.get_by_ticker(db, ticker_normalizado)
        if ativo is None:
            raise ValueError(
                f"Ativo '{ticker}' nao encontrado. Cadastre e sincronize o "
                "historico primeiro (POST /ativos/{ticker}/sincronizar)."
            )

        cotacoes = crud.cotacao_historica.listar_por_ativo(db, ativo.id)
        if len(cotacoes) < 20:
            raise ValueError(
                f"Historico insuficiente para calcular indicadores "
                f"({len(cotacoes)} candles). Sincronize um periodo maior, "
                "ex: period=1y."
            )

        df = pd.DataFrame(
            [
                {
                    "data": c.data,
                    "maxima": float(c.maxima),
                    "minima": float(c.minima),
                    "fechamento": float(c.fechamento),
                }
                for c in cotacoes
            ]
        )
        fechamento = df["fechamento"]

        macd_df = technical.calcular_macd(fechamento)
        bollinger_df = technical.calcular_bandas_bollinger(fechamento)
        suporte_resistencia = technical.identificar_suporte_resistencia(df)
        tendencia = technical.identificar_tendencia(fechamento)

        def ultimo_valor(series: pd.Series) -> float | None:
            valor = series.iloc[-1]
            return None if pd.isna(valor) else round(float(valor), 4)

        return IndicadoresTecnicosSchema(
            ticker=ativo.ticker,
            ultima_data=str(df["data"].iloc[-1]),
            ultimo_fechamento=round(float(fechamento.iloc[-1]), 4),
            medias_moveis=MediasMoveisSchema(
                sma_20=ultimo_valor(technical.calcular_sma(fechamento, 20)),
                sma_50=ultimo_valor(technical.calcular_sma(fechamento, 50)),
                sma_200=ultimo_valor(technical.calcular_sma(fechamento, 200)),
                ema_12=ultimo_valor(technical.calcular_ema(fechamento, 12)),
                ema_26=ultimo_valor(technical.calcular_ema(fechamento, 26)),
            ),
            rsi_14=ultimo_valor(technical.calcular_rsi(fechamento, 14)),
            macd=MACDSchema(
                macd=ultimo_valor(macd_df["macd"]),
                sinal=ultimo_valor(macd_df["sinal"]),
                histograma=ultimo_valor(macd_df["histograma"]),
            ),
            bollinger=BollingerSchema(
                banda_media=ultimo_valor(bollinger_df["banda_media"]),
                banda_superior=ultimo_valor(bollinger_df["banda_superior"]),
                banda_inferior=ultimo_valor(bollinger_df["banda_inferior"]),
            ),
            suporte=suporte_resistencia["suporte"],
            resistencia=suporte_resistencia["resistencia"],
            tendencia=tendencia,
        )