from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.indicadores import IndicadoresTecnicosSchema
from app.services.indicators_service import IndicatorsService

router = APIRouter(prefix="/ativos", tags=["Indicadores Tecnicos"])
_indicators_service = IndicatorsService()


@router.get("/{ticker}/indicadores", response_model=IndicadoresTecnicosSchema)
def obter_indicadores(ticker: str, db: Session = Depends(get_db)) -> IndicadoresTecnicosSchema:
    """
    Calcula indicadores tecnicos (medias moveis, RSI, MACD, Bollinger,
    suporte/resistencia, tendencia) com base no historico ja salvo no banco.

    Estes indicadores sao ferramentas de apoio a decisao, baseadas em
    estatistica sobre precos passados -- NAO constituem garantia de
    comportamento futuro do ativo.
    """
    try:
        return _indicators_service.calcular(db, ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc