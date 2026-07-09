from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_senha, verificar_senha
from app.models.usuario import Usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def criar(db: Session, email: str, senha: str) -> Usuario:
    usuario = Usuario(email=email, senha_hash=hash_senha(senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario | None:
    """Retorna o usuario se email+senha forem validos, senao None."""
    usuario = get_by_email(db, email)
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        return None
    return usuario