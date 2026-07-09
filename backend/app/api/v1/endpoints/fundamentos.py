from fastapi import APIRouter, HTTPException

from app.schemas.fundamentos import FundamentosSchema
from app.services.fundamentals_service import FundamentalsService

router = APIRouter(prefix="/ativos", tags=["Fundamentos"])
_service = FundamentalsService()


@router.get("/{ticker}/fundamentos", response_model=FundamentosSchema)
def obter_fundamentos(ticker: str) -> FundamentosSchema:
    """
    Retorna indicadores fundamentalistas (P/L, P/VP, ROE, margem
    liquida, divida/patrimonio, dividend yield) do ativo, obtidos ao
    vivo via Yahoo Finance.

    Fundamentos refletem a saude financeira HISTORICA/ATUAL da empresa
    -- nao sao garantia de desempenho futuro da acao.
    """
    try:
        return _service.obter(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc