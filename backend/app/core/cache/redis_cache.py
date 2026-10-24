# Imports dependencies.
import json
import hashlib
from typing import Optional, Dict, Any
from loguru import logger

from app.db.redis_client import redis_client
from app.config import get_settings

settings = get_settings()

class RedisQueryCache:
    def __init__(self):
        self.client = redis_client
        self.default_ttl = settings.redis_cache_ttl_seconds
        self.key_prefix = "rag:query:"

    def _generate_cache_key(self, query: str, top_k: int) -> str:
        """
        Generates a deterministic Redis key based on normalized query text and top_k.
        Example: rag:query:a1b2c3d4...:3
        """
        normalized_query = query.strip().lower()
        query_hash = hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()
        return f"{self.key_prefix}{query_hash}:{top_k}"

    async def get(self, query: str, top_k: int = 3) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached RAG result if available. Returns None on cache miss or error.
        """
        key = self._generate_cache_key(query, top_k)

        try:
            cached_data = await self.client.get(key)
            if cached_data:
                logger.success(f"[CACHE HIT] Returning cached response for query: '{query[:45]}...'")
                data = json.loads(cached_data)
                data["cached"] = True

                return data

            logger.debug(f"[CACHE MISS] No cached response found for query: '{query[:45]}...'")

            return None
        except Exception as e:
            # Fail-Open: if Redis has an issue, log warning and let RAG run normally.
            logger.warning(f"Redis cache read error (falling back to live query): {e}")

            return None

    async def set(self, query: str, top_k: int, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Saves query result to Redis with time-to-live (TTL) expiration.
        """
        key = self._generate_cache_key(query, top_k)
        expiry = ttl or self.default_ttl

        try:
            # Create a clean copy without the 'cached' flag before stroing.
            payload_to_cache = {
                "query": data.get("query"),
                "answer": data.get("answer"),
                "context": data.get("context")
            }

            await self.client.set(key, json.dumps(payload_to_cache), ex=expiry)
            logger.debug(f"Cached response stored in Redis (TTL: {expiry}s) for key: {key}")

            return True
        
        except Exception as e:
            logger.warning(f"Redis cache write errors: {e}")

            return False

    async def clear_all(self) -> int:
        """
        Clears all cached RAG queries from Redis.
        """
        try:
            keys = await self.client.keys(f"{self.key_prefix}*")
            if keys:
                deleted_count = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted_count} cached queries from Redis.")

                return deleted_count
            return 0

        except Exception as e:
            logger.error(f"Failed to clear Redis Cache: {e}")
            return 0

# Instance Creation
redis_query_cache = RedisQueryCache()