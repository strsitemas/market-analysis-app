from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.ativos_disponiveis import ATIVOS_DISPONIVEIS
from app.db.session import get_db
from app.schemas.analise import (
    AnaliseCompletaSchema,
    AnaliseMultiplaSchema,
    AtivoDisponivelSchema,
)
from app.services.analise_service import AnaliseService

router = APIRouter(tags=["Analise Consolidada"])
_service = AnaliseService()


@router.get("/ativos/disponiveis", response_model=list[AtivoDisponivelSchema])
def listar_ativos_disponiveis() -> list[AtivoDisponivelSchema]:
    """Lista os ativos disponiveis para selecao (catalogo estatico)."""
    return [AtivoDisponivelSchema(**item) for item in ATIVOS_DISPONIVEIS]


@router.get("/ativos/{ticker}/analise-completa", response_model=AnaliseCompletaSchema)
def obter_analise_completa(
    ticker: str, db: Session = Depends(get_db)
) -> AnaliseCompletaSchema:
    """
    Retorna a linha completa de analise de um ativo: tecnico,
    estatisticas, fundamentos, scores de risco/oportunidade e sinal
    final.
    """
    return _service.obter_analise_completa(db, ticker)


@router.get("/analise", response_model=AnaliseMultiplaSchema)
def obter_analise_multipla(
    tickers: str = Query(
        ..., description="Tickers separados por virgula, ex: PETR4,VALE3,ITUB4"
    ),
    db: Session = Depends(get_db),
) -> AnaliseMultiplaSchema:
    """
    Retorna a analise completa de varios ativos de uma vez, para
    montar a tabela comparativa no frontend.
    """
    lista_tickers = [t.strip() for t in tickers.split(",") if t.strip()]
    return _service.obter_analise_multipla(db, lista_tickers)