from crud.category import create_category,get_categories,get_category,update_category,upload_image, delete_category
from fastapi import APIRouter,HTTPException,status,Depends
from schemas.category_schemas import CategoryResponse,CategoryCreate,CategoryUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from utils.auth import get_current_user,get_current_active_user
from fastapi import UploadFile,File
from uuid import UUID
from models.models import User


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.post("/",response_model=CategoryResponse)
async def create_new_category(category:CategoryCreate,db:AsyncSession = Depends(get_db),user = Depends(get_current_user)):
    try:
        new_cateogry = await create_category(db,category)
        return new_cateogry
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occured:{e}")
    
@router.get("/",response_model=list[CategoryResponse])
async def get_all_categories(db:AsyncSession = Depends(get_db)):
    return await get_categories(db)
    

@router.get("/{category_id}",response_model=CategoryResponse)
async def get_single_category(category_id:int,db:AsyncSession = Depends(get_db)):
    return await get_category(db,category_id)
    
    
@router.put("/{category_id}",response_model=CategoryResponse)
async def update_category_route(category_id:int,category_data:CategoryUpdate,db:AsyncSession=Depends(get_db),user = Depends(get_current_user)):
    return await update_category(db,category_id,category_data)


#Route for category image upload
@router.post("/{category_id}/image",response_model=CategoryResponse)
async def upload_category_image(category_id:int,file:UploadFile = File(...),db:AsyncSession = Depends(get_db),user = Depends(get_current_user)):
    category = await upload_image(db,category_id,file)
    
        
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
        
    return category
    
    
@router.delete("/{category_id}",response_model=CategoryResponse)
async def delete_category_route(
    category_id:UUID,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    cat = await delete_category(db,category_id,current_user)
    
    return cat