from schemas.user_schemas import UserCreate,UserResponse,UserUpdate
from models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound,IntegrityError
from typing import List,Optional
from uuid import UUID
from fastapi import HTTPException,status,UploadFile
from utils.security import hashed_password
from utils.storage import save_upload_files

#Function to create a new user
async def  create_user(db:AsyncSession,user:UserCreate) -> UserResponse:
    #Check if user with this email already exists
    existing_user = await get_user_by_email(db,user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    #Hash the password
    hashed_pass = hashed_password(user.password)
    
    #Create new user
    new_user = User(
        username = user.username,
        hash_password = hashed_pass,
        email = user.email,
        phone = user.phone
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
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
    users = result.scalars().all()
    
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


#function to update user profile

async def update_user(
    db:AsyncSession,
    user_id:UUID,
    user_update:UserUpdate,
    current_user:User
):
    """Update a user's information"""
    #Get the user to update
    user = await get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    #Only admins can update others user's profiles
    if user.id != user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
        
    #Apply updates
    user = await update_user_attributes(user,user_update,current_user,db)
    
    #Save changes
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def update_user_attributes(
    user:User,
    user_update:UserUpdate,
    current_user:User,
    db:AsyncSession
) -> User:
    """
    Apply updates to user attributes with permission checks for certain fields
    """
    if user_update.username:
        user.username = user_update.username
        
    if user_update.email:
        #Check if email is already used by another user
        existing_user = await get_user_by_email(db,user_update.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"

            )
        user.email = user_update.email
        
    if user_update.password:
        user.hashed_password = hashed_password(user_update.password)
    
    if user_update.phone is not None:
        user.phone = user_update.phone
        
    #Admin fields only 
    
    if current_user.role == "admin":
        if user_update.role is not None:
            user.role = user_update.role
            
        if user_update.status is not None:
            user.status = user_update.status
            
    return user



async def delete_user(db: AsyncSession, user_id: UUID, current_user: User) -> bool:
    """Delete a user"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only admins or the user themselves can delete their account
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    await db.delete(user)
    await db.commit()
    
    return True



async def update_user_image(
    db: AsyncSession,
    user: User,
    file: UploadFile
) -> User:
    """Update a user's profile image"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        image_url = await save_upload_files(file)
        user.image_url = image_url
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )
            
    
