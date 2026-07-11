# Changelog

Todas as mudanças relevantes do projeto são documentadas aqui, organizadas pelos blocos de desenvolvimento definidos no planejamento original do sistema.

O formato segue livremente o espírito de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Blocos 1–23] — Sistema completo em produção

### Arquitetura e backend (Blocos 1–9)
- Planejamento técnico e arquitetura geral definidos
- Estrutura inicial do projeto (backend FastAPI + frontend Next.js)
- Configuração de ambiente, dependências e organização de pastas
- Integração com yfinance para dados de mercado
- Coleta de cotações, histórico de preços e volume
- Modelagem do banco PostgreSQL (Neon), com migrations via Alembic
- Cálculo de médias móveis (SMA/EMA), RSI e MACD
- Cálculo de Bandas de Bollinger, suporte, resistência e tendência
- Tabela técnica consolidada por ativo

### Estatística e fundamentos (Blocos 10–12)
- Métricas estatísticas: volatilidade anualizada, retorno acumulado, drawdown máximo, correlação com Ibovespa
- Indicadores fundamentalistas: P/L, P/VP, ROE, margem líquida, dívida/patrimônio, dividend yield
- Score de risco e score de oportunidade (0–100), com detalhamento por fator

### Backtesting e sinal (Blocos 13–15)
- Backtesting de estratégia de cruzamento de médias móveis (SMA20 × SMA50)
- Geração de sinal final (compra, venda, atenção, neutro), com justificativa textual
- API consolidada (`/analise`, `/ativos/{ticker}/analise-completa`) para o frontend

### Frontend (Blocos 16–21)
- Tela inicial e listagem de ativos disponíveis
- Tabela de análise comparativa com filtros e ordenação
- Gráficos de preço, volume e indicadores (Recharts)
- Dashboard geral do mercado
- Página individual por ativo
- Favoritos e alertas, com verificação periódica automática (APScheduler)

### Segurança e deploy (Blocos 22–23)
- Autenticação por e-mail/senha, sessão via cookie `httpOnly`
- Rate limiting em rotas de autenticação (`slowapi` + Redis)
- Deploy do backend no Render, frontend na Vercel
- Configuração de CORS e cookie cross-domain para produção (`SameSite=None` + `Secure`)

## [Não versionado] — Correções e melhorias pós-deploy

### Corrigido
- `requirements.txt` com linha corrompida (`httpx==0.27.2apscheduler==3.10.4`), impedindo build no Render
- Versão do Python no Render fixada via `.python-version` (o Render não lê `runtime.txt`)
- Erro de tipo no `formatter` do `Tooltip` (Recharts) impedindo build de produção da Vercel
- `Framework Preset` da Vercel corrigido de "Other" para "Next.js", resolvendo 404 sistemático em todas as rotas
- `NEXT_PUBLIC_API_URL` recriada após ser salva vazia por engano
- Isolamento de erro por ticker na rota de análise múltipla (antes, uma falha de rede em qualquer ativo derrubava a resposta inteira com 500)
- Warning React de `key` ausente, corrigido trocando fragment curto por `Fragment` explícito com `key`

### Adicionado
- Cache de fundamentos (24h, Redis) para mitigar rate limit do Yahoo Finance em consultas de múltiplos ativos
- Exigência de tendência de alta para o sinal de "compra" (antes considerava apenas os scores de risco e oportunidade)
- Estado "indeterminado" para tendência técnica inválida, evitando que dado incompleto fosse mascarado silenciosamente como "neutro"
- Validação defensiva de scores fora do intervalo 0–100
- Linha expansível na tabela de análise, mostrando a justificativa completa do sinal e métricas adicionais (suporte, resistência, MACD, drawdown, retorno acumulado, correlação, P/L, dividend yield)
- Mensagem amigável ao tentar favoritar sem estar autenticado (antes, erro genérico só visível no console)
- `loading.tsx` nas rotas dinâmicas (`/`, `/analise`, `/ativos`, `/ativos/[ticker]`), dando feedback visual durante cold start do backend
- Monitor externo (UptimeRobot, ping a cada 5 min) para mitigar cold start do plano gratuito do Render

## [Planejado] — Bloco 24

- Melhorias futuras com IA, machine learning e análise preditiva
