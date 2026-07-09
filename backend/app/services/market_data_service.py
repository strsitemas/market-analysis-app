from app.schemas.market_data import HistoricalPriceSchema, QuoteSchema
from app.services.cache_service import CacheService
from app.services.market_data.base import MarketDataProvider
from app.services.market_data.yfinance_provider import YFinanceProvider

QUOTE_CACHE_TTL_SECONDS = 60
HISTORY_CACHE_TTL_SECONDS = 60 * 60  # 1 hora


def normalizar_ticker(ticker: str) -> str:
    """
    Normaliza tickers da B3 adicionando o sufixo '.SA' esperado pelo
    yfinance, caso o usuario nao tenha informado.
    """
    ticker = ticker.strip().upper()
    if "." in ticker:
        return ticker

    parece_ticker_b3 = (
        len(ticker) in (5, 6) and ticker[-1].isdigit()
    )
    if parece_ticker_b3:
        return f"{ticker}.SA"

    return ticker


class MarketDataService:
    """
    Servico responsavel por fornecer dados de mercado ao restante da
    aplicacao, combinando a fonte de dados (provider) com cache.
    """

    def __init__(self, provider: MarketDataProvider | None = None) -> None:
        self._provider = provider or YFinanceProvider()

    def get_quote(self, ticker: str) -> QuoteSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        cache_key = f"quote:{ticker_normalizado}"

        return CacheService.get_or_set_model(
            key=cache_key,
            ttl_seconds=QUOTE_CACHE_TTL_SECONDS,
            model_class=QuoteSchema,
            fetch_fn=lambda: self._provider.get_quote(ticker_normalizado),
        )

    def get_history(
        self,
        ticker: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> HistoricalPriceSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        cache_key = f"history:{ticker_normalizado}:{period}:{interval}"

        return CacheService.get_or_set_model(
            key=cache_key,
            ttl_seconds=HISTORY_CACHE_TTL_SECONDS,
            model_class=HistoricalPriceSchema,
            fetch_fn=lambda: self._provider.get_history(
                ticker_normalizado, period, interval
            ),
        )