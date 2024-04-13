import sys
from datetime import timedelta

import redis
import os

redishost = os.environ['redishost']
redisport = os.environ['redisport']
redispass = os.environ['redispass']

def redis_connect() -> redis.client.Redis:
    try:
        client = redis.RedisCluster(
            host=redishost,
            port=redisport,
            password=redispass,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)

client = redis_connect()

async def get_routes_from_cache(key: str) -> str:
    """Data from redis."""

    val = client.get(key)
    return val


async def set_routes_to_cache(key: str, value: str, ttl: int = 600) -> bool:
    """Data to redis, default == 10 minutes"""

    state = client.setex(key, timedelta(seconds=ttl), value=value)
    return state
