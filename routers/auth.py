from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from crud.user import get_user_by_email
from utils.security import verify_password, create_access_token
from schemas.auth_schemas import Token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login",response_model=Token)
async def login(form:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db,form.username)
    if not user or not verify_password(form.password,user.hash_password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    
    token = create_access_token(str(user.id))
    return {"access_token": token}