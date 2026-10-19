from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from ..schemas.schemas_user import UserResponse

async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён: требуется роль администратора"
        )
    return current_user