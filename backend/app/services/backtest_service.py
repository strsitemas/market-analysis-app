import pandas as pd
from sqlalchemy.orm import Session

from app import crud
from app.schemas.backtest import BacktestResultSchema
from app.services.indicators import technical
from app.services.market_data_service import normalizar_ticker
from app.services.statistics import technical_stats


class BacktestService:
    """
    Executa um backtest simples de cruzamento de medias moveis
    (SMA curta x SMA longa) sobre o historico JA SALVO no banco.

    Estrategia:
        - Golden cross (SMA curta cruza para CIMA da longa) -> posicao COMPRADA
        - Death cross  (SMA curta cruza para BAIXO da longa) -> posicao NEUTRA (fora do mercado)

    AVISO: backtest com dados historicos NAO garante desempenho futuro.
    Resultados passados de uma estrategia nao se repetem necessariamente.
    """

    def executar(
        self,
        db: Session,
        ticker: str,
        periodo_curto: int = 20,
        periodo_longo: int = 50,
    ) -> BacktestResultSchema:
        ticker_normalizado = normalizar_ticker(ticker)
        ativo = crud.ativo.get_by_ticker(db, ticker_normalizado)
        if ativo is None:
            raise ValueError(
                f"Ativo '{ticker}' nao encontrado. Sincronize o historico "
                "primeiro (POST /ativos/{ticker}/sincronizar)."
            )

        cotacoes = crud.cotacao_historica.listar_por_ativo(db, ativo.id)
        if len(cotacoes) < periodo_longo + 10:
            raise ValueError(
                f"Historico insuficiente para o backtest "
                f"({len(cotacoes)} candles, minimo recomendado "
                f"{periodo_longo + 10}). Sincronize um periodo maior."
            )

        df = pd.DataFrame(
            {
                "data": [c.data for c in cotacoes],
                "fechamento": [float(c.fechamento) for c in cotacoes],
            }
        )
        fechamento = df["fechamento"]

        sma_curta = technical.calcular_sma(fechamento, periodo_curto)
        sma_longa = technical.calcular_sma(fechamento, periodo_longo)

        # Posicao: 1 = comprado (SMA curta acima da longa), 0 = fora do mercado.
        # Usamos .shift(1) para simular que a decisao de hoje so afeta o
        # retorno de AMANHA -- evita "olhar o futuro" (look-ahead bias).
        posicao = (sma_curta > sma_longa).astype(int)
        posicao_aplicada = posicao.shift(1).fillna(0)

        retornos_diarios = fechamento.pct_change().fillna(0)
        retornos_estrategia = retornos_diarios * posicao_aplicada

        capital_estrategia = (1 + retornos_estrategia).cumprod()
        capital_buy_hold = (1 + retornos_diarios).cumprod()

        retorno_estrategia_pct = float((capital_estrategia.iloc[-1] - 1) * 100)
        retorno_buy_hold_pct = float((capital_buy_hold.iloc[-1] - 1) * 100)

        # Detecta mudancas de posicao (0->1 ou 1->0) para contar operacoes
        mudancas_posicao = posicao_aplicada.diff().fillna(0)
        numero_operacoes = int((mudancas_posicao != 0).sum())

        taxa_acerto_pct = self._calcular_taxa_acerto(posicao_aplicada, retornos_diarios)

        drawdown_maximo = technical_stats.calcular_drawdown_maximo(capital_estrategia)

        return BacktestResultSchema(
            ticker=ativo.ticker,
            estrategia=f"Cruzamento de Medias Moveis (SMA{periodo_curto} x SMA{periodo_longo})",
            periodo_analisado=f"{cotacoes[0].data} a {cotacoes[-1].data}",
            retorno_estrategia_pct=round(retorno_estrategia_pct, 2),
            retorno_buy_and_hold_pct=round(retorno_buy_hold_pct, 2),
            numero_operacoes=numero_operacoes,
            taxa_acerto_pct=(
                round(taxa_acerto_pct, 2) if taxa_acerto_pct is not None else None
            ),
            drawdown_maximo_estrategia_pct=round(drawdown_maximo, 2),
        )

    @staticmethod
    def _calcular_taxa_acerto(
        posicao_aplicada: pd.Series, retornos_diarios: pd.Series
    ) -> float | None:
        """
        Agrupa os dias em "operacoes" (sequencias continuas com posicao
        comprada) e calcula o percentual de operacoes com retorno total
        positivo.
        """
        grupo_operacao = (posicao_aplicada != posicao_aplicada.shift(1)).cumsum()
        df_temp = pd.DataFrame(
            {
                "posicao": posicao_aplicada,
                "retorno": retornos_diarios,
                "grupo": grupo_operacao,
            }
        )
        operacoes_compradas = df_temp[df_temp["posicao"] == 1]
        if operacoes_compradas.empty:
            return None

        retorno_por_operacao = (
            operacoes_compradas.groupby("grupo")["retorno"]
            .apply(lambda r: (1 + r).prod() - 1)
        )
        if retorno_por_operacao.empty:
            return None

        acertos = (retorno_por_operacao > 0).sum()
        return float(acertos / len(retorno_por_operacao) * 100)