from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from crud.user import get_user_by_id
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token:str = Depends(oauth2_scheme),
    db:AsyncSession = Depends(get_db)
):
    try:
        palyoad = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        user_id = palyoad.get("sub")
        if not user_id:
            raise HTTPException(status_code=401,detail="Invalid token")
            
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")
    
    user =await  get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    
    return user