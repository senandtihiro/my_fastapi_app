# app/services/user_service.py
from typing import Optional, List
from app.dao.user_dao import UserDAO
from app.schemas.user import UserResponse
from app.core.logger import logger


class UserService:
    """用户服务层 - 仅查询"""

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def search_users(
            self,
            keyword: Optional[str] = None,
            city: Optional[str] = None,
            min_age: Optional[int] = None,
            max_age: Optional[int] = None,
            skip: int = 0,
            limit: int = 10
    ) -> List[UserResponse]:
        """搜索用户"""
        try:
            users = await self.user_dao.search_users(
                keyword=keyword,
                city=city,
                min_age=min_age,
                max_age=max_age,
                skip=skip,
                limit=limit
            )
            return [UserResponse(**user) for user in users]
        except Exception as e:
            logger.error(f"Failed to search users: {str(e)}")
            raise
