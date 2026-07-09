from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoramento import Favorito


def listar(db: Session, usuario_id: int) -> list[Favorito]:
    stmt = (
        select(Favorito)
        .where(Favorito.usuario_id == usuario_id)
        .order_by(Favorito.criado_em.desc())
    )
    return list(db.scalars(stmt).all())


def get_by_ticker(db: Session, usuario_id: int, ticker: str) -> Favorito | None:
    stmt = select(Favorito).where(
        Favorito.usuario_id == usuario_id, Favorito.ticker == ticker
    )
    return db.scalar(stmt)


def criar(db: Session, usuario_id: int, ticker: str) -> Favorito:
    favorito = Favorito(usuario_id=usuario_id, ticker=ticker)
    db.add(favorito)
    db.commit()
    db.refresh(favorito)
    return favorito


def remover_por_ticker(db: Session, usuario_id: int, ticker: str) -> bool:
    favorito = get_by_ticker(db, usuario_id, ticker)
    if favorito is None:
        return False
    db.delete(favorito)
    db.commit()
    return True