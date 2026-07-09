import redis

from app.core.config import settings

# decode_responses=True faz o cliente retornar strings (str) em vez de
# bytes, o que facilita o trabalho com JSON.
redis_client = redis.from_url(settings.redis_url, decode_responses=True)