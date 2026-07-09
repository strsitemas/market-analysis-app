export interface Favorito {
  id: number;
  ticker: string;
  criado_em: string;
}

export type TipoAlerta =
  | "preco_acima"
  | "preco_abaixo"
  | "rsi_abaixo"
  | "rsi_acima"
  | "sinal_igual";

export interface Alerta {
  id: number;
  ticker: string;
  tipo: TipoAlerta;
  parametros: Record<string, unknown>;
  ativo: boolean;
  criado_em: string;
}

export interface AlertaDisparo {
  id: number;
  alerta_id: number;
  disparado_em: string;
  valor_no_momento: string;
  lido: boolean;
}