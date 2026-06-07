# app/core/config.py
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # SQLite配置
    sqlite_url: str = "sqlite+aiosqlite:///./app.db"
    sqlite_echo: bool = False

    # Elasticsearch配置
    es_host: str = "localhost"
    es_port: int = 9200
    es_user: Optional[str] = None
    es_password: Optional[str] = None

    # 应用配置
    app_name: str = "Product & User Search API"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def es_url(self) -> str:
        """获取Elasticsearch连接URL"""
        if self.es_user and self.es_password:
            return f"http://{self.es_user}:{self.es_password}@{self.es_host}:{self.es_port}"
        return f"http://{self.es_host}:{self.es_port}"


settings = Settings()
