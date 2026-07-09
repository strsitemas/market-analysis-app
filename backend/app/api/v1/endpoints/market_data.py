from fastapi import APIRouter, HTTPException, Query

from app.schemas.market_data import HistoricalPriceSchema, QuoteSchema
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/ativos", tags=["Market Data"])

_service = MarketDataService()


@router.get("/{ticker}/cotacao", response_model=QuoteSchema)
def get_cotacao(ticker: str) -> QuoteSchema:
    """
    Retorna a cotacao mais recente disponivel para o ticker informado.
    Exemplo: /api/v1/ativos/PETR4/cotacao ou /api/v1/ativos/AAPL/cotacao
    """
    try:
        return _service.get_quote(ticker)
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Nao foi possivel obter cotacao para '{ticker}': {exc}",
        ) from exc


@router.get("/{ticker}/historico", response_model=HistoricalPriceSchema)
def get_historico(
    ticker: str,
    period: str = Query(
        default="6mo",
        description="Janela de tempo: 1mo, 3mo, 6mo, 1y, 5y, max",
    ),
    interval: str = Query(
        default="1d",
        description="Granularidade: 1d, 1wk, 1mo",
    ),
) -> HistoricalPriceSchema:
    """
    Retorna o historico de precos (OHLCV) do ticker informado.
    """
    try:
        return _service.get_history(ticker, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc