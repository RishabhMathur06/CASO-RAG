# Imports dependencies.
import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

# Initializes connection with Redis server.
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True   #transforms raw bytes into python strings.
)

# Health Check.
async def check_redis_connection():
    try:
        await redis_client.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")