# app/api/v1/users.py
from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.api.deps import UserServiceDep
from app.core.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search", response_model=List[UserResponse])


async def search_users(
        keyword: str = Query(None, description="搜索关键词（用户名、邮箱、用户ID）"),
        city: str = Query(None, description="城市筛选"),
        min_age: int = Query(None, ge=0, description="最小年龄"),
        max_age: int = Query(None, ge=0, description="最大年龄"),
        skip: int = Query(0, ge=0, description="跳过数量"),
        limit: int = Query(10, ge=1, le=100, description="每页数量"),
        user_service: UserServiceDep = None
):
    """
    搜索用户接口（从Elasticsearch查询）

    - **keyword**: 关键词搜索（用户名、邮箱、用户ID）
    - **city**: 城市筛选
    - **min_age**: 最小年龄
    - **max_age**: 最大年龄
    - **skip**: 分页跳过数量
    - **limit**: 每页返回数量
    """
    try:
        if min_age is not None and max_age is not None and min_age > max_age:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_age cannot be greater than max_age"
            )

        users = await user_service.search_users(
            keyword=keyword,
            city=city,
            min_age=min_age,
            max_age=max_age,
            skip=skip,
            limit=limit
        )

        logger.info(f"User search completed, found {len(users)} users")
        return users

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )

