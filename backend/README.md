# 知识图谱构建器后端 (Knowledge DAG Builder Backend)

使用 FastAPI + Pydantic 构建的 RESTful API 后端服务。

## 项目结构

```
src/knowledge_dag/
├── __init__.py          # 包初始化
├── __main__.py          # 模块入口（支持 python -m knowledge_dag）
├── main.py              # FastAPI 应用主入口
├── config.py            # 配置管理（使用 Pydantic Settings）
├── models.py            # Pydantic 数据模型
├── storage.py           # 数据存储层
├── services.py          # 业务逻辑服务层
└── routes.py            # API 路由
```

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **NetworkX**: 图算法和 DAG 检测
- **Uvicorn**: ASGI 服务器

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者使用 pip 安装为可编辑包：

```bash
pip install -e .
```

### 2. 配置环境变量（可选）

创建 `.env` 文件：

```env
# API 配置
API_TITLE=Knowledge DAG Builder API
API_VERSION=1.0.0

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS 配置
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# 数据存储
DATA_FILE=projects_data.json
```

## 运行

### 方式 1: 使用 run.py

```bash
python run.py
```

### 方式 2: 使用 uvicorn 直接运行

```bash
uvicorn knowledge_dag.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方式 3: 作为模块运行

```bash
python -m knowledge_dag
```

### 方式 4: 使用启动脚本

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主要特性

### 1. Pydantic 数据验证

所有请求和响应都使用 Pydantic 模型进行验证：

- 自动类型转换
- 数据验证（长度、格式等）
- 清晰的错误消息
- 自动生成 API 文档

### 2. 分层架构

- **Models**: 数据模型定义
- **Storage**: 数据持久化层
- **Services**: 业务逻辑层
- **Routes**: API 路由层

### 3. 配置管理

使用 `pydantic-settings` 进行配置管理：

- 支持环境变量
- 类型安全
- 默认值支持
- 配置文件支持

### 4. 错误处理

统一的错误处理机制：

- HTTP 异常
- 详细的错误消息
- 数据验证错误

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
black src/
```

### 代码检查

```bash
ruff check src/
```

## 数据模型

### Project (项目)
- `id`: 项目唯一标识
- `name`: 项目名称
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `chapters`: 章节列表
- `edges`: 边列表

### Chapter (章节)
- `id`: 章节唯一标识
- `name`: 章节名称
- `sections`: 部分列表

### Section (部分)
- `id`: 部分唯一标识
- `name`: 部分名称
- `nodes`: 节点列表

### Node (节点)
- `id`: 节点唯一标识
- `name`: 节点名称
- `content`: 节点内容/笔记

## API 端点

### 项目管理
- `GET /projects` - 获取所有项目
- `POST /projects` - 创建项目
- `GET /projects/{project_id}` - 获取项目详情
- `DELETE /projects/{project_id}` - 删除项目

### 章节管理
- `POST /projects/{project_id}/chapters` - 添加章节
- `DELETE /projects/{project_id}/chapters/{chapter_id}` - 删除章节

### 部分管理
- `POST /projects/{project_id}/sections` - 添加部分
- `DELETE /projects/{project_id}/sections/{section_id}` - 删除部分

### 节点管理
- `POST /projects/{project_id}/nodes` - 添加节点
- `PUT /projects/{project_id}/nodes/{node_id}` - 更新节点
- `DELETE /projects/{project_id}/nodes/{node_id}` - 删除节点

### 图谱操作
- `POST /projects/{project_id}/edges` - 创建连接
- `DELETE /projects/{project_id}/edges` - 删除连接
- `GET /projects/{project_id}/graph_analysis` - 分析图谱
- `GET /projects/{project_id}/nodes/{node_id}/location` - 获取节点位置

## 许可证

MIT License

