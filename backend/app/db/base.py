from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe base para todos os modelos ORM (SQLAlchemy) da aplicacao.
    Todo model deve herdar desta classe para ser reconhecido pelo
    Alembic na geracao automatica de migrations.
    """

    pass
from app.models.monitoramento import Favorito, Alerta, AlertaDisparo  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401