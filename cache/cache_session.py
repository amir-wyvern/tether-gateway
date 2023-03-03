from cache.database import AUTH_TOKEN_EXPIRE
import redis

def create_auth_session(token, value, db: redis.Redis):
    return db.set(token, value, ex= AUTH_TOKEN_EXPIRE)

def get_auth_code_by_session(token: str, db: redis.Redis):
    return db.get(token)

def set_lock_for_user(user_id, db):
    return db.set(f'lock:user:{user_id}', 'True', ex= 300)

def set_lock_for_tx_hash(tx_hash, db):
    return db.set(f'lock:tx_hash:{tx_hash}', 'True', ex= 300)

def unlock_user(user_id, db):
    return db.delete(f'lock:user:{user_id}')

def unlock_tx_hash(tx_hash, db):
    return db.delete(f'lock:tx_hash:{tx_hash}')

def get_status_lock_from_user(user_id, db: redis.Redis):
    return db.get(f'lock:user:{user_id}')

def get_status_lock_from_tx_hash(tx_hash, db: redis.Redis):
    return db.get(f'lock:tx_hash:{tx_hash}')