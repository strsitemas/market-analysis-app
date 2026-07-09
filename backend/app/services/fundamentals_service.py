import yfinance as yf

from app.schemas.fundamentos import FundamentosSchema
from app.services.market_data_service import normalizar_ticker


class FundamentalsService:
    """
    Busca indicadores fundamentalistas AO VIVO via yfinance (campo
    .info). Nao persiste no banco -- fundamentos mudam pouco no
    dia a dia, entao cache de curto prazo seria suficiente, mas por
    simplicidade nesta etapa buscamos direto (podemos adicionar cache
    Redis aqui depois, no mesmo padrao do MarketDataService).

    NOTA TECNICA: a partir do yfinance 1.x, o campo dividendYield ja
    vem em PONTOS PERCENTUAIS (ex: 10.19 significa 10,19%), diferente
    de versoes antigas que retornavam fracao (0.1019). Por isso, aqui
    NAO multiplicamos por 100 -- so arredondamos. Verificado contra
    fonte externa (Morningstar) em 2026-07-05.
    """

    def obter(self, ticker: str) -> FundamentosSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        info = yf.Ticker(ticker_normalizado).info

        if not info or info.get("regularMarketPrice") is None:
            raise ValueError(
                f"Nao foi possivel obter dados fundamentalistas para "
                f"'{ticker_normalizado}'."
            )

        roe = info.get("returnOnEquity")
        margem = info.get("profitMargins")
        dividend_yield = info.get("dividendYield")

        return FundamentosSchema(
            ticker=ticker_normalizado,
            nome_empresa=info.get("longName") or info.get("shortName"),
            setor=info.get("sector"),
            pl=info.get("trailingPE"),
            pvp=info.get("priceToBook"),
            roe_pct=round(roe * 100, 2) if roe is not None else None,
            margem_liquida_pct=round(margem * 100, 2) if margem is not None else None,
            divida_patrimonio=info.get("debtToEquity"),
            dividend_yield_pct=(
                round(dividend_yield, 2) if dividend_yield is not None else None
            ),
        )