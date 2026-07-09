from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Favorito(Base):
    """
    Ativo marcado como favorito por um usuario especifico.
    """

    __tablename__ = "favoritos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "ticker", name="uq_favorito_usuario_ticker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Favorito usuario_id={self.usuario_id} ticker={self.ticker}>"

class Alerta(Base):
    """
    Regra de monitoramento de um ativo, pertencente a um usuario.

    Tipos suportados:
        preco_acima  -> parametros: {"valor": float}
        preco_abaixo -> parametros: {"valor": float}
        rsi_abaixo   -> parametros: {"valor": float}
        rsi_acima    -> parametros: {"valor": float}
        sinal_igual  -> parametros: {"sinal": "compra" | "venda" | "atencao"}
    """

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    parametros: Mapped[dict] = mapped_column("parametros_json", JSONB, nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    disparos: Mapped[list["AlertaDisparo"]] = relationship(
        back_populates="alerta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Alerta id={self.id} usuario_id={self.usuario_id} ticker={self.ticker}>"


class AlertaDisparo(Base):
    """Registro de UM disparo de um alerta."""

    __tablename__ = "alertas_disparos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alerta_id: Mapped[int] = mapped_column(ForeignKey("alertas.id"), index=True)
    disparado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    valor_no_momento: Mapped[str] = mapped_column(String(100))
    lido: Mapped[bool] = mapped_column(default=False)

    alerta: Mapped["Alerta"] = relationship(back_populates="disparos")

    def __repr__(self) -> str:
        return f"<AlertaDisparo alerta_id={self.alerta_id} em={self.disparado_em}>"
