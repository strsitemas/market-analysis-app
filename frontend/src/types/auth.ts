export interface Usuario {
  id: number;
  email: string;
  ativo: boolean;
  criado_em: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}