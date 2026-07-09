from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_usuario_atual
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.monitoramento import AlertaCreate, AlertaDisparoRead, AlertaRead
from app.services.alerta_avaliacao_service import AlertaAvaliacaoService
from app.services.market_data_service import normalizar_ticker

router = APIRouter(prefix="/alertas", tags=["Alertas"])
_avaliacao_service = AlertaAvaliacaoService()

TIPOS_VALIDOS = {"preco_acima", "preco_abaixo", "rsi_abaixo", "rsi_acima", "sinal_igual"}
PARAMETRO_OBRIGATORIO = {
    "preco_acima": "valor",
    "preco_abaixo": "valor",
    "rsi_abaixo": "valor",
    "rsi_acima": "valor",
    "sinal_igual": "sinal",
}


def _validar_parametros(tipo: str, parametros: dict) -> None:
    chave_esperada = PARAMETRO_OBRIGATORIO[tipo]
    if chave_esperada not in parametros:
        raise HTTPException(
            status_code=422,
            detail=f"Alertas do tipo '{tipo}' exigem o parametro '{chave_esperada}'",
        )


@router.get("", response_model=list[AlertaRead])
def listar_alertas(
    apenas_ativos: bool = False,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> list[AlertaRead]:
    """Lista os alertas do usuario autenticado."""
    return crud.alerta.listar(db, usuario_atual.id, apenas_ativos=apenas_ativos)


@router.post("", response_model=AlertaRead, status_code=201)
def criar_alerta(
    alerta_in: AlertaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> AlertaRead:
    """Cria um novo alerta de monitoramento para o usuario autenticado."""
    _validar_parametros(alerta_in.tipo, alerta_in.parametros)
    ticker_normalizado = normalizar_ticker(alerta_in.ticker)
    return crud.alerta.criar(
        db, usuario_atual.id, ticker_normalizado, alerta_in.tipo, alerta_in.parametros
    )

@router.patch("/{alerta_id}/ativar", response_model=AlertaRead)
def ativar_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> AlertaRead:
    """Reativa um alerta pausado do usuario autenticado."""
    alerta = crud.alerta.alternar_ativo(db, usuario_atual.id, alerta_id, ativo=True)
    if alerta is None:
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")
    return alerta


@router.patch("/{alerta_id}/pausar", response_model=AlertaRead)
def pausar_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> AlertaRead:
    """Pausa um alerta do usuario autenticado."""
    alerta = crud.alerta.alternar_ativo(db, usuario_atual.id, alerta_id, ativo=False)
    if alerta is None:
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")
    return alerta


@router.delete("/{alerta_id}", status_code=204)
def remover_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> None:
    """Remove um alerta do usuario autenticado."""
    removido = crud.alerta.remover(db, usuario_atual.id, alerta_id)
    if not removido:
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")


@router.get("/disparos", response_model=list[AlertaDisparoRead])
def listar_disparos(
    apenas_nao_lidos: bool = False,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> list[AlertaDisparoRead]:
    """Lista o historico de disparos dos alertas do usuario autenticado."""
    return crud.alerta.listar_disparos(
        db, usuario_atual.id, apenas_nao_lidos=apenas_nao_lidos
    )


@router.patch("/disparos/{disparo_id}/marcar-lido", response_model=AlertaDisparoRead)
def marcar_disparo_como_lido(
    disparo_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> AlertaDisparoRead:
    """Marca um disparo do usuario autenticado como lido."""
    disparo = crud.alerta.marcar_como_lido(db, usuario_atual.id, disparo_id)
    if disparo is None:
        raise HTTPException(status_code=404, detail="Disparo nao encontrado")
    return disparo


@router.post("/verificar-agora")
def verificar_agora(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> dict:
    """
    Forca uma verificacao IMEDIATA dos alertas ATIVOS do usuario
    autenticado, sem esperar o proximo ciclo automatico (15 min).
    """
    alertas_usuario = crud.alerta.listar(db, usuario_atual.id, apenas_ativos=True)
    resumo = _avaliacao_service.avaliar_lista(db, alertas_usuario)
    disparados = [r for r in resumo if r["status"] == "disparado"]
    return {"avaliados": len(resumo), "disparados": len(disparados), "detalhes": resumo}
