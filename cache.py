import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_cached(key: str):
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None


def set_cached(key: str, value, expire_seconds: int = 60):
    redis_client.set(key, json.dumps(value), ex=expire_seconds)