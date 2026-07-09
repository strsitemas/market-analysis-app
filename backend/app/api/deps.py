from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import decodificar_token
from app.db.session import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency que protege rotas: exige um Bearer token valido no
    header Authorization e retorna o Usuario correspondente. Lanca 401
    se o token faltar, for invalido/expirado, ou o usuario nao existir
    mais.
    """
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decodificar_token(token)
    if email is None:
        raise credenciais_invalidas

    usuario = crud.usuario.get_by_email(db, email)
    if usuario is None:
        raise credenciais_invalidas
    return usuario