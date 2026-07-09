from datetime import date, datetime

from pydantic import BaseModel, Field


class QuoteSchema(BaseModel):
    """
    Representa a cotacao atual (ou mais recente disponivel) de um ativo.
    """

    ticker: str = Field(..., description="Codigo do ativo, ex: PETR4.SA, AAPL")
    preco_atual: float = Field(..., description="Ultimo preco negociado")
    variacao_diaria_pct: float = Field(
        ..., description="Variacao percentual em relacao ao fechamento anterior"
    )
    volume: int = Field(..., description="Volume negociado no dia")
    data_hora: datetime = Field(..., description="Momento de referencia da cotacao")
    moeda: str = Field(default="BRL", description="Moeda de referencia do preco")


class HistoricalPricePoint(BaseModel):
    """
    Um unico ponto (candle diario) do historico de precos de um ativo.
    """

    data: date
    abertura: float
    maxima: float
    minima: float
    fechamento: float
    volume: int


class HistoricalPriceSchema(BaseModel):
    """
    Serie historica de precos de um ativo, usada como base para todos
    os calculos de indicadores tecnicos e estatisticos.
    """

    ticker: str
    pontos: list[HistoricalPricePoint]