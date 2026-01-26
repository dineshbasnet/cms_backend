from schemas.user_schemas import UserCreate,UserResponse,UserUpdate,AccountStatusEnum
from models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List,Optional, Dict, Any
from uuid import UUID
import secrets
from fastapi import HTTPException,status,UploadFile
from utils.security import hashed_password
from utils.storage import save_upload_files

#Function to create a new user
async def  create_user(db:AsyncSession,user_data:UserCreate) -> User:
    """Create new user"""
    #Check if user with this email already exists
    existing_user = await get_user_by_email(db,user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
        
    #Hash the password
    password_hashed = hashed_password(user_data.password)
    
    #Create new user
    new_user = User(
        username = user_data.username,
        email = user_data.email,
        hash_password = password_hashed,
        phone = user_data.phone,
        status = AccountStatusEnum.pending_verification,
        verified = False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


async def get_users(
    db:AsyncSession,
    skip:int = 0,
    limit:int = 100,
    filters:Optional[Dict[str,Any]] = None
) -> List[User]:
    """Get a list of users with optional filtering"""
    query = select(User)
    
    if filters:
        if 'role' in filters and filters['role']:
            query = query.filter(User.role==filters['role'])
        if 'status' in filters and filters['status']:
            query = query.filter(User.status == filters['status'])
            
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

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
        user.hash_password = hashed_password(user_update.password)
    
    if user_update.phone is not None:
        user.phone = user_update.phone
        
    #Admin fields only 
    if current_user.role == "admin":
        if user_update.role is not None:
            user.role = user_update.role
            
        if user_update.status is not None:
            user.status = user_update.status
            
        if user_update.verified is not None:
            user.verified = user_update.verified
            
    return user



async def delete_user(db: AsyncSession, user_id: UUID, current_user: User) -> bool:
    """Delete a user"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Only admins or the user themselves can delete their account
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this user"
        )
    
    user.status = AccountStatusEnum.deleted
    user.verified = False
    user.username = f"Anonymous_{user.id.hex[:6]}"
    user.email = f"deleted_{user.id}@gmail.com"
    user.hash_password = secrets.token_urlsafe(32)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return True

#Function to upload user image
async def update_user_image(
    db: AsyncSession,
    user: User,
    file: UploadFile
) -> User:
    """Update a user's profile image"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        image_url = await save_upload_files(file,subdir="users")
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

