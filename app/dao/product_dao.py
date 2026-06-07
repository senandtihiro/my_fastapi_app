# app/dao/product_dao.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_
from app.dao.base_dao import BaseDAO
from app.models.product import Product


class ProductDAO(BaseDAO[Product]):
    """产品数据访问对象"""

    def __init__(self, db):
        super().__init__(Product, db)

    async def create_product(self, product_data: Dict[str, Any]) -> Product:
        """创建产品（调用基类的create方法）"""
        return await self.create(**product_data)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """根据SKU获取产品"""
        stmt = select(Product).where(Product.sku == sku)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Product]:
        """根据名称获取产品"""
        stmt = select(Product).where(Product.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_products(
            self,
            name: Optional[str] = None,
            category: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Product]:
        """搜索产品"""
        conditions = []

        if name:
            conditions.append(Product.name.like(f"%{name}%"))
        if category:
            conditions.append(Product.category == category)
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)

        stmt = select(Product)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())