"""配置管理模块"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    api_title: str = "Knowledge DAG Builder API"
    api_version: str = "1.0.0"
    api_prefix: str = ""
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS 配置
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # 数据存储配置
    data_file: Path = Path(__file__).parent.parent / "projects_data.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

