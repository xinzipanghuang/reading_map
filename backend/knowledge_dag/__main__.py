"""允许使用 python -m knowledge_dag 运行应用"""
from knowledge_dag.main import app
import uvicorn
from knowledge_dag.config import settings

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )

