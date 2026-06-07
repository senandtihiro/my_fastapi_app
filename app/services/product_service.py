# app/services/product_service.py
from typing import Optional, List
from app.dao.product_dao import ProductDAO
from app.schemas.product import ProductResponse, ProductCreate
from app.core.logger import logger


class ProductService:
    """产品服务层 - 仅查询"""

    def __init__(self, product_dao: ProductDAO):
        self.product_dao = product_dao

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """
        创建产品

        Args:
            product_data: 产品创建数据

        Returns:
            创建的产品信息

        Raises:
            DuplicateException: SKU已存在
        """
        # 1. 检查SKU是否已存在
        existing = await self.product_dao.get_by_sku(product_data.sku)
        if existing:
            raise DuplicateException(
                message=f"产品SKU '{product_data.sku}' 已存在",
                data={"sku": product_data.sku}
            )

        # 2. 检查产品名称是否已存在（可选）
        existing_by_name = await self.product_dao.get_by_name(product_data.name)
        if existing_by_name:
            logger.warning(f"Product name '{product_data.name}' already exists, but SKU is different")

        # 3. 创建产品
        product = await self.product_dao.create_product(product_data.model_dump())

        # 4. 提交事务
        await self.product_dao.db.commit()

        # 5. 返回响应
        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """根据ID获取产品"""
        try:
            product = await self.product_dao.get_by_id(product_id)
            if product:
                return ProductResponse.model_validate(product)
            return None
        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {str(e)}")
            raise

    async def get_product_by_sku(self, sku: str) -> Optional[ProductResponse]:
        """根据SKU获取产品"""
        try:
            product = await self.product_dao.get_by_sku(sku)
            if product:
                return ProductResponse.model_validate(product)
            return None
        except Exception as e:
            logger.error(f"Failed to get product by sku {sku}: {str(e)}")
            raise

    async def search_products(
            self,
            name: Optional[str] = None,
            category: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            skip: int = 0,
            limit: int = 10
    ) -> List[ProductResponse]:
        """搜索产品"""
        try:
            products = await self.product_dao.search_products(
                name=name,
                category=category,
                min_price=min_price,
                max_price=max_price,
                skip=skip,
                limit=limit
            )
            return [ProductResponse.model_validate(p) for p in products]
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            raise
