export interface AtivoDisponivel {
  ticker: string;
  nome: string;
  setor: string;
}

export interface MediasMoveis {
  sma_20: number;
  sma_50: number;
  sma_200: number;
  ema_12: number;
  ema_26: number;
}

export interface Macd {
  macd: number;
  sinal: number;
  histograma: number;
}

export interface Bollinger {
  banda_media: number;
  banda_superior: number;
  banda_inferior: number;
}

export interface TabelaTecnica {
  ticker: string;
  preco_atual: number;
  variacao_diaria_pct: number;
  volume: number;
  liquidez_media_20d: number;
  tendencia: "alta" | "baixa" | "lateral";
  suporte: number;
  resistencia: number;
  medias_moveis: MediasMoveis;
  rsi_14: number;
  macd: Macd;
  bollinger: Bollinger;
}

export interface Estatisticas {
  ticker: string;
  periodo_analisado: string;
  volatilidade_anualizada_pct: number;
  retorno_acumulado_pct: number;
  drawdown_maximo_pct: number;
  correlacao_ibovespa: number;
}

export interface Fundamentos {
  ticker: string;
  nome_empresa: string;
  setor: string;
  pl: number | null;
  pvp: number | null;
  roe_pct: number | null;
  margem_liquida_pct: number | null;
  divida_patrimonio: number | null;
  dividend_yield_pct: number | null;
}

export interface Scores {
  ticker: string;
  score_risco: number;
  score_oportunidade: number;
  detalhes_risco: Record<string, number>;
  detalhes_oportunidade: Record<string, number>;
}

export interface SinalFinal {
  ticker: string;
  sinal: "compra" | "venda" | "atencao" | "neutro";
  justificativa: string;
  score_risco: number;
  score_oportunidade: number;
  tendencia: string;
}

export interface AnaliseCompleta {
  ticker: string;
  tecnico: TabelaTecnica;
  estatisticas: Estatisticas;
  fundamentos: Fundamentos | null;
  scores: Scores;
  sinal: SinalFinal;
}

export interface AnaliseMultipla {
  resultados: AnaliseCompleta[];
  erros: Record<string, string>;
}
export interface HistoricoPonto {
  data: string;
  abertura: number;
  maxima: number;
  minima: number;
  fechamento: number;
  volume: number;
  id: number;
  ativo_id: number;
}
