# Arquitetura — Market Analysis App

Documento técnico de referência sobre as decisões de arquitetura do sistema. Complementa o [`README.md`](../README.md).

## 1. Visão geral do fluxo de dados

```
Usuário
  │
  ▼
Frontend (Next.js / Vercel)
  │  HTTPS + cookie httpOnly
  ▼
Backend (FastAPI / Render)
  │
  ├──▶ PostgreSQL (Neon)        → dados persistentes: usuários, ativos, cotações
  │                               históricas, favoritos, alertas
  │
  ├──▶ Redis (Upstash)          → cache: cotações (60s), histórico (1h),
  │                               fundamentos (24h)
  │
  └──▶ Yahoo Finance (yfinance) → fonte de dados de mercado ao vivo
```

## 2. Backend

### 2.1 Camadas

O backend segue uma separação clássica em camadas:

- **`api/v1/endpoints/`** — rotas HTTP (FastAPI routers), sem lógica de negócio
- **`services/`** — lógica de negócio isolada por responsabilidade (um service por domínio: indicadores, estatísticas, fundamentos, scores, sinal, backtest, alertas)
- **`crud/`** — acesso direto ao banco (SQLAlchemy)
- **`models/`** — modelos ORM
- **`schemas/`** — contratos de entrada/saída da API (Pydantic), desacoplados dos models

Essa separação permite testar cada `service` isoladamente e trocar a fonte de dados (ex: outro provedor além do yfinance) sem tocar nas rotas.

### 2.2 Orquestração da análise completa

`AnaliseService` (`app/services/analise_service.py`) é o orquestrador central: recebe um ticker, chama em sequência `TabelaTecnicaService`, `StatisticsService`, `FundamentalsService`, `ScoringService` e `SinalService`, e consolida tudo em um único schema de resposta (`AnaliseCompletaSchema`).

Para análise de múltiplos ativos (`/analise?tickers=...`), cada ticker é processado **isoladamente**: uma falha em um ativo (ex: dado ausente no yfinance) é capturada e reportada no campo `erros` da resposta, sem interromper o processamento dos demais.

### 2.3 Regra do sinal final

Implementada em `SinalService._decidir`, com prioridade de avaliação:

1. **Risco ≥ 75** → `atencao`, independentemente da oportunidade (proteção nunca é sobrescrita)
2. **Oportunidade ≥ 70 E risco ≤ 50 E tendência = alta** → `compra`
3. **Oportunidade ≤ 30 E tendência = baixa** → `venda`
4. Caso contrário → `neutro`
5. Tendência fora de `{alta, baixa, lateral}` → `indeterminado` (dado de entrada incompleto, tratado explicitamente em vez de mascarado como neutro)

A exigência de tendência de alta para o sinal de compra é intencional: evita sinalizar compra em um ativo tecnicamente em queda, mesmo que os scores numéricos estejam favoráveis.

### 2.4 Cache

Implementado via `CacheService` (`app/services/cache_service.py`), uma camada genérica sobre Redis com serialização Pydantic:

| Dado | TTL | Motivo |
|---|---|---|
| Cotação atual | 60s | Preço muda a cada instante, mas não precisa ser em tempo real |
| Histórico de preços | 1h | Candles diários não mudam intraday |
| Fundamentos (P/L, ROE etc.) | 24h | Mudam tipicamente uma vez por trimestre; cache agressivo reduz drasticamente as chamadas ao Yahoo Finance e mitiga rate limiting em consultas de múltiplos ativos |

### 2.5 Autenticação

- Login gera um JWT (`python-jose`), gravado em cookie `httpOnly` (inacessível a JavaScript, mitigando XSS)
- `SameSite` e `Secure` são condicionais ao ambiente:
  - **Desenvolvimento** (`APP_ENV=development`): `SameSite=Lax`, `Secure=False` — funciona em `http://localhost` sem HTTPS
  - **Produção** (`APP_ENV=production`): `SameSite=None`, `Secure=True` — necessário porque backend (Render) e frontend (Vercel) ficam em domínios diferentes (cookie cross-site exige `SameSite=None`, que por sua vez exige HTTPS)
- Rate limiting (`slowapi` + Redis) em `/auth/login` e `/auth/registrar` (5 requisições/minuto)

### 2.6 Alertas

`APScheduler` roda em background dentro do processo da API, avaliando alertas cadastrados a cada 15 minutos (`avaliar_alertas_job`). Como o Render free tier pode "dormir" o processo por inatividade, o scheduler reinicia do zero a cada cold start — não há persistência de estado do agendador entre reinícios (limitação conhecida do plano gratuito; ver seção de riscos abaixo).

## 3. Frontend

### 3.1 Renderização

Next.js 16 (App Router) mistura rotas estáticas e dinâmicas:

- **Estáticas** (`○`): `/login`, `/registrar`, `/dashboard`, `/favoritos`, `/alertas` — buscam dado no navegador (client-side), via `"use client"` + `useEffect`
- **Dinâmicas** (`ƒ`): `/`, `/analise`, `/ativos`, `/ativos/[ticker]` — Server Components que buscam dado no servidor da Vercel a cada requisição

Cada rota dinâmica tem um `loading.tsx` correspondente, exibido automaticamente pelo Next.js enquanto o fetch no servidor está em andamento — importante porque o cold start do backend pode levar 30–60s na primeira requisição do dia.

### 3.2 Cliente HTTP

`src/lib/api.ts` centraliza todas as chamadas à API, sempre com `credentials: "include"` (necessário para o cookie de sessão trafegar cross-domain) e leitura de `NEXT_PUBLIC_API_URL` do ambiente.

## 4. Modelagem do banco de dados

| Tabela | Descrição |
|---|---|
| `usuarios` | Conta do usuário (e-mail, hash de senha) |
| `ativos` | Catálogo de ativos monitorados |
| `cotacoes_historicas` | Candles diários (OHLCV) por ativo, com constraint de unicidade `(ativo_id, data)` |
| `favoritos` | Relação usuário ↔ ativo favoritado |
| `alertas` | Regras de alerta cadastradas por usuário |
| `alertas_disparos` | Histórico de disparos de alerta |

Migrations gerenciadas via Alembic (`backend/alembic/versions/`).

## 5. Riscos conhecidos e mitigações

| Risco | Mitigação atual | Status |
|---|---|---|
| Rate limit do Yahoo Finance em consultas de múltiplos ativos | Cache de fundamentos (24h) via Redis | Mitigado |
| Cold start do Render free tier (~30–60s) | `loading.tsx` no frontend + ping do UptimeRobot a cada 5 min | Mitigado |
| Scheduler de alertas não persiste entre reinícios do processo | Nenhuma (limitação do plano gratuito) | **Em aberto** |
| Ausência de log/monitoramento de erro persistente (ex: Sentry) | Nenhuma — logs do Render são efêmeros | **Em aberto** |
| Encoding de acentos em alguns campos vindos do yfinance | Nenhuma (cosmético, não afeta funcionalidade) | **Em aberto** |

## 6. Decisões de design deliberadas

- **Cookie `httpOnly` em vez de token em `localStorage`**: reduz superfície de ataque XSS, ao custo de exigir configuração cuidadosa de CORS/SameSite entre domínios distintos.
- **Isolamento de erro por ticker** na análise múltipla: uma falha pontual (ex: dado ausente para um ativo) nunca derruba a experiência inteira do usuário.
- **Sinal de compra exige tendência de alta**: prioriza coerência técnica sobre "otimizar" a frequência de sinais fortes — o sistema pode legitimamente retornar `neutro` para todos os ativos de uma consulta, se for o que os dados indicam.
- **Cache com TTL diferenciado por tipo de dado**: cotação (60s) reflete o mercado quase em tempo real; fundamentos (24h) evitam chamadas desnecessárias a um dado que muda pouco.
