import pandas as pd


def calcular_sma(series: pd.Series, periodo: int) -> pd.Series:
    """
    Media Movel Simples (SMA): media aritmetica do preco de fechamento
    nas ultimas `periodo` sessoes.

    Formula: SMA_t = (P_t + P_(t-1) + ... + P_(t-n+1)) / n
    """
    return series.rolling(window=periodo, min_periods=periodo).mean()


def calcular_ema(series: pd.Series, periodo: int) -> pd.Series:
    """
    Media Movel Exponencial (EMA): da mais peso aos precos recentes.

    Formula: EMA_t = Preco_t * k + EMA_(t-1) * (1 - k), onde k = 2 / (n + 1)
    """
    return series.ewm(span=periodo, adjust=False, min_periods=periodo).mean()


def calcular_rsi(series: pd.Series, periodo: int = 14) -> pd.Series:
    """
    Indice de Forca Relativa (IFR/RSI). Acima de 70 = possivel
    sobrecompra, abaixo de 30 = possivel sobrevenda. Nao e garantia
    de reversao.

    Formula:
        RS  = media dos ganhos / media das perdas (no periodo)
        RSI = 100 - (100 / (1 + RS))
    """
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(window=periodo, min_periods=periodo).mean()
    media_perda = perda.rolling(window=periodo, min_periods=periodo).mean()

    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(media_perda != 0, 100)
    return rsi


def calcular_macd(
    series: pd.Series,
    periodo_curto: int = 12,
    periodo_longo: int = 26,
    periodo_sinal: int = 9,
) -> pd.DataFrame:
    """
    MACD: mede a relacao entre duas EMAs para identificar momentum.

    Formula:
        Linha MACD  = EMA_curta - EMA_longa
        Linha Sinal = EMA(Linha MACD, periodo_sinal)
        Histograma  = Linha MACD - Linha Sinal
    """
    ema_curta = calcular_ema(series, periodo_curto)
    ema_longa = calcular_ema(series, periodo_longo)
    linha_macd = ema_curta - ema_longa
    linha_sinal = linha_macd.ewm(span=periodo_sinal, adjust=False).mean()
    histograma = linha_macd - linha_sinal

    return pd.DataFrame(
        {"macd": linha_macd, "sinal": linha_sinal, "histograma": histograma}
    )


def calcular_bandas_bollinger(
    series: pd.Series, periodo: int = 20, num_desvios: float = 2.0
) -> pd.DataFrame:
    """
    Bandas de Bollinger: envelope de volatilidade ao redor de uma media
    movel. Bandas largas = alta volatilidade; estreitas = baixa
    volatilidade.

    Formula:
        Banda Media    = SMA(preco, periodo)
        Desvio Padrao  = desvio padrao do preco no mesmo periodo
        Banda Superior = Banda Media + (num_desvios * Desvio Padrao)
        Banda Inferior = Banda Media - (num_desvios * Desvio Padrao)
    """
    media = calcular_sma(series, periodo)
    desvio = series.rolling(window=periodo, min_periods=periodo).std()

    return pd.DataFrame(
        {
            "banda_media": media,
            "banda_superior": media + (num_desvios * desvio),
            "banda_inferior": media - (num_desvios * desvio),
        }
    )


def identificar_suporte_resistencia(df: pd.DataFrame, janela: int = 20) -> dict:
    """
    Metodo simples: usa a minima e a maxima dos ultimos `janela` candles
    como niveis aproximados de suporte e resistencia.
    """
    janela_recente = df.tail(janela)
    return {
        "suporte": float(janela_recente["minima"].min()),
        "resistencia": float(janela_recente["maxima"].max()),
    }


def identificar_tendencia(
    series: pd.Series, periodo_curto: int = 20, periodo_longo: int = 50
) -> str:
    """
    Classifica a tendencia pelo cruzamento de medias moveis:
        media curta > media longa -> ALTA
        media curta < media longa -> BAIXA
        diferenca menor que 0.5%  -> LATERAL
    """
    media_curta = calcular_sma(series, periodo_curto).iloc[-1]
    media_longa = calcular_sma(series, periodo_longo).iloc[-1]

    if pd.isna(media_curta) or pd.isna(media_longa):
        return "indefinida"

    diferenca_pct = abs(media_curta - media_longa) / media_longa
    if diferenca_pct < 0.005:
        return "lateral"
    return "alta" if media_curta > media_longa else "baixa"