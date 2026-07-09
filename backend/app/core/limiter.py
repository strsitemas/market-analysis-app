from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Usa o Redis (Upstash) que voces ja tem configurado como storage dos
# contadores de tentativas, em vez de guardar em memoria local (o que
# nao funcionaria com mais de uma instancia/worker da API).
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)