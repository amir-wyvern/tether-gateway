from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

import os
from dotenv import load_dotenv
from pathlib import Path

from fastapi import (
  Depends,
  HTTPException,
  status
) 

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

OAUTH2_SECRET_KEY = os.getenv('OAUTH2_SECRET_KEY')
OAUTH2_ALGORITHM = os.getenv('OAUTH2_ALGORITHM')
OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES'))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, OAUTH2_SECRET_KEY, algorithm=OAUTH2_ALGORITHM)
  return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, OAUTH2_SECRET_KEY, algorithms=[OAUTH2_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
