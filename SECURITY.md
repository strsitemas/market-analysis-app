# Política de Segurança

## Medidas implementadas

| Área | Medida |
|---|---|
| Sessão | JWT em cookie `httpOnly` (inacessível a JavaScript, mitiga XSS) |
| Transporte | `Secure=True` em produção (cookie só trafega via HTTPS) |
| Cross-site | `SameSite=None` apenas em produção, com `CORS_ORIGINS` restrito ao domínio exato do frontend (não `*`) |
| Senhas | Hash via `bcrypt` (`passlib`), nunca armazenadas em texto plano |
| Força bruta | Rate limiting (`slowapi` + Redis) em `/auth/login` e `/auth/registrar`: 5 requisições/minuto por IP |
| Segredos | `SECRET_KEY` e credenciais de banco/cache nunca commitados; gerenciados via variáveis de ambiente na plataforma de deploy |
| Rotação de credenciais | `SECRET_KEY` de produção gerado separadamente do de desenvolvimento |

## Reportando uma vulnerabilidade

Se você identificar uma vulnerabilidade de segurança neste projeto, por favor **não abra uma issue pública**. Entre em contato diretamente com a equipe StrSoftware através dos canais internos.

Ao reportar, inclua:
- Descrição do problema e impacto potencial
- Passos para reproduzir
- Versão/commit afetado, se souber

## Escopo

Este projeto está atualmente em ambiente de produção real, mas em estágio de desenvolvimento ativo (plano de hospedagem gratuito, sem SLA formal). Trate os dados como não críticos até uma revisão de segurança mais formal antes de qualquer uso comercial em escala.

## Checklist de segurança antes de cada deploy

- [ ] `.env` e variantes nunca foram commitados (`git log --all --full-history -- backend/.env`)
- [ ] `SECRET_KEY` de produção é diferente do de desenvolvimento
- [ ] `CORS_ORIGINS` aponta para o domínio exato de produção, não wildcard
- [ ] Cookie de sessão confirmado com `HttpOnly` + `Secure` + `SameSite=None` em produção (via DevTools → Application → Cookies)
- [ ] Nenhuma credencial aparece em logs de commit ou em conversas/capturas de tela compartilhadas publicamente
