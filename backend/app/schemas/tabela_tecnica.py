from app.schemas.indicadores import BollingerSchema, MACDSchema, MediasMoveisSchema
from pydantic import BaseModel


class TabelaTecnicaSchema(BaseModel):
    """
    Linha consolidada da tabela de analise tecnica de um ativo.
    Combina cotacao ao vivo (Yahoo Finance) com indicadores calculados
    a partir do historico salvo no banco de dados.
    """
    ticker: str
    preco_atual: float
    variacao_diaria_pct: float
    volume: int
    liquidez_media_20d: float
    tendencia: str
    suporte: float | None = None
    resistencia: float | None = None
    medias_moveis: MediasMoveisSchema
    rsi_14: float | None = None
    macd: MACDSchema
    bollinger: BollingerSchema