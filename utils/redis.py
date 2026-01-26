import redis.asyncio as redis
from config import settings


redis_client = redis.from_url(settings.REDIS_URL,decode_responses = True)

async def store_in_redis(key:str, value:str,ttl:int):
    await redis_client.setex(key,ttl,value)
    
async def get_from_redis(key:str):
    return await redis_client.get(key)

async def delete_from_redis(key:str):
    await redis_client.delete(key)
    
    