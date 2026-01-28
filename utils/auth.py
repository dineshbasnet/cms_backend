from fastapi import Depends,HTTPException,status,Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.user_schemas import AccountStatusEnum

from db import get_db
from crud.user import get_user_by_id
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# async def get_current_user(
#     token:str = Depends(oauth2_scheme),
#     db:AsyncSession = Depends(get_db)
# ):
#     try:
#         palyoad = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
#         user_id = palyoad.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=401,detail="Invalid token")
            
#     except JWTError:
#         raise HTTPException(status_code=401,detail="Invalid token")
    
#     user =await  get_user_by_id(db,user_id)
#     if not user:
#         raise HTTPException(status_code=401,detail="User not found")
    
#     return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await db.get(User, str(UUID(user_id)))

    if user is None:
        raise credentials_exception

    return user


# Verify JWT Token and ensure the user is active 
async def get_current_active_user(current_user:User = Depends(get_current_user)) -> User:
    """
    Verify the user is active (not suspended or inactive)
    """
    if current_user.status == AccountStatusEnum.suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact support."
        )
    
    elif current_user.status == AccountStatusEnum.inactive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please active your account."
        )
        
    return current_user


# Helper function to check token expiration
def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token has expired without raising exceptions
    Returns True if expired, False otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
        expiration = payload.get("exp")
        
        if expiration is None:
            return True
            
        return datetime.utcfromtimestamp(expiration) < datetime.utcnow()
        
    except JWTError:
        return True
    
# Get user's role from token for role-based access control
def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extract user role from a valid JWT token without DB access
    Useful for quick role checks when full user data is not needed
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("role")
        
    except JWTError:
        return None
    
    
def get_token_from_header(authorization:str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
            
        )
        
    return authorization.split(" ")[1]

def get_current_role(token:str = Depends(get_token_from_header)) -> str:
    role = get_user_role_from_token(token)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return role
