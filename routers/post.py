from db import get_db
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException,status
from crud.post import create_post,get_all_posts,get_post,update_post
from models.models import User
from uuid import UUID
from schemas.user_schemas import Roles
from utils.auth import get_current_active_user,get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post("/",response_model=PostResponse)
async def create_new_post(post:PostCreate,db:AsyncSession = Depends(get_db),current_user:User = Depends(get_current_user)):
    if current_user.role not in [Roles.admin,Roles.author]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    try:
        new_post = await create_post(db,current_user.id,post)
        return new_post
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"errors occurs {e}")
    
    

@router.get("/",response_model=list[PostResponse])
async def get_all_posts_route(db:AsyncSession = Depends(get_db)):
    return await get_all_posts(db)

@router.get("/{post_id}",response_model=PostResponse)
async def get_single_post(post_id:UUID,db:AsyncSession = Depends(get_db)):
    return await get_post(db,post_id)


@router.put("/{post_id}",response_model=PostResponse)
async def update_posts(
    post_id:UUID,
    post_data:PostUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_user)
):
    post = await get_post(db,post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    updated_post = await update_post(db,post_data,post_id)

    return updated_post
    