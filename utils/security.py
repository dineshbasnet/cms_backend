from passlib.context import CryptContext
from datetime import datetime,timedelta
import uuid
from jose import jwt
from config import settings

pwd_context = CryptContext(schemes=["argon2"],deprecated = "auto")

#function to hash plain password
def hashed_password(plain_password:str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password,hashed_password) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(subject:str):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub":subject,"exp":expire}
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)