from pydantic_settings import BaseSettings
from typing import Optional

"""
实现 Settings 类:
继承 BaseSettings
定义所有配置字段（数据库、Redis、Celery、应用等）
配置从 .env 文件加载
创建全局 settings 实例
"""

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis (Optional for now, required for Celery/Cache in later stages)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    # Celery (Optional for now, required in Stage 6)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Application
    APP_NAME: str = "WebProbe"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Cache
    CACHE_TTL: int = 300

    # Scraper
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    USER_AGENT: str = "WebProbe/1.0"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()