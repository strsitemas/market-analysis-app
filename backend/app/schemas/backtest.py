from pydantic import BaseModel


class BacktestResultSchema(BaseModel):
    ticker: str
    estrategia: str
    periodo_analisado: str
    retorno_estrategia_pct: float
    retorno_buy_and_hold_pct: float
    numero_operacoes: int
    taxa_acerto_pct: float | None = None
    drawdown_maximo_estrategia_pct: float