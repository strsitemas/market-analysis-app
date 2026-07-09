from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tabela_tecnica import TabelaTecnicaSchema
from app.services.tabela_tecnica_service import TabelaTecnicaService

router = APIRouter(prefix="/ativos", tags=["Tabela Tecnica"])
_service = TabelaTecnicaService()


@router.get("/{ticker}/tabela-tecnica", response_model=TabelaTecnicaSchema)
def obter_tabela_tecnica(ticker: str, db: Session = Depends(get_db)) -> TabelaTecnicaSchema:
    """
    Retorna a linha consolidada de analise tecnica do ativo: cotacao
    ao vivo + indicadores calculados sobre o historico salvo no banco.
    Requer que o ativo tenha sido sincronizado antes.
    """
    try:
        return _service.montar(db, ticker)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Nao foi possivel montar a tabela tecnica de '{ticker}': {exc}. "
            "Sincronize o ativo primeiro (POST /ativos/{ticker}/sincronizar).",
        ) from exc