from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha_plana: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return _pwd_context.hash(senha_plana)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Confere se a senha em texto puro corresponde ao hash armazenado."""
    return _pwd_context.verify(senha_plana, senha_hash)


def criar_access_token(subject: str) -> str:
    """
    Gera um JWT assinado. O `subject` (aqui, o email do usuario) fica no
    claim padrao "sub". O token expira em ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expira_em}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decodificar_token(token: str) -> str | None:
    """
    Decodifica e valida o JWT. Retorna o `subject` (email) se valido,
    ou None se o token for invalido/expirado.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None