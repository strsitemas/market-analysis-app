from abc import ABC, abstractmethod

from app.schemas.market_data import HistoricalPriceSchema, QuoteSchema


class MarketDataProvider(ABC):
    """
    Interface (contrato) para qualquer fonte de dados de mercado.

    Motivo tecnico: isolar o restante da aplicacao da implementacao
    concreta de uma fonte de dados especifica (ex: yfinance). Se a fonte
    mudar no futuro (ex: para uma API paga da B3), basta criar uma nova
    classe que implemente esta interface, sem alterar os services que
    a consomem (Dependency Inversion Principle).
    """

    @abstractmethod
    def get_quote(self, ticker: str) -> QuoteSchema:
        """Retorna a cotacao mais recente disponivel para o ticker."""
        raise NotImplementedError

    @abstractmethod
    def get_history(
        self,
        ticker: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> HistoricalPriceSchema:
        """
        Retorna o historico de precos do ticker.

        period: janela de tempo (ex: '1mo', '6mo', '1y', '5y')
        interval: granularidade dos dados (ex: '1d', '1wk', '1mo')
        """
        raise NotImplementedError