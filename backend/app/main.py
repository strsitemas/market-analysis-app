from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.services.alerta_avaliacao_service import avaliar_alertas_job

configure_logging()

INTERVALO_VERIFICACAO_ALERTAS_MINUTOS = 15
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        avaliar_alertas_job,
        trigger="interval",
        minutes=INTERVALO_VERIFICACAO_ALERTAS_MINUTOS,
        id="verificar_alertas",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "API de analise de ativos financeiros. "
            "Fornece dados tecnicos, fundamentalistas e estatisticos "
            "para apoio a decisao. NAO garante previsao de mercado."
        ),
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()


@app.get("/", tags=["Root"])
def root() -> dict:
    return {
        "message": "Market Analysis API no ar.",
        "docs": "/docs",
    }