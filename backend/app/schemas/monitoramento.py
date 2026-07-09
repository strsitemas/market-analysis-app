from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoAlerta = Literal["preco_acima", "preco_abaixo", "rsi_abaixo", "rsi_acima", "sinal_igual"]


class FavoritoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    criado_em: datetime


class FavoritoCreate(BaseModel):
    ticker: str = Field(..., description="Codigo do ativo, ex: PETR4, PETR4.SA")


class AlertaCreate(BaseModel):
    ticker: str = Field(..., description="Codigo do ativo, ex: PETR4, PETR4.SA")
    tipo: TipoAlerta = Field(
        ...,
        description=(
            "preco_acima/preco_abaixo esperam {'valor': float}; "
            "rsi_abaixo/rsi_acima esperam {'valor': float} (0-100); "
            "sinal_igual espera {'sinal': 'compra'|'venda'|'atencao'|'neutro'}"
        ),
    )
    parametros: dict = Field(..., description="Ver descricao do campo 'tipo'.")


class AlertaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    tipo: str
    parametros: dict
    ativo: bool
    criado_em: datetime


class AlertaDisparoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alerta_id: int
    disparado_em: datetime
    valor_no_momento: str
    lido: bool