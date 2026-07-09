from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_usuario_atual
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.monitoramento import FavoritoCreate, FavoritoRead
from app.services.market_data_service import normalizar_ticker

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])


@router.get("", response_model=list[FavoritoRead])
def listar_favoritos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> list[FavoritoRead]:
    """Lista os favoritos do usuario autenticado."""
    return crud.favorito.listar(db, usuario_atual.id)


@router.post("", response_model=FavoritoRead, status_code=201)
def adicionar_favorito(
    favorito_in: FavoritoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> FavoritoRead:
    """Marca um ativo como favorito do usuario autenticado."""
    ticker_normalizado = normalizar_ticker(favorito_in.ticker)
    existente = crud.favorito.get_by_ticker(db, usuario_atual.id, ticker_normalizado)
    if existente:
        raise HTTPException(
            status_code=409, detail=f"'{ticker_normalizado}' ja esta nos favoritos"
        )
    return crud.favorito.criar(db, usuario_atual.id, ticker_normalizado)


@router.delete("/{ticker}", status_code=204)
def remover_favorito(
    ticker: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> None:
    """Remove um ativo dos favoritos do usuario autenticado."""
    ticker_normalizado = normalizar_ticker(ticker)
    removido = crud.favorito.remover_por_ticker(db, usuario_atual.id, ticker_normalizado)
    if not removido:
        raise HTTPException(
            status_code=404, detail=f"'{ticker_normalizado}' nao esta nos favoritos"
        )