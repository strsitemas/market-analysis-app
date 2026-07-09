from pydantic import BaseModel


class EstatisticasSchema(BaseModel):
    ticker: str
    periodo_analisado: str
    volatilidade_anualizada_pct: float
    retorno_acumulado_pct: float
    drawdown_maximo_pct: float
    correlacao_ibovespa: float | None = None