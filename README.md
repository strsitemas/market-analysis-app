# Market Analysis App

**Ferramenta de apoio à decisão para análise de ativos da bolsa brasileira**, combinando indicadores técnicos, estatística, dados fundamentalistas, score de risco/oportunidade e backtesting de estratégias — desenvolvida por **StrSoftware**.

[![Status](https://img.shields.io/badge/status-em%20produção-brightgreen)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2016-black)]()
[![Deploy](https://img.shields.io/badge/deploy-Render%20%2B%20Vercel-informational)]()
[![License](https://img.shields.io/badge/license-proprietary-lightgrey)]()

> ⚠️ **Aviso importante:** este sistema é uma ferramenta de **apoio à decisão**, baseada em regras estatísticas sobre dados históricos. Ele **não constitui recomendação de investimento**, nem promete previsão garantida de mercado. Decisões financeiras devem considerar contexto mais amplo e, se necessário, orientação de um profissional habilitado.

---

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Stack técnica](#stack-técnica)
- [Arquitetura](#arquitetura)
- [Como rodar localmente](#como-rodar-localmente)
- [Ambientes em produção](#ambientes-em-produção)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Documentação adicional](#documentação-adicional)
- [Roadmap](#roadmap)
- [Licença](#licença)

---

## Visão geral

O usuário seleciona ativos da B3 e o sistema gera uma tabela de análise consolidada contendo preço, variação, volume, liquidez, tendência, suporte/resistência, médias móveis, RSI, MACD, Bandas de Bollinger, volatilidade, retorno acumulado, drawdown, correlação com o Ibovespa, indicadores fundamentalistas, score de risco, score de oportunidade e um sinal final (**compra**, **venda**, **atenção** ou **neutro**), sempre acompanhado da justificativa que levou àquela classificação.

## Funcionalidades

### Análise de mercado
- Indicadores técnicos: SMA, EMA, RSI (14), MACD, Bandas de Bollinger, suporte/resistência, tendência
- Estatística: volatilidade anualizada, retorno acumulado, drawdown máximo, correlação com o Ibovespa
- Fundamentos: P/L, P/VP, ROE, margem líquida, dívida/patrimônio, dividend yield (via yfinance, com cache de 24h)
- Score de risco e score de oportunidade (0–100)
- **Sinal final** com justificativa textual, exigindo tendência de alta confirmada para sinal de compra
- **Backtesting** de estratégia de cruzamento de médias móveis (SMA20 × SMA50), com retorno da estratégia vs. buy-and-hold, taxa de acerto e drawdown

### Plataforma
- Autenticação por e-mail/senha, sessão via cookie `httpOnly` (protegido contra XSS), com `SameSite=None` + `Secure` em produção
- Rate limiting em rotas sensíveis (login/registro)
- Favoritos e alertas de preço/indicador, com verificação periódica automática (scheduler)
- Dashboard geral do mercado e página individual por ativo, com gráfico de preço/volume
- Tabela comparativa com filtros, ordenação e linha expansível mostrando o motivo do sinal

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic |
| Banco de dados | PostgreSQL (hospedado no [Neon](https://neon.tech)) |
| Cache | Redis (hospedado no [Upstash](https://upstash.com)) |
| Dados de mercado | [yfinance](https://github.com/ranaroussi/yfinance) |
| Autenticação | JWT (`python-jose`) + cookie `httpOnly`, hashing com `passlib`/`bcrypt` |
| Agendamento | APScheduler (verificação periódica de alertas) |
| Frontend | Next.js 16 (App Router, Turbopack), React, TypeScript |
| Estilo | Tailwind CSS |
| Gráficos | Recharts |
| Deploy backend | [Render](https://render.com) |
| Deploy frontend | [Vercel](https://vercel.com) |
| Monitoramento de uptime | [UptimeRobot](https://uptimerobot.com) |

## Arquitetura

Visão resumida abaixo — detalhamento completo em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

```
┌─────────────┐      HTTPS       ┌──────────────┐      SQL       ┌──────────────┐
│   Vercel    │ ───────────────▶ │    Render    │ ─────────────▶ │  Neon (PG)   │
│  (Next.js)  │ ◀─────────────── │  (FastAPI)   │ ◀───────────── │              │
└─────────────┘   cookie httpOnly └──────┬───────┘                └──────────────┘
                                          │
                                          │ cache (cotações, histórico, fundamentos)
                                          ▼
                                   ┌──────────────┐
                                   │ Upstash Redis│
                                   └──────────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  Yahoo       │
                                   │  Finance API │
                                   └──────────────┘
```

## Como rodar localmente

### Pré-requisitos
- Python 3.13
- Node.js 20+
- Uma instância PostgreSQL (Neon free tier funciona)
- Uma instância Redis (Upstash free tier funciona)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt

# Configure o .env (ver docs/DEPLOY.md para a lista completa de variáveis)
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`, com documentação interativa em `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install

# Configure o .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

npm run dev
```

O app sobe em `http://localhost:3000`.

## Ambientes em produção

| Serviço | Plataforma | Observação |
|---|---|---|
| API | Render (free tier) | "dorme" após 15 min de inatividade — mitigado com ping periódico via UptimeRobot |
| Frontend | Vercel | deploy automático a cada push na branch `main` |
| Banco de dados | Neon (PostgreSQL) | plano free, connection pooling habilitado |
| Cache | Upstash (Redis) | plano free |

Runbook completo de deploy, variáveis de ambiente e troubleshooting em [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Estrutura de pastas

```
market-analysis-app/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # Rotas HTTP
│   │   ├── core/                  # Configuração, segurança, cache, rate limit
│   │   ├── crud/                  # Acesso a dados
│   │   ├── db/                    # Sessão e base do SQLAlchemy
│   │   ├── models/                # Modelos ORM
│   │   ├── schemas/                # Schemas Pydantic (contrato de API)
│   │   └── services/              # Regras de negócio (indicadores, scores, sinal, backtest...)
│   ├── alembic/versions/          # Migrations do banco
│   ├── requirements.txt
│   └── .python-version
├── frontend/
│   ├── src/
│   │   ├── app/                   # Rotas (App Router do Next.js)
│   │   ├── components/            # Componentes React
│   │   ├── context/                # AuthContext
│   │   ├── lib/                    # Cliente HTTP (api.ts)
│   │   └── types/                  # Tipos TypeScript
│   └── package.json
└── docs/
    ├── ARQUITETURA.md
    ├── API.md
    └── DEPLOY.md
```

## Documentação adicional

| Documento | Conteúdo |
|---|---|
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Decisões técnicas, fluxo de dados, modelagem do banco |
| [`docs/API.md`](docs/API.md) | Referência de todos os endpoints da API |
| [`docs/DEPLOY.md`](docs/DEPLOY.md) | Passo a passo de deploy e variáveis de ambiente |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de blocos/funcionalidades entregues |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Padrões de commit, código e revisão |
| [`SECURITY.md`](SECURITY.md) | Política de segurança e reporte de vulnerabilidades |

## Roadmap

O desenvolvimento seguiu um plano estruturado em 24 blocos. Os Blocos 1–23 estão **completos e em produção**. O Bloco 24 — melhorias futuras com IA, machine learning e análise preditiva — está em aberto como próxima fronteira do projeto.

## Licença

Software proprietário — todos os direitos reservados © StrSoftware. Uso, cópia ou distribuição não autorizados são proibidos. Ver [`LICENSE`](LICENSE).
