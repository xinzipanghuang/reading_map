#!/usr/bin/env python3
"""启动脚本"""
import uvicorn
from knowledge_dag.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "knowledge_dag.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )

