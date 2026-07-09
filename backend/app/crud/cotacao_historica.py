from datetime import date

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cotacao_historica import CotacaoHistorica


def listar_por_ativo(
    db: Session,
    ativo_id: int,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[CotacaoHistorica]:
    stmt = select(CotacaoHistorica).where(CotacaoHistorica.ativo_id == ativo_id)
    if data_inicio:
        stmt = stmt.where(CotacaoHistorica.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(CotacaoHistorica.data <= data_fim)
    stmt = stmt.order_by(CotacaoHistorica.data.asc())
    return list(db.scalars(stmt).all())


def upsert_lote(db: Session, ativo_id: int, pontos: list[dict]) -> int:
    """
    Insere ou ATUALIZA um lote de cotacoes (UPSERT).

    Se voce sincronizar o mesmo ativo duas vezes com periodos que se
    sobrepoem, o banco recusaria a segunda insercao por causa da
    constraint unica uq_ativo_data (ativo_id + data). O upsert resolve
    isso: se o candle daquele dia ja existe, so ATUALIZA os valores;
    se nao existe, INSERE.
    """
    if not pontos:
        return 0

    valores = [{**ponto, "ativo_id": ativo_id} for ponto in pontos]

    stmt = insert(CotacaoHistorica).values(valores)
    stmt = stmt.on_conflict_do_update(
        index_elements=["ativo_id", "data"],
        set_={
            "abertura": stmt.excluded.abertura,
            "maxima": stmt.excluded.maxima,
            "minima": stmt.excluded.minima,
            "fechamento": stmt.excluded.fechamento,
            "volume": stmt.excluded.volume,
        },
    )
    db.execute(stmt)
    db.commit()
    return len(valores)