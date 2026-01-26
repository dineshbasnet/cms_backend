from passlib.context import CryptContext
from datetime import datetime,timedelta
from uuid import uuid4
from typing import Dict,Any,Optional
from jose import jwt
from config import settings
import random
import secrets

pwd_context = CryptContext(schemes=["argon2"],deprecated = "auto")

#function to hash plain password
def hashed_password(plain_password:str) -> str:
    return pwd_context.hash(plain_password)

#Helper function to verify passwords
def verify_password(plain_password,hashed_password) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

#Create JWT Token
def create_access_token(data:Dict[str,Any],expires_delta:Optional[timedelta] = None) -> str:
    """Generate a JWT access token with optional expiration"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({
            "exp":expire,
            "iat":datetime.utcnow(),
            "jti":str(uuid4()) # JWT ID for token uniqueness
        })
        
    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    
    return encoded_jwt

#Function to generate random otp
def generate_otp(length:int = 6) -> str:
    return "".join(str(random.randint(0,9)) for _ in range(length))


#Generate reset token
def generate_secure_token(length:int = 32) -> str:
    return secrets.token_urlsafe(length)