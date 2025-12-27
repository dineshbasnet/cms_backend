from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"],deprecated = "auto")

#function to hash plain password
def hashed_password(plain_password:str) -> str:
    return pwd_context.hash(plain_password)
    