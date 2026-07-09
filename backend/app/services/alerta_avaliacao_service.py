import logging

from sqlalchemy.orm import Session

from app import crud
from app.db.session import SessionLocal
from app.services.indicators_service import IndicatorsService
from app.services.market_data_service import normalizar_ticker
from app.services.sinal_service import SinalService

logger = logging.getLogger("alertas")


class AlertaAvaliacaoService:
    """
    Avalia se as condicoes de alertas ATIVOS foram atingidas, usando os
    dados mais recentes disponiveis (preco, RSI, sinal final).

    Cada tipo de alerta compara um valor atual contra o parametro
    configurado:
        preco_acima  -> preco_atual >= parametros["valor"]
        preco_abaixo -> preco_atual <= parametros["valor"]
        rsi_abaixo   -> rsi_14 <= parametros["valor"]
        rsi_acima    -> rsi_14 >= parametros["valor"]
        sinal_igual  -> sinal_final == parametros["sinal"]
    """

    def __init__(
        self,
        indicators_service: IndicatorsService | None = None,
        sinal_service: SinalService | None = None,
    ) -> None:
        self._indicators_service = indicators_service or IndicatorsService()
        self._sinal_service = sinal_service or SinalService()

    def avaliar_todos(self, db: Session) -> list[dict]:
        """
        Avalia TODOS os alertas ativos do sistema (todos os usuarios).
        Usado pelo job automatico em segundo plano.
        """
        alertas_ativos = crud.alerta.listar_todos_ativos(db)
        return self.avaliar_lista(db, alertas_ativos)

    def avaliar_lista(self, db: Session, alertas: list) -> list[dict]:
        """
        Avalia uma lista especifica de alertas e registra disparo para
        os que atingiram a condicao (respeitando a regra de nao
        duplicar disparo nao-lido). Retorna um resumo do processamento.
        """
        resumo = []

        for alerta in alertas:
            try:
                atingiu, valor_atual = self._avaliar_um(db, alerta)
            except ValueError as exc:
                logger.warning("Alerta %s (%s): %s", alerta.id, alerta.ticker, exc)
                resumo.append({"alerta_id": alerta.id, "status": "erro", "detalhe": str(exc)})
                continue

            if not atingiu:
                resumo.append({"alerta_id": alerta.id, "status": "nao_atingido"})
                continue

            if crud.alerta.ja_disparado_recentemente(db, alerta.id):
                resumo.append({"alerta_id": alerta.id, "status": "atingido_mas_ja_notificado"})
                continue

            crud.alerta.registrar_disparo(db, alerta.id, valor_atual)
            logger.info("Alerta %s disparado (%s = %s)", alerta.id, alerta.ticker, valor_atual)
            resumo.append({"alerta_id": alerta.id, "status": "disparado", "valor": valor_atual})

        return resumo

    def _avaliar_um(self, db: Session, alerta) -> tuple[bool, str]:
        ticker_normalizado = normalizar_ticker(alerta.ticker)

        if alerta.tipo in ("preco_acima", "preco_abaixo"):
            indicadores = self._indicators_service.calcular(db, ticker_normalizado)
            preco = indicadores.ultimo_fechamento
            valor_limite = float(alerta.parametros["valor"])

            if alerta.tipo == "preco_acima":
                return preco >= valor_limite, f"{preco:.2f}"
            return preco <= valor_limite, f"{preco:.2f}"

        if alerta.tipo in ("rsi_abaixo", "rsi_acima"):
            indicadores = self._indicators_service.calcular(db, ticker_normalizado)
            rsi = indicadores.rsi_14
            if rsi is None:
                raise ValueError("RSI indisponivel (historico insuficiente)")
            valor_limite = float(alerta.parametros["valor"])

            if alerta.tipo == "rsi_abaixo":
                return rsi <= valor_limite, f"{rsi:.2f}"
            return rsi >= valor_limite, f"{rsi:.2f}"

        if alerta.tipo == "sinal_igual":
            sinal = self._sinal_service.gerar(db, ticker_normalizado)
            sinal_esperado = alerta.parametros["sinal"]
            return sinal.sinal == sinal_esperado, sinal.sinal

        raise ValueError(f"Tipo de alerta desconhecido: {alerta.tipo}")


def avaliar_alertas_job() -> None:
    """
    Funcao de entrada usada pelo scheduler (APScheduler). Abre sua
    PROPRIA sessao de banco, ja que roda fora do ciclo de
    request/response do FastAPI.
    """
    db = SessionLocal()
    try:
        service = AlertaAvaliacaoService()
        resumo = service.avaliar_todos(db)
        disparados = [r for r in resumo if r["status"] == "disparado"]
        logger.info(
            "Verificacao de alertas concluida: %d avaliados, %d disparados",
            len(resumo),
            len(disparados),
        )
    finally:
        db.close()