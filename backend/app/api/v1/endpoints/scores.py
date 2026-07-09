from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scores import ScoreRiscoOportunidadeSchema
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/ativos", tags=["Scores"])
_service = ScoringService()


@router.get("/{ticker}/scores", response_model=ScoreRiscoOportunidadeSchema)
def obter_scores(ticker: str, db: Session = Depends(get_db)) -> ScoreRiscoOportunidadeSchema:
    """
    Calcula o Score de Risco (0-100, quanto maior mais arriscado) e o
    Score de Oportunidade (0-100, quanto maior mais atrativo), com base
    em indicadores tecnicos, estatisticas e fundamentos.

    Estes scores sao heuristicas de apoio a decisao -- nao constituem
    recomendacao de investimento nem garantia de resultado.
    """
    return _service.calcular(db, ticker)