from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schemas import Roles, AccountStatusEnum
from models.models import User
from utils.security import hashed_password
from config import settings


async def seed_admin(db:AsyncSession):
    result = await db.execute(select(User).where(User.role == Roles.admin))
    admin = result.scalars().first()
    
    if admin:
        return
    
    admin_user = User(
        username= settings.ADMIN_NAME,
        email= settings.ADMIN_EMAIL,
        hash_password = hashed_password(settings.ADMIN_PASSWORD),
        role = Roles.admin,
        status = AccountStatusEnum.active,
        verified = True
    )   
    
    db.add(admin_user)
    await db.commit()