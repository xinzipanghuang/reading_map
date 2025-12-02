# 知识图谱构建器 (Knowledge DAG Builder)

一个用于构建和管理知识依赖关系的 Web 应用，支持读书笔记和知识管理。

## 项目结构

```
.
├── frontend/          # 前端项目 (Vue 3 + Vite)
├── backend/           # 后端项目 (FastAPI + Pydantic)
└── README.md         # 项目说明
```

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端服务将在 `http://localhost:8000` 启动。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 启动。

## 详细文档

- **前端文档**: 查看 [frontend/README.md](frontend/README.md)
- **后端文档**: 查看 [backend/README.md](backend/README.md)

## 功能特性

- ✅ **项目管理**: 创建、删除、切换多个项目
- ✅ **层级结构**: 项目 → 章节 → 部分 → 知识节点
- ✅ **知识节点管理**: 在每个部分中添加任意多个知识节点
- ✅ **依赖关系**: 在不同章节/部分之间创建节点连接
- ✅ **DAG 可视化**: 自动检测环，确保有向无环图
- ✅ **节点选择**: 点击节点查看其完整的 DAG 路径（祖先和后代）
- ✅ **路径高亮**: 自动高亮显示选中节点的相关路径

## 技术栈

### 前端
- Vue 3 + Composition API
- Vite
- Tailwind CSS
- Vis.js (图谱可视化)
- Axios

### 后端
- FastAPI
- Pydantic (数据验证)
- NetworkX (图算法)
- Uvicorn

## 开发

### 后端开发

```bash
cd backend
pip install -e ".[dev]"  # 安装开发依赖
python run.py             # 启动开发服务器
```

### 前端开发

```bash
cd frontend
npm install
npm run dev               # 启动开发服务器
npm run build            # 构建生产版本
```

## API 文档

启动后端后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 许可证

MIT License
