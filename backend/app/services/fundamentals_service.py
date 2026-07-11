import yfinance as yf

from app.schemas.fundamentos import FundamentosSchema
from app.services.cache_service import CacheService
from app.services.market_data_service import normalizar_ticker

FUNDAMENTOS_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 horas


class FundamentalsService:
    """
    Busca indicadores fundamentalistas via yfinance (campo .info),
    com cache de 24h no Redis.

    Motivo tecnico do cache: fundamentos (P/L, ROE, dividend yield
    etc.) mudam muito pouco no dia a dia -- normalmente uma vez por
    trimestre, quando a empresa publica balanco. Buscar ao vivo a
    cada requisicao gera uma rajada de chamadas ao Yahoo Finance
    quando varios tickers sao consultados de uma vez (rota
    /analise?tickers=...), o que pode disparar rate limit do provedor
    externo e derrubar a resposta. Cachear por 24h elimina a maior
    parte dessas chamadas repetidas sem prejudicar a atualidade do
    dado (fundamentos de ontem sao, na pratica, iguais aos de hoje).

    NOTA TECNICA: a partir do yfinance 1.x, o campo dividendYield ja
    vem como percentual (9.83), diferente de versoes antigas que
    retornavam fracao (0.1019). Por isso, aqui NAO multiplicamos por
    100 -- so arredondamos. Verificado contra fonte externa
    (Morningstar) em 2026-07-05.
    """

    def obter(self, ticker: str) -> FundamentosSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        cache_key = f"fundamentos:{ticker_normalizado}"

        return CacheService.get_or_set_model(
            key=cache_key,
            ttl_seconds=FUNDAMENTOS_CACHE_TTL_SECONDS,
            model_class=FundamentosSchema,
            fetch_fn=lambda: self._buscar_ao_vivo(ticker_normalizado),
        )

    def _buscar_ao_vivo(self, ticker_normalizado: str) -> FundamentosSchema:
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