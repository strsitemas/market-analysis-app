from sqlalchemy.orm import Session

from app.schemas.sinal import SinalFinalSchema
from app.services.indicators_service import IndicatorsService
from app.services.market_data_service import normalizar_ticker
from app.services.scoring_service import ScoringService

LIMITE_RISCO_ALTO = 75
LIMITE_RISCO_CONTROLADO = 50
LIMITE_OPORTUNIDADE_ALTA = 70
LIMITE_OPORTUNIDADE_BAIXA = 30


class SinalService:
    """
    Gera o sinal final de analise (compra, venda, atencao, neutro ou
    indeterminado), combinando o Score de Risco, o Score de
    Oportunidade e a tendencia tecnica do ativo.

    AVISO CRITICO: este sinal e uma ferramenta de APOIO A DECISAO,
    baseada em regras estatisticas sobre dados historicos. NAO e uma
    recomendacao de compra/venda, nem promessa de resultado futuro.
    Decisoes de investimento devem considerar contexto mais amplo e,
    se necessario, orientacao de um profissional habilitado.
    """

    def __init__(
        self,
        scoring_service: ScoringService | None = None,
        indicators_service: IndicatorsService | None = None,
    ) -> None:
        self._scoring_service = scoring_service or ScoringService()
        self._indicators_service = indicators_service or IndicatorsService()

    def gerar(self, db: Session, ticker: str) -> SinalFinalSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        scores = self._scoring_service.calcular(db, ticker_normalizado)
        indicadores = self._indicators_service.calcular(db, ticker_normalizado)

        sinal, justificativa = self._decidir(
            scores.score_risco, scores.score_oportunidade, indicadores.tendencia
        )

        return SinalFinalSchema(
            ticker=ticker_normalizado,
            sinal=sinal,
            justificativa=justificativa,
            score_risco=scores.score_risco,
            score_oportunidade=scores.score_oportunidade,
            tendencia=indicadores.tendencia,
        )

    @staticmethod
    def _decidir(
        score_risco: float,
        score_oportunidade: float,
        tendencia: str,
    ) -> tuple[str, str]:
        """
        Regras, em ordem de prioridade:

        1. Risco alto (>=75) sempre vira "atencao", independente do
           resto -- protecao nunca e sobrescrita por oportunidade.
        2. "Compra" exige TRES condicoes simultaneas: oportunidade
           alta, risco controlado E tendencia de alta. A exigencia de
           tendencia de alta e nova aqui -- antes bastava risco e
           oportunidade, o que permitia sinalizar "compra" mesmo com o
           ativo em queda tecnica, algo inconsistente com analise
           tecnica (comprar contra a tendencia e mais arriscado).
        3. "Venda" exige oportunidade baixa combinada com tendencia de
           baixa (inalterado).
        4. Validacoes defensivas: score fora de 0-100 e erro de dado
           (nao deveria acontecer, mas falha alto e claro em vez de
           gerar sinal incorreto silenciosamente). Tendencia fora de
           alta/baixa/lateral vira "indeterminado" em vez de cair
           silenciosamente em "neutro" por omissao -- deixa explicito
           que o dado de entrada estava incompleto.
        """
        if not 0 <= score_risco <= 100:
            raise ValueError("Score de risco deve estar entre 0 e 100.")
        if not 0 <= score_oportunidade <= 100:
            raise ValueError("Score de oportunidade deve estar entre 0 e 100.")

        tendencia_normalizada = tendencia.strip().lower()
        if tendencia_normalizada not in {"alta", "baixa", "lateral"}:
            return (
                "indeterminado",
                f"Tendencia tecnica invalida ou insuficiente: {tendencia}.",
            )

        if score_risco >= LIMITE_RISCO_ALTO:
            return (
                "atencao",
                f"Risco elevado (score {score_risco}), independente da "
                "oportunidade identificada. Recomenda-se cautela adicional.",
            )
        if (
            score_oportunidade >= LIMITE_OPORTUNIDADE_ALTA
            and score_risco <= LIMITE_RISCO_CONTROLADO
            and tendencia_normalizada == "alta"
        ):
            return (
                "compra",
                f"Oportunidade alta (score {score_oportunidade}) com risco "
                f"controlado (score {score_risco}) e tendencia tecnica de "
                "alta.",
            )
        if score_oportunidade <= LIMITE_OPORTUNIDADE_BAIXA and tendencia_normalizada == "baixa":
            return (
                "venda",
                f"Oportunidade baixa (score {score_oportunidade}) combinada "
                "com tendencia tecnica de baixa.",
            )
        return (
            "neutro",
            f"Sinais mistos (risco {score_risco}, oportunidade "
            f"{score_oportunidade}, tendencia {tendencia_normalizada}) -- "
            "sem conviccao suficiente para compra ou venda.",
        )