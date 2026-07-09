from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.schemas.ativo import AtivoCreate, AtivoRead
from app.schemas.cotacao_historica import CotacaoHistoricaRead
from app.services.market_data_service import normalizar_ticker
from app.services.sync_service import SyncService

router = APIRouter(prefix="/ativos", tags=["Ativos"])
_sync_service = SyncService()


@router.post("", response_model=AtivoRead, status_code=201)
def cadastrar_ativo(ativo_in: AtivoCreate, db: Session = Depends(get_db)) -> AtivoRead:
    """Cadastra um ativo para monitoramento. Retorna 409 se o ticker ja existir."""
    ticker_normalizado = normalizar_ticker(ativo_in.ticker)
    existente = crud.ativo.get_by_ticker(db, ticker_normalizado)
    if existente:
        raise HTTPException(
            status_code=409, detail=f"Ativo '{ticker_normalizado}' ja cadastrado"
        )
    ativo_in.ticker = ticker_normalizado
    return crud.ativo.criar(db, ativo_in)


@router.get("", response_model=list[AtivoRead])
def listar_ativos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[AtivoRead]:
    """Lista todos os ativos cadastrados no sistema."""
    return crud.ativo.listar(db, skip=skip, limit=limit)


@router.get("/{ticker}", response_model=AtivoRead)
def obter_ativo(ticker: str, db: Session = Depends(get_db)) -> AtivoRead:
    ativo = crud.ativo.get_by_ticker(db, normalizar_ticker(ticker))
    if ativo is None:
        raise HTTPException(status_code=404, detail=f"Ativo '{ticker}' nao encontrado")
    return ativo


@router.post("/{ticker}/sincronizar")
def sincronizar_ativo(
    ticker: str,
    period: str = Query(default="1y", description="Janela: 1mo, 3mo, 6mo, 1y, 5y, max"),
    interval: str = Query(default="1d", description="Granularidade: 1d, 1wk, 1mo"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Busca o historico no Yahoo Finance e salva/atualiza no banco de dados.
    Cadastra o ativo automaticamente se ele ainda nao existir.
    """
    try:
        return _sync_service.sincronizar_historico(db, ticker, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{ticker}/historico-salvo", response_model=list[CotacaoHistoricaRead])
def obter_historico_salvo(
    ticker: str, db: Session = Depends(get_db)
) -> list[CotacaoHistoricaRead]:
    """Retorna o historico ja salvo no Postgres (rapido, sem chamar o Yahoo)."""
    ativo = crud.ativo.get_by_ticker(db, normalizar_ticker(ticker))
    if ativo is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ativo '{ticker}' nao encontrado. Cadastre e sincronize primeiro.",
        )
    return crud.cotacao_historica.listar_por_ativo(db, ativo.id)