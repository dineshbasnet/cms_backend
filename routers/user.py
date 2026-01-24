from crud.user import create_user,upload_image,get_user_by_id,get_users
from db import get_db
from uuid import UUID
from utils.auth import get_current_user
from sqlalchemy import select
from schemas.user_schemas import UserCreate,UserResponse
from models.models import User
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile,File


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register",response_model=UserResponse)
async def create_new_user(user_data:UserCreate,db:AsyncSession = Depends(get_db)):
    try:
        new_user = await create_user(db,user_data)
        return new_user
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occures {e}")
    
#end point for user image upload
@router.post("/{user_id}/image",response_model=UserResponse)
async def upload_user_image(user_id:UUID,file:UploadFile = File(...),db:AsyncSession=Depends(get_db)):
    user = await upload_image(db,user_id,file)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user

@router.get("/",response_model=list[UserResponse])
async def get_all_users(db:AsyncSession=Depends(get_db)):
    users = await get_users(db)
    return users


@router.get("/{user_id}",response_model=UserResponse)
async def get_single_user(user_id:str,db:AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    return user
    

