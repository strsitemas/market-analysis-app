const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store", credentials: "include" });
  if (!res.ok) {
    throw new Error(`Erro ${res.status} ao consultar ${path}`);
  }
  return res.json() as Promise<T>;
}

async function apiSend<T>(
  path: string,
  method: "POST" | "DELETE" | "PATCH",
  body?: unknown
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
    credentials: "include",
  });
  if (!res.ok) {
    const detalhe = await res.json().catch(() => null);
    throw new Error(detalhe?.detail ?? `Erro ${res.status} ao consultar ${path}`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export function listarAtivosDisponiveis() {
  return apiGet<import("@/types/analise").AtivoDisponivel[]>("/ativos/disponiveis");
}

export function obterAnaliseCompleta(ticker: string) {
  return apiGet<import("@/types/analise").AnaliseCompleta>(
    `/ativos/${ticker}/analise-completa`
  );
}

export function obterAnaliseMultipla(tickers: string[]) {
  const query = tickers.join(",");
  return apiGet<import("@/types/analise").AnaliseMultipla>(
    `/analise?tickers=${encodeURIComponent(query)}`
  );
}

export function obterHistoricoSalvo(ticker: string) {
  return apiGet<import("@/types/analise").HistoricoPonto[]>(
    `/ativos/${ticker}/historico-salvo`
  );
}

// --- Favoritos ---

export function listarFavoritos() {
  return apiGet<import("@/types/monitoramento").Favorito[]>("/favoritos");
}

export function adicionarFavorito(ticker: string) {
  return apiSend<import("@/types/monitoramento").Favorito>("/favoritos", "POST", { ticker });
}

export function removerFavorito(ticker: string) {
  return apiSend<void>(`/favoritos/${ticker}`, "DELETE");
}

// --- Alertas ---

export function listarAlertas(apenasAtivos = false) {
  const query = apenasAtivos ? "?apenas_ativos=true" : "";
  return apiGet<import("@/types/monitoramento").Alerta[]>(`/alertas${query}`);
}

export function criarAlerta(
  ticker: string,
  tipo: import("@/types/monitoramento").TipoAlerta,
  parametros: Record<string, unknown>
) {
  return apiSend<import("@/types/monitoramento").Alerta>("/alertas", "POST", {
    ticker,
    tipo,
    parametros,
  });
}

export function pausarAlerta(id: number) {
  return apiSend<import("@/types/monitoramento").Alerta>(`/alertas/${id}/pausar`, "PATCH");
}

export function ativarAlerta(id: number) {
  return apiSend<import("@/types/monitoramento").Alerta>(`/alertas/${id}/ativar`, "PATCH");
}

export function removerAlerta(id: number) {
  return apiSend<void>(`/alertas/${id}`, "DELETE");
}

export function listarDisparos(apenasNaoLidos = false) {
  const query = apenasNaoLidos ? "?apenas_nao_lidos=true" : "";
  return apiGet<import("@/types/monitoramento").AlertaDisparo[]>(`/alertas/disparos${query}`);
}

export function marcarDisparoComoLido(id: number) {
  return apiSend<import("@/types/monitoramento").AlertaDisparo>(
    `/alertas/disparos/${id}/marcar-lido`,
    "PATCH"
  );
}

export function verificarAlertasAgora() {
  return apiSend<{ avaliados: number; disparados: number; detalhes: unknown[] }>(
    "/alertas/verificar-agora",
    "POST"
  );
}

// --- Autenticacao ---
// O backend agora seta um cookie httpOnly no login. Nao guardamos mais
// token nenhum no frontend -- o navegador manda o cookie sozinho em
// toda chamada, desde que "credentials: include" esteja setado (ja
// esta, em apiGet/apiSend/login/logout).

export function registrarUsuario(email: string, senha: string) {
  return apiSend<import("@/types/auth").Usuario>("/auth/registrar", "POST", { email, senha });
}

export async function login(email: string, senha: string): Promise<void> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", senha);

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
    cache: "no-store",
    credentials: "include",
  });

  if (!res.ok) {
    const detalhe = await res.json().catch(() => null);
    throw new Error(detalhe?.detail ?? "Email ou senha invalidos");
  }
  // Nao precisamos ler o token do corpo: o cookie ja foi setado pela
  // resposta (Set-Cookie). So confirmamos que deu certo.
}

export function logout(): Promise<void> {
  return apiSend<void>("/auth/logout", "POST");
}

export function obterUsuarioAtual() {
  return apiGet<import("@/types/auth").Usuario>("/auth/me");
}