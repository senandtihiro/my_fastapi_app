# app/dao/user_dao.py
from typing import Optional, List, Dict, Any
from app.core.elasticsearch_client import es_client
from app.core.logger import logger


class UserDAO:
    """用户数据访问对象 - 仅查询"""

    INDEX_NAME = "users"

    def __init__(self):
        self.es_client = es_client

    async def search_users(
            self,
            keyword: Optional[str] = None,
            city: Optional[str] = None,
            min_age: Optional[int] = None,
            max_age: Optional[int] = None,
            skip: int = 0,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索用户"""
        try:
            must_conditions = []

            if keyword:
                must_conditions.append({
                    "multi_match": {
                        "query": keyword,
                        "fields": ["username^3", "email^2", "user_id"],
                        "fuzziness": "AUTO"
                    }
                })

            if not must_conditions:
                must_conditions.append({"match_all": {}})

            filter_conditions = []

            if city:
                filter_conditions.append({"term": {"city": city}})

            if min_age is not None or max_age is not None:
                age_range = {}
                if min_age is not None:
                    age_range["gte"] = min_age
                if max_age is not None:
                    age_range["lte"] = max_age
                filter_conditions.append({"range": {"age": age_range}})

            query = {
                "bool": {
                    "must": must_conditions,
                    "filter": filter_conditions
                }
            }

            users = await self.es_client.search(
                index=self.INDEX_NAME,
                query=query,
                size=limit,
                from_=skip
            )

            return users
        except Exception as e:
            logger.error(f"Failed to search users: {str(e)}")
            raise
