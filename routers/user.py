from crud.user import create_user,upload_image
from db import get_db
from schemas.user_schemas import UserCreate,UserResponse
from models.models import User
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile,File


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/",response_model=UserResponse)
async def create_new_user(user:UserCreate,db:AsyncSession = Depends(get_db)):
    try:
        new_user = await create_user(db,user)
        return new_user
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occures {e}")
    
#end point for user image upload
@router.post("/{user_id}/image",response_model=UserResponse)
async def upload_user_image(user_id:int,file:UploadFile = File(...),db:AsyncSession=Depends(get_db)):
    user = await upload_image(db,user_id,file)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user

# @router.get("/users",response_model=list[UserResponse])
# async def get_users(db:AsyncSession=Depends(get_db)):
#     users = await get_all_users(db)
#     return users

