from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import decodificar_token
from app.db.session import get_db
from app.models.usuario import Usuario

COOKIE_NAME = "access_token"

# auto_error=False: se nao vier header Authorization, nao explode
# sozinho, deixa a gente checar o cookie como alternativa.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False
)


def _extrair_token(
    request: Request, token_header: str | None = Depends(oauth2_scheme)
) -> str | None:
    """
    Prioriza o cookie httpOnly (fluxo do frontend web). Cai para o
    header Authorization: Bearer se o cookie nao existir (util para
    testes via Swagger/Postman/scripts).
    """
    token_cookie = request.cookies.get(COOKIE_NAME)
    return token_cookie or token_header


def get_usuario_atual(
    token: str | None = Depends(_extrair_token), db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency que protege rotas: exige um token valido (cookie ou
    Bearer) e retorna o Usuario correspondente. Lanca 401 se faltar,
    for invalido/expirado, ou o usuario nao existir mais.
    """
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credenciais_invalidas
    email = decodificar_token(token)
    if email is None:
        raise credenciais_invalidas
    usuario = crud.usuario.get_by_email(db, email)
    if usuario is None:
        raise credenciais_invalidas
    return usuario