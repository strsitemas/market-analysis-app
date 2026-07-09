from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ativo import Ativo
from app.schemas.ativo import AtivoCreate


def get_by_ticker(db: Session, ticker: str) -> Ativo | None:
    """Busca um ativo pelo ticker exato (ex: PETR4.SA)."""
    stmt = select(Ativo).where(Ativo.ticker == ticker)
    return db.scalar(stmt)


def get_by_id(db: Session, ativo_id: int) -> Ativo | None:
    return db.get(Ativo, ativo_id)


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Ativo]:
    stmt = select(Ativo).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def criar(db: Session, ativo_in: AtivoCreate) -> Ativo:
    ativo = Ativo(
        ticker=ativo_in.ticker,
        nome=ativo_in.nome,
        setor=ativo_in.setor,
        moeda=ativo_in.moeda,
    )
    db.add(ativo)
    db.commit()
    db.refresh(ativo)
    return ativo


def obter_ou_criar(db: Session, ticker: str) -> Ativo:
    """
    Busca o ativo; se nao existir, cadastra automaticamente.
    Usado pela sincronizacao, para nao exigir cadastro manual antes.
    """
    ativo = get_by_ticker(db, ticker)
    if ativo is None:
        ativo = criar(db, AtivoCreate(ticker=ticker))
    return ativo