import numpy as np
import pandas as pd

DIAS_UTEIS_POR_ANO = 252


def calcular_retornos_diarios(series: pd.Series) -> pd.Series:
    """
    Retorno diario percentual: variacao entre um fechamento e o anterior.
    Formula: retorno_t = (preco_t / preco_(t-1)) - 1
    """
    return series.pct_change().dropna()


def calcular_volatilidade_anualizada(series: pd.Series) -> float:
    """
    Volatilidade anualizada: desvio padrao dos retornos diarios,
    escalado para o periodo de 1 ano.

    Formula: volatilidade = desvio_padrao(retornos_diarios) * sqrt(252)

    Por que multiplicar pela raiz de 252? A variancia de retornos
    independentes soma-se ao longo do tempo; o desvio padrao (raiz da
    variancia) portanto escala com a raiz do numero de periodos.
    252 e o numero aproximado de pregoes em um ano na B3.
    """
    retornos = calcular_retornos_diarios(series)
    return float(retornos.std() * np.sqrt(DIAS_UTEIS_POR_ANO) * 100)


def calcular_retorno_acumulado(series: pd.Series) -> float:
    """
    Retorno acumulado no periodo analisado.
    Formula: retorno = (preco_final / preco_inicial - 1) * 100
    """
    preco_inicial = series.iloc[0]
    preco_final = series.iloc[-1]
    return float((preco_final / preco_inicial - 1) * 100)


def calcular_drawdown_maximo(series: pd.Series) -> float:
    """
    Drawdown maximo: a maior queda percentual (pico ate o fundo) no
    periodo. Serve como medida de "pior perda historica" do ativo.

    Formula:
        pico_acumulado_t = maior preco ja visto ate o dia t
        drawdown_t        = (preco_t / pico_acumulado_t) - 1
        drawdown_maximo    = valor minimo (mais negativo) de drawdown_t
    """
    pico_acumulado = series.cummax()
    drawdown = (series / pico_acumulado) - 1
    return float(drawdown.min() * 100)


def calcular_correlacao(
    series_ativo: pd.Series, series_indice: pd.Series
) -> float | None:
    """
    Correlacao de Pearson entre os retornos diarios do ativo e os
    retornos diarios do indice de referencia (ex: Ibovespa).

    Interpretacao:
        proximo de +1  -> ativo se move junto com o indice
        proximo de  0  -> movimento independente do indice
        proximo de -1  -> ativo se move de forma oposta ao indice
    """
    retornos_ativo = calcular_retornos_diarios(series_ativo)
    retornos_indice = calcular_retornos_diarios(series_indice)

    df = pd.DataFrame(
        {"ativo": retornos_ativo, "indice": retornos_indice}
    ).dropna()

    if len(df) < 2:
        return None

    correlacao = df["ativo"].corr(df["indice"])
    return None if pd.isna(correlacao) else float(correlacao)