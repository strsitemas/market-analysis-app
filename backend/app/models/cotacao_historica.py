from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CotacaoHistorica(Base):
    """
    Representa um ponto historico (candle diario) de precos de um ativo:
    abertura, maxima, minima, fechamento e volume (OHLCV).
    """

    __tablename__ = "cotacoes_historicas"
    __table_args__ = (
        UniqueConstraint("ativo_id", "data", name="uq_ativo_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ativo_id: Mapped[int] = mapped_column(ForeignKey("ativos.id"), index=True)
    data: Mapped[date] = mapped_column(Date, index=True)

    abertura: Mapped[float] = mapped_column(Numeric(18, 4))
    maxima: Mapped[float] = mapped_column(Numeric(18, 4))
    minima: Mapped[float] = mapped_column(Numeric(18, 4))
    fechamento: Mapped[float] = mapped_column(Numeric(18, 4))
    volume: Mapped[int] = mapped_column()

    ativo: Mapped["Ativo"] = relationship(back_populates="cotacoes_historicas")

    def __repr__(self) -> str:
        return f"<CotacaoHistorica ativo_id={self.ativo_id} data={self.data}>"