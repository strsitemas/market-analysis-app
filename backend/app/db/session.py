from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency do FastAPI para injetar uma sessao de banco de dados
    em qualquer endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()