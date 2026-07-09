from pydantic import BaseModel


class ScoreRiscoOportunidadeSchema(BaseModel):
    ticker: str
    score_risco: float
    score_oportunidade: float
    detalhes_risco: dict
    detalhes_oportunidade: dict