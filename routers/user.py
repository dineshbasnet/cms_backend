from crud.user import create_user,get_all_users
from db import get_db
from schemas.user_schemas import UserCreate,UserResponse
from models.models import User
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    tags=["users"]
)

@router.post("/users",response_model=UserResponse)
async def create_new_user(user:UserCreate,db:AsyncSession = Depends(get_db)):
    try:
        new_user = await create_user(db,user)
        return new_user
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occures {e}")

@router.get("/users",response_model=list[UserResponse])
async def get_users(db:AsyncSession=Depends(get_db)):
    users = await get_all_users(db)
    return users
