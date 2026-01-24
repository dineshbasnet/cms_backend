from schemas.user_schemas import UserCreate,UserResponse,UserUpdate
from models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound,IntegrityError
from typing import List,Optional
from uuid import UUID
from fastapi import HTTPException,status
from utils.security import hashed_password
from utils.storage import save_upload_files

#Function to create a new user
async def  create_user(db:AsyncSession,user:UserCreate) -> UserResponse:
    new_user = User(
        username = user.username,
        email = user.email,
        phone = user.phone,
        image_url = "image.png"
    )
    #pass hashing password function to hast the plain password
    new_user.hash_password = hashed_password(user.password)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User with this email already registered")
    
    return new_user
      
#Function to upload user image
async def upload_image(db:AsyncSession,user_id:UUID,file):
    result = await db.execute(select(User).where(User.id ==user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"

        )
        
    #Save image
    user.image_url = await save_upload_files(file,subdir="users")
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db:AsyncSession) -> List[UserResponse]:
    result = await db.execute(select(User))
    users = result.all()
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found"
        )
        
    return users



#Function to gettting user by email
async def get_user_by_email(db:AsyncSession,email:str):
    result =  await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


#Function to get user by user id
async def get_user_by_id(db:AsyncSession,user_id):
    return await db.get(User,user_id)


