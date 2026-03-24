import pytest
import redis.asyncio as redis


@pytest.mark.asyncio
async def test_redis_connection():
    # Пытаемся "пингнуть" Redis
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    response = await redis_client.ping()
    assert response is True

@pytest.mark.asyncio
async def test_redis_set_get():
    # Проверяем запись и чтение
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    await redis_client.set("test_key", "hello_revit")
    value = await redis_client.get("test_key")
    assert value == "hello_revit"
