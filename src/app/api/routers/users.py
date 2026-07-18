from fastapi import APIRouter, Depends
from app.models.user import User as UserModel
from app.schemas.user import User
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(deps.get_current_user),
) -> User:
    return current_user

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserUpdate

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    return current_user
