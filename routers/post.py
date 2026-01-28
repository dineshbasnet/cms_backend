from db import get_db
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate,PostStatusUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile,File
from crud.post import( create_post,update_post,delete_post,get_single_post,get_all_posts,
                    get_published_posts,get_published_post,update_post_image)
from models.models import User,Post
from typing import List
from uuid import UUID
from utils.storage import save_upload_files
from schemas.user_schemas import Roles
from utils.auth import get_current_active_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

#public routes
@router.get("/{post_id}/public",response_model=PostResponse)
async def get_public_post(
    post_id:UUID,
    db:AsyncSession = Depends(get_db)
):
    
    return await get_published_post(db,post_id)


@router.get("/public", response_model=List[PostResponse])
async def get_public_posts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    return await get_published_posts(db, skip, limit)


#Post management routes (common for admin and author)
@router.post("/",response_model=PostResponse)
async def create_new_post(post:PostCreate,
                          db:AsyncSession = Depends(get_db),
                          current_user:User = Depends(get_current_active_user)
                    ):
        
    if current_user.role not in [Roles.admin,Roles.author]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )    
    try:        
        new_post = await create_post(db,current_user,image_url,post)
        return new_post
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"errors occurs {e}")

@router.post("/{post_id}/image",response_model=PostResponse)
async def upload_post_image(
    post_id:UUID,
    file:UploadFile = File(...),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    post = await get_single_post(db,post_id,current_user)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    image_url = await save_upload_files(file,subdir="posts")
    post.image_url = image_url
    
    await db.commit()
    await db.refresh(post)

    return post

@router.put("/{post_id}/image",response_model=PostResponse)
async def update_post_image_route(
    post_id:UUID,
    file:UploadFile = File(...),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    return await update_post_image(db,post_id,file,current_user)
    

        
    
        
    
@router.get("/",response_model=List[PostResponse])
async def get_all_posts_route(
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    
    posts = await get_all_posts(db,current_user)
    
    return posts


@router.get("/{post_id}",response_model=PostResponse)
async def get_single_post_route(
    post_id:UUID,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    post = await get_single_post(db,post_id,current_user)
    
    return post


@router.patch("/{post_id}",response_model=PostResponse)
async def update_posts(
    post_id:UUID,
    post_data:PostUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
 
    updated_post = await update_post(db,post_id,current_user,post_data)

    return updated_post


@router.delete("/{post_id}",response_model=PostResponse)
async def delete_post_route(
    post_id:UUID,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    """Only admins or authors can delete"""
    deleted_post =await delete_post(db,post_id,current_user)
    
    return deleted_post

@router.patch("/{post_id}/status",response_model=PostResponse)
async def update_post_status(
    post_id:UUID,
    status_update:PostStatusUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
    
):
    post = await get_single_post(db,post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update post status"
        )
        
    post.status = status_update.status
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return post


