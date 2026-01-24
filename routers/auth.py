from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from schemas.user_schemas import AccountStatusEnum

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
    user = await get_user_by_email(db,email=form.username)
    if not user or not verify_password(form.password,user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate":"Bearer"}
                            
        )
        
    # Check if user account is active 
    if user.status == AccountStatusEnum.suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact support."
        )
        
    # Update last login time
    user.last_login = datetime.utcnow()
    db.add(user)
    await db.commit()
    


    # Generate access token
    access_token = create_access_token(
        data={"sub":str(user.id),
              "role":user.role.value
              },
        expires_delta=timedelta(minutes=4440)
    )
    
    return {"access_token":access_token,"token_type":"bearer"}