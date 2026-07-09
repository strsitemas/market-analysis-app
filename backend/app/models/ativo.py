from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ativo(Base):
    """
    Representa um ativo financeiro monitorado pelo sistema
    (ex: PETR4.SA, AAPL, VALE3.SA).
    """

    __tablename__ = "ativos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    setor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    moeda: Mapped[str] = mapped_column(String(10), default="BRL")

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    cotacoes_historicas: Mapped[list["CotacaoHistorica"]] = relationship(
        back_populates="ativo", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ativo ticker={self.ticker}>"