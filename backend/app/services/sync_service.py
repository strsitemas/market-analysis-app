from sqlalchemy.orm import Session

from app import crud
from app.services.market_data_service import MarketDataService, normalizar_ticker


class SyncService:
    """
    Busca dados no provider externo (Yahoo Finance, via MarketDataService)
    e PERSISTE no banco de dados Postgres. Separa "buscar ao vivo" de
    "gravar para uso futuro".
    """

    def __init__(self, market_data_service: MarketDataService | None = None) -> None:
        self._market_data_service = market_data_service or MarketDataService()

    def sincronizar_historico(
        self,
        db: Session,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> dict:
        ticker_normalizado = normalizar_ticker(ticker)

        ativo = crud.ativo.obter_ou_criar(db, ticker_normalizado)

        historico = self._market_data_service.get_history(
            ticker_normalizado, period, interval
        )

        pontos = [
            {
                "data": ponto.data,
                "abertura": ponto.abertura,
                "maxima": ponto.maxima,
                "minima": ponto.minima,
                "fechamento": ponto.fechamento,
                "volume": ponto.volume,
            }
            for ponto in historico.pontos
        ]

        quantidade = crud.cotacao_historica.upsert_lote(db, ativo.id, pontos)

        return {
            "ativo": ativo.ticker,
            "ativo_id": ativo.id,
            "pontos_sincronizados": quantidade,
        }