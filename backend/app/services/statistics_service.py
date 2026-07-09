import pandas as pd
from sqlalchemy.orm import Session

from app import crud
from app.schemas.estatisticas import EstatisticasSchema
from app.services.market_data_service import MarketDataService, normalizar_ticker
from app.services.statistics import technical_stats

TICKER_INDICE_REFERENCIA = "^BVSP"  # Ibovespa


class StatisticsService:
    """
    Calcula metricas estatisticas (volatilidade, retorno acumulado,
    drawdown, correlacao) com base no historico JA SALVO no banco para
    o ativo, e no historico AO VIVO (via Yahoo) para o indice de
    referencia -- o indice nao precisa estar cadastrado/sincronizado
    no banco, pois e usado so para comparacao.
    """

    def __init__(self, market_data_service: MarketDataService | None = None) -> None:
        self._market_data_service = market_data_service or MarketDataService()

    def calcular(
        self, db: Session, ticker: str, period: str = "1y"
    ) -> EstatisticasSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        ativo = crud.ativo.get_by_ticker(db, ticker_normalizado)
        if ativo is None:
            raise ValueError(
                f"Ativo '{ticker}' nao encontrado. Sincronize o historico "
                "primeiro (POST /ativos/{ticker}/sincronizar)."
            )

        cotacoes = crud.cotacao_historica.listar_por_ativo(db, ativo.id)
        if len(cotacoes) < 10:
            raise ValueError(
                f"Historico insuficiente para calcular estatisticas "
                f"({len(cotacoes)} candles). Sincronize um periodo maior."
            )

        fechamento_ativo = pd.Series(
            [float(c.fechamento) for c in cotacoes],
            index=[c.data for c in cotacoes],
        )

        volatilidade = technical_stats.calcular_volatilidade_anualizada(fechamento_ativo)
        retorno_acumulado = technical_stats.calcular_retorno_acumulado(fechamento_ativo)
        drawdown_maximo = technical_stats.calcular_drawdown_maximo(fechamento_ativo)

        correlacao = self._calcular_correlacao_com_indice(fechamento_ativo, period)

        return EstatisticasSchema(
            ticker=ativo.ticker,
            periodo_analisado=f"{cotacoes[0].data} a {cotacoes[-1].data}",
            volatilidade_anualizada_pct=round(volatilidade, 2),
            retorno_acumulado_pct=round(retorno_acumulado, 2),
            drawdown_maximo_pct=round(drawdown_maximo, 2),
            correlacao_ibovespa=(
                round(correlacao, 4) if correlacao is not None else None
            ),
        )

    def _calcular_correlacao_com_indice(
        self, fechamento_ativo: pd.Series, period: str
    ) -> float | None:
        try:
            historico_indice = self._market_data_service.get_history(
                TICKER_INDICE_REFERENCIA, period=period, interval="1d"
            )
        except ValueError:
            # Indice indisponivel no momento -- nao impede o resto da analise
            return None

        fechamento_indice = pd.Series(
            [p.fechamento for p in historico_indice.pontos],
            index=[p.data for p in historico_indice.pontos],
        )

        return technical_stats.calcular_correlacao(fechamento_ativo, fechamento_indice)