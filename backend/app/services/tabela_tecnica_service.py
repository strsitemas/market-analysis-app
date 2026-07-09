from sqlalchemy.orm import Session

from app import crud
from app.schemas.tabela_tecnica import TabelaTecnicaSchema
from app.services.indicators_service import IndicatorsService
from app.services.market_data_service import MarketDataService, normalizar_ticker


class TabelaTecnicaService:
    """
    Orquestra a montagem da tabela tecnica: busca a cotacao AO VIVO
    (preco atual, variacao, volume) e combina com os indicadores
    calculados a partir do historico JA SALVO no banco.
    """

    def __init__(
        self,
        market_data_service: MarketDataService | None = None,
        indicators_service: IndicatorsService | None = None,
    ) -> None:
        self._market_data_service = market_data_service or MarketDataService()
        self._indicators_service = indicators_service or IndicatorsService()

    def montar(self, db: Session, ticker: str) -> TabelaTecnicaSchema:
        ticker_normalizado = normalizar_ticker(ticker)

        quote = self._market_data_service.get_quote(ticker_normalizado)
        indicadores = self._indicators_service.calcular(db, ticker_normalizado)

        ativo = crud.ativo.get_by_ticker(db, ticker_normalizado)
        cotacoes = crud.cotacao_historica.listar_por_ativo(db, ativo.id)
        ultimos_20 = cotacoes[-20:]
        liquidez_media_20d = sum(c.volume for c in ultimos_20) / len(ultimos_20)

        return TabelaTecnicaSchema(
            ticker=ticker_normalizado,
            preco_atual=quote.preco_atual,
            variacao_diaria_pct=quote.variacao_diaria_pct,
            volume=quote.volume,
            liquidez_media_20d=round(liquidez_media_20d, 0),
            tendencia=indicadores.tendencia,
            suporte=indicadores.suporte,
            resistencia=indicadores.resistencia,
            medias_moveis=indicadores.medias_moveis,
            rsi_14=indicadores.rsi_14,
            macd=indicadores.macd,
            bollinger=indicadores.bollinger,
        )