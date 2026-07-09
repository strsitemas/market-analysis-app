from datetime import datetime, timezone

import yfinance as yf

from app.schemas.market_data import (
    HistoricalPricePoint,
    HistoricalPriceSchema,
    QuoteSchema,
)
from app.services.market_data.base import MarketDataProvider


class YFinanceProvider(MarketDataProvider):
    """
    Implementacao de MarketDataProvider usando a biblioteca yfinance.

    AVISO: yfinance obtem dados do Yahoo Finance de forma nao-oficial
    (via raspagem/API nao documentada publicamente). Adequado para
    prototipagem e estudo. Para producao real, recomenda-se avaliar
    fontes oficiais ou provedores pagos com SLA.
    """

    def get_quote(self, ticker: str) -> QuoteSchema:
        ativo = yf.Ticker(ticker)
        info = ativo.fast_info

        preco_atual = float(info["last_price"])
        fechamento_anterior = float(info["previous_close"])
        variacao_pct = (
            (preco_atual - fechamento_anterior) / fechamento_anterior
        ) * 100

        return QuoteSchema(
            ticker=ticker,
            preco_atual=preco_atual,
            variacao_diaria_pct=round(variacao_pct, 2),
            volume=int(info["last_volume"]),
            data_hora=datetime.now(timezone.utc),
            moeda=info.get("currency", "BRL"),
        )

    def get_history(
        self,
        ticker: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> HistoricalPriceSchema:
        ativo = yf.Ticker(ticker)
        df = ativo.history(period=period, interval=interval)

        if df.empty:
            raise ValueError(
                f"Nenhum dado historico encontrado para o ticker '{ticker}'. "
                "Verifique se o codigo esta correto (ex: PETR4.SA para B3)."
            )

        pontos = [
            HistoricalPricePoint(
                data=index.date(),
                abertura=round(float(row["Open"]), 2),
                maxima=round(float(row["High"]), 2),
                minima=round(float(row["Low"]), 2),
                fechamento=round(float(row["Close"]), 2),
                volume=int(row["Volume"]),
            )
            for index, row in df.iterrows()
        ]

        return HistoricalPriceSchema(ticker=ticker, pontos=pontos)