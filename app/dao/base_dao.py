# app/dao/base_dao.py
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base
from app.core.logger import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    """基础DAO类 - 仅查询"""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs) -> ModelType:
        """创建单条记录"""
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            await self.db.flush()
            await self.db.refresh(instance)
            logger.info(f"Created {self.model.__name__}: {instance}")
            return instance
        except Exception as e:
            logger.error(f"Failed to create {self.model.__name__}: {str(e)}")
            raise

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据ID获取记录"""
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get {self.model.__name__} by id {id}: {str(e)}")
            raise

    async def list(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters
    ) -> List[ModelType]:
        """获取记录列表"""
        try:
            stmt = select(self.model)

            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Failed to list {self.model.__name__}: {str(e)}")
            raise

    async def count(self, **filters) -> int:
        """统计记录数"""
        try:
            stmt = select(func.count()).select_from(self.model)

            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

            result = await self.db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {str(e)}")
            raise