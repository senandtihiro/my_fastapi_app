# app/core/elasticsearch_client.py
from typing import Optional, Dict, Any, List
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from app.core.logger import logger


class ElasticsearchClient:
    """Elasticsearch客户端封装"""

    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None

    async def connect(self) -> None:
        """连接到Elasticsearch"""
        try:
            self.client = AsyncElasticsearch(
                [settings.es_url],
                verify_certs=False,
                request_timeout=30
            )
            info = await self.client.info()
            logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            raise

    async def close(self) -> None:
        """关闭Elasticsearch连接"""
        if self.client:
            await self.client.close()
            logger.info("Elasticsearch connection closed")

    async def search(
            self,
            index: str,
            query: Dict[str, Any],
            size: int = 10,
            from_: int = 0
    ) -> List[Dict[str, Any]]:
        """搜索文档"""
        try:
            result = await self.client.search(
                index=index,
                query=query,
                size=size,
                from_=from_
            )
            hits = result['hits']['hits']
            documents = [hit['_source'] for hit in hits]
            return documents
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            raise


es_client = ElasticsearchClient()
