from datetime import date
from pydantic import BaseModel, ConfigDict


class CotacaoHistoricaBase(BaseModel):
    data: date
    abertura: float
    maxima: float
    minima: float
    fechamento: float
    volume: int


class CotacaoHistoricaCreate(CotacaoHistoricaBase):
    ativo_id: int


class CotacaoHistoricaRead(CotacaoHistoricaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo_id: int