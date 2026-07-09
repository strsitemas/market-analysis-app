from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.alerta_avaliacao_service import avaliar_alertas_job

configure_logging()

INTERVALO_VERIFICACAO_ALERTAS_MINUTOS = 15

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa na SUBIDA da aplicacao: agenda a verificacao periodica de
    # alertas e inicia o scheduler em background (thread separada, nao
    # bloqueia o event loop do FastAPI).
    scheduler.add_job(
        avaliar_alertas_job,
        trigger="interval",
        minutes=INTERVALO_VERIFICACAO_ALERTAS_MINUTOS,
        id="verificar_alertas",
        replace_existing=True,
    )
    scheduler.start()

    yield  # a aplicacao roda aqui

    # Executa no DESLIGAMENTO da aplicacao: para o scheduler de forma limpa
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