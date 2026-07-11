# Guia de Contribuição

Este é um projeto privado da **StrSoftware**. Este guia documenta os padrões usados no desenvolvimento, para manter consistência entre colaboradores.

## Fluxo de trabalho

1. Crie uma branch a partir de `main` para a mudança
2. Faça commits pequenos e descritivos (ver convenção abaixo)
3. Teste localmente antes de subir:
   - Backend: `uvicorn app.main:app --reload` + teste manual do endpoint alterado
   - Frontend: `npm run build` (não só `npm run dev` — o build de produção pega erros de tipo que o modo dev pode deixar passar)
4. Abra um Pull Request para `main` com descrição do que mudou e por quê
5. Após merge, o deploy é automático (Render para `backend/`, Vercel para `frontend/`)

## Convenção de commits

Prefixos usados neste projeto:

| Prefixo | Uso |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Alteração apenas de documentação |
| `refactor:` | Mudança de código sem alterar comportamento externo |
| `chore:` | Manutenção (dependências, configuração, `.gitignore` etc.) |

Exemplo:
```
feat: exigir tendencia de alta para sinal de compra + validacao defensiva de scores/tendencia
```

## Padrões de código

### Backend (Python)
- Nomes de variáveis, funções e comentários em **português**, sem acentuação em identificadores (compatibilidade e consistência com o restante do código)
- Um `service` por responsabilidade de domínio (não misturar lógica de indicadores técnicos com lógica de scoring, por exemplo)
- Exceções específicas (`ValueError` etc.) para erros de negócio esperados; capturar `Exception` genérica **apenas** em pontos de isolamento de falha por item (ex: processamento de lista de tickers), nunca para mascarar bugs de lógica
- Toda função que envolve cálculo financeiro deve ter docstring explicando a fórmula e a fonte/motivo da decisão técnica

### Frontend (TypeScript/React)
- Componentes com `"use client"` apenas quando realmente precisam de interatividade/estado no navegador — prefira Server Components por padrão
- Toda rota dinâmica (Server Component com fetch) deve ter um `loading.tsx` correspondente
- Usar `Fragment` explícito (não `<>`) quando precisar de `key` em uma lista
- Chamadas à API sempre via `src/lib/api.ts`, nunca `fetch` direto nos componentes

## Variáveis de ambiente e segredos

- **Nunca** commitar arquivos `.env`, `.env.local` ou `.env.production.local`
- Antes de qualquer commit que toque em configuração, rode `git status` e confirme que nenhum arquivo de ambiente aparece na lista
- Ao gerar uma nova credencial (ex: `SECRET_KEY`), sempre usar um valor diferente entre desenvolvimento e produção

## Avisos de compliance

Este sistema fornece **apoio à decisão**, não recomendação de investimento. Qualquer nova funcionalidade que gere sinais, scores ou sugestões deve:
- Deixar claro que é análise probabilística sobre dados históricos, não promessa de resultado futuro
- Vir acompanhada de justificativa/explicação legível, não apenas um rótulo
- Evitar linguagem que soe como instrução direta de compra/venda sem contexto
