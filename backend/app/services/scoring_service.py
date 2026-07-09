from sqlalchemy.orm import Session

from app.schemas.scores import ScoreRiscoOportunidadeSchema
from app.services.fundamentals_service import FundamentalsService
from app.services.indicators_service import IndicatorsService
from app.services.market_data_service import normalizar_ticker
from app.services.statistics_service import StatisticsService


def _clamp(valor: float, minimo: float = 0.0, maximo: float = 100.0) -> float:
    """Restringe um valor ao intervalo [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


class ScoringService:
    """
    Calcula o Score de Risco e o Score de Oportunidade de um ativo,
    combinando indicadores tecnicos, estatisticas e fundamentos ja
    calculados pelos services anteriores.

    IMPORTANTE: estes scores sao heuristicas de apoio a decisao,
    baseadas em pesos definidos por regras de bom senso de mercado.
    NAO sao uma formula cientifica nem garantia de resultado.
    """

    PESO_VOLATILIDADE = 35
    PESO_DRAWDOWN = 30
    PESO_DIVIDA = 20
    PESO_CORRELACAO = 15

    PESO_TENDENCIA = 20
    PESO_RSI = 20
    PESO_MACD = 15
    PESO_BOLLINGER = 15
    PESO_PL = 15
    PESO_DIVIDEND_YIELD = 15

    def __init__(
        self,
        indicators_service: IndicatorsService | None = None,
        statistics_service: StatisticsService | None = None,
        fundamentals_service: FundamentalsService | None = None,
    ) -> None:
        self._indicators_service = indicators_service or IndicatorsService()
        self._statistics_service = statistics_service or StatisticsService()
        self._fundamentals_service = fundamentals_service or FundamentalsService()

    def calcular(self, db: Session, ticker: str) -> ScoreRiscoOportunidadeSchema:
        ticker_normalizado = normalizar_ticker(ticker)

        indicadores = self._indicators_service.calcular(db, ticker_normalizado)
        estatisticas = self._statistics_service.calcular(db, ticker_normalizado)

        try:
            fundamentos = self._fundamentals_service.obter(ticker_normalizado)
        except ValueError:
            fundamentos = None

        score_risco, detalhes_risco = self._calcular_risco(estatisticas, fundamentos)
        score_oportunidade, detalhes_oportunidade = self._calcular_oportunidade(
            indicadores, fundamentos
        )

        return ScoreRiscoOportunidadeSchema(
            ticker=ticker_normalizado,
            score_risco=round(score_risco, 1),
            score_oportunidade=round(score_oportunidade, 1),
            detalhes_risco=detalhes_risco,
            detalhes_oportunidade=detalhes_oportunidade,
        )

    def _calcular_risco(self, estatisticas, fundamentos) -> tuple[float, dict]:
        risco_volatilidade = _clamp(estatisticas.volatilidade_anualizada_pct / 60 * 100)
        risco_drawdown = _clamp(abs(estatisticas.drawdown_maximo_pct) / 60 * 100)

        if fundamentos and fundamentos.divida_patrimonio is not None:
            risco_divida = _clamp(fundamentos.divida_patrimonio / 200 * 100)
        else:
            risco_divida = 50.0

        correlacao = estatisticas.correlacao_ibovespa
        risco_correlacao = abs(correlacao) * 100 if correlacao is not None else 50.0

        score_risco = (
            risco_volatilidade * self.PESO_VOLATILIDADE
            + risco_drawdown * self.PESO_DRAWDOWN
            + risco_divida * self.PESO_DIVIDA
            + risco_correlacao * self.PESO_CORRELACAO
        ) / 100

        detalhes = {
            "risco_volatilidade": round(risco_volatilidade, 1),
            "risco_drawdown": round(risco_drawdown, 1),
            "risco_divida": round(risco_divida, 1),
            "risco_correlacao": round(risco_correlacao, 1),
        }
        return score_risco, detalhes

    def _calcular_oportunidade(self, indicadores, fundamentos) -> tuple[float, dict]:
        mapa_tendencia = {"alta": 100.0, "lateral": 50.0, "baixa": 0.0}
        oportunidade_tendencia = mapa_tendencia.get(indicadores.tendencia, 50.0)

        rsi = indicadores.rsi_14
        oportunidade_rsi = _clamp(100 - rsi) if rsi is not None else 50.0

        histograma = indicadores.macd.histograma
        oportunidade_macd = 100.0 if (histograma and histograma > 0) else 0.0

        preco = indicadores.ultimo_fechamento
        b_inf = indicadores.bollinger.banda_inferior
        b_sup = indicadores.bollinger.banda_superior
        if b_inf is not None and b_sup is not None and b_sup != b_inf:
            posicao_pct = (preco - b_inf) / (b_sup - b_inf) * 100
            oportunidade_bollinger = _clamp(100 - posicao_pct)
        else:
            oportunidade_bollinger = 50.0

        if fundamentos and fundamentos.pl is not None and fundamentos.pl > 0:
            oportunidade_pl = _clamp(100 - ((fundamentos.pl - 5) / 30 * 100))
        else:
            oportunidade_pl = 50.0

        if fundamentos and fundamentos.dividend_yield_pct is not None:
            oportunidade_dy = _clamp(fundamentos.dividend_yield_pct / 12 * 100)
        else:
            oportunidade_dy = 50.0

        score_oportunidade = (
            oportunidade_tendencia * self.PESO_TENDENCIA
            + oportunidade_rsi * self.PESO_RSI
            + oportunidade_macd * self.PESO_MACD
            + oportunidade_bollinger * self.PESO_BOLLINGER
            + oportunidade_pl * self.PESO_PL
            + oportunidade_dy * self.PESO_DIVIDEND_YIELD
        ) / 100

        detalhes = {
            "oportunidade_tendencia": round(oportunidade_tendencia, 1),
            "oportunidade_rsi": round(oportunidade_rsi, 1),
            "oportunidade_macd": round(oportunidade_macd, 1),
            "oportunidade_bollinger": round(oportunidade_bollinger, 1),
            "oportunidade_pl": round(oportunidade_pl, 1),
            "oportunidade_dividend_yield": round(oportunidade_dy, 1),
        }
        return score_oportunidade, detalhes