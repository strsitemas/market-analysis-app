from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AtivoBase(BaseModel):
    ticker: str = Field(..., description="Codigo do ativo, ex: PETR4.SA, AAPL")
    nome: str | None = None
    setor: str | None = None
    moeda: str = "BRL"


class AtivoCreate(AtivoBase):
    """Schema usado para CADASTRAR um novo ativo via API."""
    pass


class AtivoRead(AtivoBase):
    """Schema usado para RETORNAR um ativo (inclui campos gerados pelo banco)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime