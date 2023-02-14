from cache.database import AUTH_TOKEN_EXPIRE
import redis

def create_auth_session(token, value, db: redis.Redis):
    return db.set(token, value, ex= AUTH_TOKEN_EXPIRE)

def get_auth_code_by_session(token: str, db: redis.Redis):

    return db.get(token)