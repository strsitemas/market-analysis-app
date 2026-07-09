from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoramento import Alerta, AlertaDisparo


def listar(db: Session, usuario_id: int, apenas_ativos: bool = False) -> list[Alerta]:
    stmt = (
        select(Alerta)
        .where(Alerta.usuario_id == usuario_id)
        .order_by(Alerta.criado_em.desc())
    )
    if apenas_ativos:
        stmt = stmt.where(Alerta.ativo == True)  # noqa: E712
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, usuario_id: int, alerta_id: int) -> Alerta | None:
    stmt = select(Alerta).where(Alerta.id == alerta_id, Alerta.usuario_id == usuario_id)
    return db.scalar(stmt)


def criar(db: Session, usuario_id: int, ticker: str, tipo: str, parametros: dict) -> Alerta:
    alerta = Alerta(usuario_id=usuario_id, ticker=ticker, tipo=tipo, parametros=parametros)
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def remover(db: Session, usuario_id: int, alerta_id: int) -> bool:
    alerta = get_by_id(db, usuario_id, alerta_id)
    if alerta is None:
        return False
    db.delete(alerta)
    db.commit()
    return True


def alternar_ativo(db: Session, usuario_id: int, alerta_id: int, ativo: bool) -> Alerta | None:
    alerta = get_by_id(db, usuario_id, alerta_id)
    if alerta is None:
        return None
    alerta.ativo = ativo
    db.commit()
    db.refresh(alerta)
    return alerta

def registrar_disparo(db: Session, alerta_id: int, valor_no_momento: str) -> AlertaDisparo:
    disparo = AlertaDisparo(alerta_id=alerta_id, valor_no_momento=valor_no_momento)
    db.add(disparo)
    db.commit()
    db.refresh(disparo)
    return disparo


def ja_disparado_recentemente(db: Session, alerta_id: int) -> bool:
    stmt = select(AlertaDisparo).where(
        AlertaDisparo.alerta_id == alerta_id, AlertaDisparo.lido == False  # noqa: E712
    )
    return db.scalar(stmt) is not None


def listar_disparos(
    db: Session, usuario_id: int, apenas_nao_lidos: bool = False
) -> list[AlertaDisparo]:
    stmt = (
        select(AlertaDisparo)
        .join(Alerta, AlertaDisparo.alerta_id == Alerta.id)
        .where(Alerta.usuario_id == usuario_id)
        .order_by(AlertaDisparo.disparado_em.desc())
    )
    if apenas_nao_lidos:
        stmt = stmt.where(AlertaDisparo.lido == False)  # noqa: E712
    return list(db.scalars(stmt).all())


def marcar_como_lido(db: Session, usuario_id: int, disparo_id: int) -> AlertaDisparo | None:
    stmt = (
        select(AlertaDisparo)
        .join(Alerta, AlertaDisparo.alerta_id == Alerta.id)
        .where(AlertaDisparo.id == disparo_id, Alerta.usuario_id == usuario_id)
    )
    disparo = db.scalar(stmt)
    if disparo is None:
        return None
    disparo.lido = True
    db.commit()
    db.refresh(disparo)
    return disparo


def listar_todos_ativos(db: Session) -> list[Alerta]:
    """
    Lista TODOS os alertas ativos do sistema, de qualquer usuario.
    Usado exclusivamente pelo job automatico em segundo plano.
    """
    stmt = select(Alerta).where(Alerta.ativo == True)  # noqa: E712
    return list(db.scalars(stmt).all())
