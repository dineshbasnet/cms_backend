from models.models import Category
from schemas.category_schemas import CategoryCreate,CategoryResponse,CategoryUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi import HTTPException,status
from typing import List
from sqlalchemy import select
from utils.storage import save_upload_files


# Function for creating category
async def create_category(db:AsyncSession,category:CategoryCreate) -> CategoryResponse:
    new_category = Category(
        name = category.name,
        description = category.description
    )
    
    db.add(new_category)
    try:
        await db.commit()
        await db.refresh(new_category)
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid data")
    
    return new_category



#Function to get all categories
async def get_categories(db:AsyncSession) -> List[CategoryResponse]:
    try:
        result = await db.execute(select(Category))
        categories = result.scalars().all()
        return categories
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to fetch categories")
 
 
  
#Function to get single category
async def get_category(db:AsyncSession,category_id:int) -> CategoryResponse:
   
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
    
    return category



#Function to update category
async def update_category(db:AsyncSession,category_id:int,category_data:CategoryUpdate) -> CategoryResponse:
    try:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalars().first()
        
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
        
        #Apply updates only if values are provided
        update_data = category_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return category
        
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        
        return category
        
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )
        


#Function to upload category image
async def upload_image(db:AsyncSession,category_id:int,file):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(    
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
        
    category.image_url = await save_upload_files(file,subdir="categories")
    await db.commit()
    await db.refresh(category)
    return category
        
        
    