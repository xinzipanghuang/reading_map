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
    _init_demo_data()
    
    return app


def _init_demo_data():
    """初始化示例数据"""
    projects = storage.get_all()
    # 如果没有任何项目，或者 demo 项目不存在，创建 demo 项目
    if not projects or "demo" not in projects:
        demo_chapter = Chapter(
            id="ch1",
            name="第一章：基础概念",
            sections=[
                Section(
                    id="sec1",
                    name="1.1 基本定义",
                    nodes=[
                        Node(id="node1", name="集合", content="集合是数学中的基本概念"),
                        Node(id="node2", name="函数", content="函数是映射关系")
                    ]
                ),
                Section(
                    id="sec2",
                    name="1.2 运算",
                    nodes=[
                        Node(id="node3", name="加法", content="加法的定义和性质")
                    ]
                )
            ]
        )
        
        demo_project = Project(
            id="demo",
            name="示例项目：数学基础",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            chapters=[demo_chapter],
            edges=[
                Edge(source="node1", target="node2", label=""),
                Edge(source="node2", target="node3", label="")
            ]
        )
        # 如果 demo 已存在，更新它；否则添加
        if "demo" in projects:
            storage.update(demo_project)
        else:
            storage.add(demo_project)
        print("Demo project initialized/updated")


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

