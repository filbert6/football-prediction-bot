import os
from cachetools import TTLCache
from functools import lru_cache

_cache = TTLCache(maxsize=128, ttl=int(os.environ.get("CACHE_TTL", 3600)))


def get_cache():
    return _cache


def cache_get(key):
    return _cache.get(key)


def cache_set(key, value):
    _cache[key] = value


@lru_cache(maxsize=32)
def expensive_operation(x):
    # placeholder for decorated expensive computation
    return x * 2
