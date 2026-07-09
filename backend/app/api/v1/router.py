from fastapi import APIRouter

from app.api.v1.endpoints import (
    alertas,
    analise,
    ativos,
    auth,
    backtest,
    estatisticas,
    favoritos,
    fundamentos,
    health,
    indicadores,
    market_data,
    scores,
    sinal,
    tabela_tecnica,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(market_data.router)

# analise.router precisa vir ANTES de ativos.router: ele contem a rota
# estatica "/ativos/disponiveis", que seria "engolida" pela rota dinamica
# "/ativos/{ticker}" do ativos.router se viesse depois (o FastAPI resolve
# rotas na ordem em que sao registradas).
api_router.include_router(analise.router)
api_router.include_router(ativos.router)

api_router.include_router(indicadores.router)
api_router.include_router(tabela_tecnica.router)
api_router.include_router(estatisticas.router)
api_router.include_router(fundamentos.router)
api_router.include_router(scores.router)
api_router.include_router(backtest.router)
api_router.include_router(sinal.router)

api_router.include_router(favoritos.router)
api_router.include_router(alertas.router)