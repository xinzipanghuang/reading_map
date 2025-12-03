"""FastAPI 应用主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from knowledge_dag.config import settings
from knowledge_dag.routes import router
from knowledge_dag.storage import storage
from knowledge_dag.models import Project, Chapter, Section, Node, Edge
from datetime import datetime


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # 注册路由
    app.include_router(router, prefix=settings.api_prefix)
    
    # 初始化示例数据    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "knowledge_dag.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )

