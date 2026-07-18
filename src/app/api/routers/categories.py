from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.course import Category as CategoryModel
from app.schemas.course import Category, CategoryCreate
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Category])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[CategoryModel]:
    result = await db.execute(select(CategoryModel).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=Category)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_role("admin"))
) -> CategoryModel:
    db_category = CategoryModel(**category_in.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category
