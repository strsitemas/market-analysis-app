from sqlalchemy.orm import Session

from app.schemas.analise import AnaliseCompletaSchema, AnaliseMultiplaSchema
from app.services.fundamentals_service import FundamentalsService
from app.services.market_data_service import normalizar_ticker
from app.services.scoring_service import ScoringService
from app.services.sinal_service import SinalService
from app.services.statistics_service import StatisticsService
from app.services.tabela_tecnica_service import TabelaTecnicaService


class AnaliseService:
    """
    Orquestra todos os services anteriores para montar a linha final
    de analise de um ativo (ou de varios, em lote).
    """

    def __init__(
        self,
        tabela_tecnica_service: TabelaTecnicaService | None = None,
        statistics_service: StatisticsService | None = None,
        fundamentals_service: FundamentalsService | None = None,
        scoring_service: ScoringService | None = None,
        sinal_service: SinalService | None = None,
    ) -> None:
        self._tabela_tecnica_service = tabela_tecnica_service or TabelaTecnicaService()
        self._statistics_service = statistics_service or StatisticsService()
        self._fundamentals_service = fundamentals_service or FundamentalsService()
        self._scoring_service = scoring_service or ScoringService()
        self._sinal_service = sinal_service or SinalService()

    def obter_analise_completa(self, db: Session, ticker: str) -> AnaliseCompletaSchema:
        ticker_normalizado = normalizar_ticker(ticker)

        tecnico = self._tabela_tecnica_service.montar(db, ticker_normalizado)
        estatisticas = self._statistics_service.calcular(db, ticker_normalizado)

        try:
            fundamentos = self._fundamentals_service.obter(ticker_normalizado)
        except ValueError:
            fundamentos = None

        scores = self._scoring_service.calcular(db, ticker_normalizado)
        sinal = self._sinal_service.gerar(db, ticker_normalizado)

        return AnaliseCompletaSchema(
            ticker=ticker_normalizado,
            tecnico=tecnico,
            estatisticas=estatisticas,
            fundamentos=fundamentos,
            scores=scores,
            sinal=sinal,
        )

    def obter_analise_multipla(
        self, db: Session, tickers: list[str]
    ) -> AnaliseMultiplaSchema:
        """
        Processa cada ticker isoladamente. Se um ticker falhar (erro de
        rede, dado ausente no yfinance, timeout etc.), o erro fica
        registrado em `erros` e o processamento continua para os
        demais -- um ativo com problema nunca derruba a tabela inteira.

        Antes so capturavamos ValueError, mas falhas reais de rede/API
        externa (yfinance) podem vir como outros tipos de excecao (ex:
        erros de conexao, timeout, JSON invalido). Por isso capturamos
        Exception aqui -- e o unico lugar do sistema onde isso e
        aceitavel, porque estamos isolando erro por item de uma lista,
        nao escondendo bug de logica interna.
        """
        resultados = []
        erros: dict[str, str] = {}

        for ticker in tickers:
            ticker_normalizado = normalizar_ticker(ticker)
            try:
                resultados.append(self.obter_analise_completa(db, ticker))
            except Exception as exc:
                erros[ticker_normalizado] = str(exc)

        return AnaliseMultiplaSchema(resultados=resultados, erros=erros)