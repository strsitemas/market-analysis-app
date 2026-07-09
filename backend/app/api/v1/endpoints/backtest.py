from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.backtest import BacktestResultSchema
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/ativos", tags=["Backtest"])
_service = BacktestService()


@router.get("/{ticker}/backtest", response_model=BacktestResultSchema)
def executar_backtest(
    ticker: str,
    periodo_curto: int = Query(default=20, description="Periodo da media movel curta"),
    periodo_longo: int = Query(default=50, description="Periodo da media movel longa"),
    db: Session = Depends(get_db),
) -> BacktestResultSchema:
    """
    Executa um backtest de cruzamento de medias moveis sobre o
    historico salvo no banco.

    AVISO: desempenho passado de uma estrategia, mesmo em backtest,
    NAO garante resultado futuro. Serve como ferramenta exploratoria.
    """
    try:
        return _service.executar(db, ticker, periodo_curto, periodo_longo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc