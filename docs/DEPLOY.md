# Runbook de Deploy — Market Analysis App

Este documento descreve como publicar (ou republicar do zero) o backend e o frontend, e como diagnosticar os problemas mais comuns já enfrentados neste projeto.

## Visão geral

| Componente | Plataforma | Deploy |
|---|---|---|
| Backend (FastAPI) | [Render](https://render.com) | Automático a cada push na branch `main`, pasta `backend/` |
| Frontend (Next.js) | [Vercel](https://vercel.com) | Automático a cada push na branch `main`, pasta `frontend/` |
| Banco de dados | [Neon](https://neon.tech) | Gerenciado, não requer deploy |
| Cache | [Upstash](https://upstash.com) | Gerenciado, não requer deploy |

---

## Backend — Render

### Configuração do serviço

| Campo | Valor |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Fixar a versão do Python

⚠️ **Importante:** o Render **não lê `runtime.txt`** (método legado, ignorado silenciosamente). Use um dos dois métodos suportados atualmente:

1. Arquivo `backend/.python-version` com o conteúdo `3.13`
2. Variável de ambiente `PYTHON_VERSION=3.13.0` (ou qualquer patch da série 3.13)

Sem isso, o Render usa a versão mais recente disponível por padrão, que pode não ter wheels pré-compilados para dependências pesadas (`numpy`, `pandas`), forçando compilação do zero e aumentando o tempo de build de segundos para vários minutos — ou falhando.

### Variáveis de ambiente obrigatórias

| Chave | Exemplo/observação |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Connection string do Neon, no formato `postgresql+psycopg2://usuario:senha@host/banco?sslmode=require&channel_binding=require` — **não** copiar o comando `psql '...'` inteiro que o Neon sugere, só a URL pura |
| `REDIS_URL` | Connection string do Upstash, formato `rediss://default:token@host:porta` |
| `SECRET_KEY` | Gerar com `python -c "import secrets; print(secrets.token_hex(32))"` — usar um valor diferente do de desenvolvimento |
| `CORS_ORIGINS` | URL de produção do frontend (ex: `https://seu-app.vercel.app`) — sem barra final |
| `PYTHON_VERSION` | `3.13.0` (redundante com `.python-version`, mas garante o comportamento independentemente do mecanismo que o Render priorizar) |

### Checklist antes de cada deploy manual

1. `requirements.txt` instala limpo em uma venv nova (`python -m venv venv_teste && pip install -r requirements.txt`)
2. `.env` nunca foi commitado (`git log --all --full-history -- backend/.env` deve retornar vazio)
3. `CORS_ORIGINS` aponta para o domínio de produção correto do frontend, não `localhost`

---

## Frontend — Vercel

### Configuração do projeto

| Campo | Valor |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | **Next.js** (não "Other" — ver troubleshooting abaixo) |

### Variável de ambiente obrigatória

| Chave | Exemplo |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://seu-backend.onrender.com/api/v1` — configurar tanto em **Production** quanto em **Preview** |

### Deploy via CLI (alternativa ao painel web)

```bash
npm install -g vercel
vercel login
cd frontend
vercel link          # conectar a pasta ao projeto existente
vercel env pull .env.local
vercel --prod         # build + deploy direto para produção, promovendo automaticamente o domínio
```

O `vercel --prod` é a forma mais confiável de garantir que o domínio de produção aponte para o build mais recente, contornando eventuais inconsistências do painel web (`Promote to Production` às vezes não reflete no domínio principal).

---

## Ordem recomendada para um deploy do zero

1. Publicar o **backend** primeiro no Render, com `CORS_ORIGINS` provisório (ex: `http://localhost:3000`)
2. Anotar a URL final do Render
3. Publicar o **frontend** na Vercel, com `NEXT_PUBLIC_API_URL` apontando para a URL do passo 2
4. Anotar a URL final da Vercel
5. Voltar no Render e atualizar `CORS_ORIGINS` com a URL real da Vercel → disparar redeploy manual
6. Testar login/registro de ponta a ponta e confirmar, via DevTools → Application → Cookies, que `access_token` aparece com `SameSite=None` e `Secure=✓`

---

## Troubleshooting — problemas já enfrentados

### 404 genérico em todas as rotas, mesmo com build bem-sucedido
**Causa raiz:** projeto configurado com **Framework Preset = "Other"** em vez de "Next.js" no painel da Vercel. Sem o preset correto, a Vercel trata o output como estático genérico e não aplica o roteamento necessário para Server Components/rotas dinâmicas.
**Correção:** Settings → Build and Deployment → Framework Preset → **Next.js** → Save → novo deploy.

### `Failed to type check` no build da Vercel (erro de tipo do Recharts `Tooltip`)
**Causa:** anotação de tipo `(value: number) =>` no `formatter` do `Tooltip`, incompatível com o tipo `ValueType | undefined` esperado pela lib.
**Correção:** remover a anotação explícita e usar `Number(value)` dentro da função.

### `NEXT_PUBLIC_API_URL` configurada mas página quebra com "server error"
**Causa:** valor da variável ficou **vazio** ao ser salvo no painel (`""`).
**Diagnóstico:** `vercel env pull .env.production.local --environment=production` e inspecionar o arquivo baixado.
**Correção:** remover e recriar a variável com o valor correto (`vercel env rm` seguido de `vercel env add`).

### Erro 500 em `/analise?tickers=...` com múltiplos tickers, mas endpoint de ticker único funciona
**Causa:** captura de exceção restrita a `ValueError`; falhas de rede/rate-limit do yfinance (outros tipos de exceção) escapavam sem tratamento e derrubavam a rota inteira.
**Correção:** capturar `Exception` genérica no loop de processamento de múltiplos tickers, isolando o erro por ticker no campo `erros` da resposta.

### Falhas intermitentes (falha na 1ª tentativa, sucesso na 2ª idêntica)
**Causa provável:** cold start do Render free tier (processo "dorme" após ~15 min de inatividade) combinado com rate limit pontual do Yahoo Finance na primeira consulta do dia.
**Mitigação:** cache de fundamentos (24h) via Redis + monitor externo (UptimeRobot, intervalo de 5 min) fazendo ping em `/` para manter o serviço acordado + `loading.tsx` no frontend para dar feedback visual durante a espera.

### `Each child in a list should have a unique "key" prop`
**Causa:** uso de fragment curto `<>...</>` dentro de `.map()`, que não aceita a prop `key`.
**Correção:** trocar por `<Fragment key={...}>` explícito, importado de `react`.

### `psycopg2.OperationalError: invalid channel_binding value`
**Causa:** URL de conexão do Neon colada incorretamente — geralmente esquema duplicado (`postgresql+psycopg2://postgresql://...`) ou sufixo `://` sobrando no final, por copiar o comando `psql '...'` completo em vez de só a URL.
**Correção:** reescrever a `DATABASE_URL` com um único esquema no início (`postgresql+psycopg2://`) e terminando limpo em `channel_binding=require`, sem duplicações.
