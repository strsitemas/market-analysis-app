from pydantic import BaseModel


class MediasMoveisSchema(BaseModel):
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    ema_12: float | None = None
    ema_26: float | None = None


class MACDSchema(BaseModel):
    macd: float | None = None
    sinal: float | None = None
    histograma: float | None = None


class BollingerSchema(BaseModel):
    banda_media: float | None = None
    banda_superior: float | None = None
    banda_inferior: float | None = None


class IndicadoresTecnicosSchema(BaseModel):
    ticker: str
    ultima_data: str
    ultimo_fechamento: float
    medias_moveis: MediasMoveisSchema
    rsi_14: float | None = None
    macd: MACDSchema
    bollinger: BollingerSchema
    suporte: float | None = None
    resistencia: float | None = None
    tendencia: str