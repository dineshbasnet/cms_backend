from models.models import User
from schemas.user_schemas import UserCreate,UserResponse
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

async def create_user(db:AsyncSession,user:UserCreate) -> UserResponse:
    new_user = User(username=user.username,email=user.email)
    db.add(new_user)
    
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    except IntegrityError:
        await db.rollback()
        raise ValueError("user with this username and email already exits.")
    
    
async def get_all_users(db:AsyncSession) -> list[UserResponse]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users



    
    
    
    