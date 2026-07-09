from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.estatisticas import EstatisticasSchema
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/ativos", tags=["Estatisticas"])
_service = StatisticsService()


@router.get("/{ticker}/estatisticas", response_model=EstatisticasSchema)
def obter_estatisticas(
    ticker: str,
    period: str = Query(
        default="1y", description="Janela para comparacao com o indice: 6mo, 1y, 5y"
    ),
    db: Session = Depends(get_db),
) -> EstatisticasSchema:
    """
    Calcula volatilidade anualizada, retorno acumulado, drawdown maximo
    e correlacao com o Ibovespa, com base no historico salvo no banco.

    Estas metricas descrevem o COMPORTAMENTO PASSADO do ativo -- sao
    ferramentas de analise de risco, nao previsao de resultados futuros.
    """
    try:
        return _service.calcular(db, ticker, period)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc