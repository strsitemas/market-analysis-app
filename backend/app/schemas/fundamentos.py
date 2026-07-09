from pydantic import BaseModel


class FundamentosSchema(BaseModel):
    ticker: str
    nome_empresa: str | None = None
    setor: str | None = None
    pl: float | None = None
    pvp: float | None = None
    roe_pct: float | None = None
    margem_liquida_pct: float | None = None
    divida_patrimonio: float | None = None
    dividend_yield_pct: float | None = None