from pydantic import BaseModel

from app.schemas.estatisticas import EstatisticasSchema
from app.schemas.fundamentos import FundamentosSchema
from app.schemas.scores import ScoreRiscoOportunidadeSchema
from app.schemas.sinal import SinalFinalSchema
from app.schemas.tabela_tecnica import TabelaTecnicaSchema


class AtivoDisponivelSchema(BaseModel):
    ticker: str
    nome: str
    setor: str


class AnaliseCompletaSchema(BaseModel):
    """
    Linha completa da tabela de analise final, unindo tecnico,
    estatistica, fundamentos, scores e sinal de um unico ativo.
    """

    ticker: str
    tecnico: TabelaTecnicaSchema
    estatisticas: EstatisticasSchema
    fundamentos: FundamentosSchema | None
    scores: ScoreRiscoOportunidadeSchema
    sinal: SinalFinalSchema


class AnaliseMultiplaSchema(BaseModel):
    """
    Resultado de uma consulta em lote (varios tickers de uma vez),
    separando sucessos de falhas para o frontend poder exibir
    parcialmente os dados mesmo se 1 ticker falhar.
    """

    resultados: list[AnaliseCompletaSchema]
    erros: dict[str, str]