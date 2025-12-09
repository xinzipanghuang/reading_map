"""FastAPI 应用主入口"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from knowledge_dag.config import settings
from knowledge_dag.routes import router
from knowledge_dag.storage import storage
from knowledge_dag.models import Project, Chapter, Section, Node, Edge
from datetime import datetime
import traceback


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
    
    # 添加全局异常处理器，捕获验证错误并打印详细信息
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        print(f"\n{'='*60}")
        print(f"VALIDATION ERROR (422):")
        print(f"URL: {request.url}")
        print(f"Method: {request.method}")
        print(f"Path: {request.url.path}")
        try:
            body = await request.body()
            print(f"Request body: {body.decode('utf-8') if body else 'empty'}")
        except:
            print(f"Request body: (could not read)")
        print(f"Errors: {exc.errors()}")
        print(f"Error details:")
        for error in exc.errors():
            print(f"  - {error}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
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

