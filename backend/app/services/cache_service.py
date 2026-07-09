import json
from typing import Callable, TypeVar

from pydantic import BaseModel

from app.core.redis_client import redis_client

T = TypeVar("T", bound=BaseModel)


class CacheService:
    """
    Camada generica de cache usando Redis.

    Motivo tecnico: centraliza a logica de serializacao/deserializacao
    e TTL (tempo de vida) do cache, evitando repetir esse padrao em
    cada service que precisar cachear algo.
    """

    @staticmethod
    def get(key: str) -> dict | None:
        raw = redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    @staticmethod
    def set(key: str, value: dict, ttl_seconds: int) -> None:
        redis_client.set(key, json.dumps(value), ex=ttl_seconds)

    @staticmethod
    def get_or_set_model(
        key: str,
        ttl_seconds: int,
        model_class: type[T],
        fetch_fn: Callable[[], T],
    ) -> T:
        """
        Busca um valor no cache; se nao existir, chama fetch_fn(),
        salva o resultado no cache e retorna.
        """
        cached = CacheService.get(key)
        if cached is not None:
            return model_class(**cached)

        result = fetch_fn()
        CacheService.set(key, result.model_dump(mode="json"), ttl_seconds)
        return result