from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sinal import SinalFinalSchema
from app.services.sinal_service import SinalService

router = APIRouter(prefix="/ativos", tags=["Sinal Final"])
_service = SinalService()


@router.get("/{ticker}/sinal", response_model=SinalFinalSchema)
def obter_sinal(ticker: str, db: Session = Depends(get_db)) -> SinalFinalSchema:
    """
    Gera o sinal final de analise: compra, venda, atencao ou neutro.

    Este sinal e uma ferramenta de apoio a decisao baseada em analise
    probabilistica de risco e oportunidade -- NAO e recomendacao de
    investimento nem promessa de resultado futuro.
    """
    try:
        return _service.gerar(db, ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc