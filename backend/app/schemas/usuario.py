from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=8, description="Minimo 8 caracteres")


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    ativo: bool
    criado_em: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"