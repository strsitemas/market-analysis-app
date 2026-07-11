# Referência da API — Market Analysis API

Base URL (produção): `https://market-analysis-app-x07d.onrender.com/api/v1`
Documentação interativa (Swagger): `/docs` na raiz do serviço.

Todas as rotas autenticadas dependem do cookie de sessão `access_token` (`httpOnly`), obtido via `POST /auth/login`. Requisições do frontend devem incluir `credentials: "include"`.

---

## Autenticação

### `POST /auth/registrar`
Cria uma nova conta.

**Body** (JSON): `{ "email": string, "senha": string }`
**Resposta:** `201` com dados do usuário criado. `409` se o e-mail já existir.
**Rate limit:** 5 requisições/minuto por IP.

### `POST /auth/login`
Autentica e grava o cookie de sessão.

**Body** (`application/x-www-form-urlencoded`): `username` (e-mail), `password`
**Resposta:** `200`, define o cookie `access_token` (`httpOnly`). `401` se credenciais inválidas.
**Rate limit:** 5 requisições/minuto por IP.

### `POST /auth/logout`
Remove o cookie de sessão. `204` sem corpo.

### `GET /auth/me`
Retorna os dados do usuário autenticado pelo cookie atual. `401` se não autenticado.

---

## Ativos e catálogo

### `GET /ativos/disponiveis`
Lista o catálogo estático de ativos disponíveis para seleção (ticker, nome, setor).

### `GET /ativos/{ticker}/analise-completa`
Retorna a análise completa de um único ativo: técnico, estatísticas, fundamentos, scores e sinal final.

### `GET /ativos/{ticker}/historico-salvo`
Retorna o histórico de cotações já persistido no banco para o ativo.

### `GET /ativos/{ticker}/backtest`
Executa um backtest da estratégia de cruzamento de médias móveis (SMA20 × SMA50) sobre o histórico do ativo.

**Resposta:**
```json
{
  "ticker": "PETR4.SA",
  "estrategia": "Cruzamento de Medias Moveis (SMA20 x SMA50)",
  "periodo_analisado": "2025-07-03 a 2026-07-03",
  "retorno_estrategia_pct": 15.78,
  "retorno_buy_and_hold_pct": 29.40,
  "numero_operacoes": 6,
  "taxa_acerto_pct": 33.33,
  "drawdown_maximo_estrategia_pct": -16.17
}
```

---

## Análise consolidada

### `GET /analise?tickers=PETR4,VALE3,ITUB4`
Retorna a análise completa de múltiplos ativos de uma vez, usada para montar a tabela comparativa. Cada ticker é processado isoladamente — falhas pontuais não afetam os demais.

**Resposta:**
```json
{
  "resultados": [ /* array de AnaliseCompletaSchema */ ],
  "erros": { "TICKER.SA": "motivo da falha" }
}
```

---

## Favoritos

Todas as rotas abaixo exigem autenticação.

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/favoritos` | Lista os favoritos do usuário |
| `POST` | `/favoritos` | Adiciona um ticker aos favoritos (`{ "ticker": "PETR4" }`) |
| `DELETE` | `/favoritos/{ticker}` | Remove dos favoritos |

---

## Alertas

Todas as rotas abaixo exigem autenticação.

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/alertas?apenas_ativos=true` | Lista alertas cadastrados |
| `POST` | `/alertas` | Cria um alerta (`ticker`, `tipo`, `parametros`) |
| `PATCH` | `/alertas/{id}/pausar` | Pausa um alerta |
| `PATCH` | `/alertas/{id}/ativar` | Reativa um alerta |
| `DELETE` | `/alertas/{id}` | Remove um alerta |
| `GET` | `/alertas/disparos?apenas_nao_lidos=true` | Lista disparos registrados |
| `PATCH` | `/alertas/disparos/{id}/marcar-lido` | Marca disparo como lido |
| `POST` | `/alertas/verificar-agora` | Força uma verificação imediata de todos os alertas (fora do ciclo automático de 15 min) |

---

## Indicadores individuais

Rotas granulares (usadas internamente pela análise completa, mas disponíveis isoladamente):

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/ativos/{ticker}/tabela-tecnica` | SMA, EMA, RSI, MACD, Bollinger, suporte/resistência, tendência |
| `GET` | `/ativos/{ticker}/estatisticas` | Volatilidade, retorno acumulado, drawdown, correlação com Ibovespa |
| `GET` | `/ativos/{ticker}/fundamentos` | P/L, P/VP, ROE, margem líquida, dívida/patrimônio, dividend yield |
| `GET` | `/ativos/{ticker}/scores` | Score de risco e score de oportunidade, com detalhamento por fator |
| `GET` | `/ativos/{ticker}/sinal` | Sinal final isolado, com justificativa |

---

## Convenções gerais

- Tickers da B3 são normalizados automaticamente com o sufixo `.SA` (ex: `PETR4` → `PETR4.SA`)
- Erros seguem o formato padrão do FastAPI: `{ "detail": "mensagem" }`
- Todos os valores percentuais são retornados já multiplicados por 100 (ex: `9.83` representa 9,83%)
- Este sistema é uma ferramenta de **apoio à decisão** — nenhum endpoint constitui recomendação de investimento
