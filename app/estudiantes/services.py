import json
import os

from config import get_redis_client
from estudiantes import repository

CACHE_TTL = int(os.getenv("CACHE_TTL", 300))


def get_perfil_cached(id: str) -> dict | None:
    """Devuelve el perfil desde Redis si existe, si no lo busca en DynamoDB y lo cachea."""
    redis = get_redis_client()
    cache_key = f"estudiante:{id}"

    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    perfil = repository.get_perfil(id)
    if perfil:
        redis.setex(cache_key, CACHE_TTL, json.dumps(perfil))

    return perfil


def invalidate_cache(id: str) -> None:
    """Elimina el perfil del caché cuando se borra el estudiante."""
    get_redis_client().delete(f"estudiante:{id}")
