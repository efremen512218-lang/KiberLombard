"""
Redis кэширование для цен и данных
"""
import json
import redis
from typing import Optional, Any
from config import get_settings

settings = get_settings()

# Подключение к Redis (опционально)
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
        port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("[CACHE] Redis подключен")
except Exception as e:
    REDIS_AVAILABLE = False
    print(f"[CACHE] Redis недоступен: {e}")
    redis_client = None


def get_cached(key: str) -> Optional[Any]:
    """Получить значение из кэша"""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"[CACHE] Ошибка чтения: {e}")
    
    return None


def set_cached(key: str, value: Any, ttl: int = 3600) -> bool:
    """Сохранить значение в кэш"""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, ensure_ascii=False, default=str)
        )
        return True
    except Exception as e:
        print(f"[CACHE] Ошибка записи: {e}")
        return False


def delete_cached(key: str) -> bool:
    """Удалить значение из кэша"""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"[CACHE] Ошибка удаления: {e}")
        return False


def clear_cache(pattern: str = "*") -> int:
    """Очистить кэш по паттерну"""
    if not REDIS_AVAILABLE:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"[CACHE] Ошибка очистки: {e}")
        return 0
