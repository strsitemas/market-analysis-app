from pydantic import BaseModel


class SinalFinalSchema(BaseModel):
    ticker: str
    sinal: str
    justificativa: str
    score_risco: float
    score_oportunidade: float
    tendencia: str