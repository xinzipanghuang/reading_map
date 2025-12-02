# 快速开始指南

## 前置要求

- Python 3.8+
- Node.js 16+ (推荐使用 npm/yarn/pnpm)

## 启动步骤

### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

后端将在 `http://localhost:8000` 启动。

### 2. 启动前端（新终端窗口）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### 3. 访问应用

打开浏览器访问: http://localhost:5173

## 使用启动脚本（Windows）

### 后端
```bash
cd backend
start.bat
```

### 前端
```bash
cd frontend
npm run dev
```

## 项目结构

```
.
├── frontend/              # 前端项目
│   ├── src/              # 源代码
│   ├── index.html        # HTML 入口
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite 配置
│
├── backend/               # 后端项目
│   ├── knowledge_dag/    # Python 包
│   ├── projects_data.json # 数据文件
│   ├── requirements.txt  # 后端依赖
│   └── run.py           # 启动脚本
│
└── README.md             # 项目文档
```

## 常见问题

### 后端启动失败

1. 检查 Python 版本: `python --version` (需要 3.8+)
2. 检查依赖安装: `pip list | grep fastapi`
3. 检查端口占用: 确保 8000 端口未被占用

### 前端启动失败

1. 检查 Node.js 版本: `node --version` (需要 16+)
2. 删除 node_modules 重新安装: `rm -rf node_modules && npm install`
3. 检查端口占用: 确保 5173 端口未被占用

### API 连接失败

1. 确保后端已启动
2. 检查后端地址: 默认 `http://localhost:8000`
3. 检查浏览器控制台错误信息

## 开发模式

### 后端热重载

后端默认不开启热重载，如需开启，修改 `backend/knowledge_dag/config.py`:

```python
reload: bool = True
```

或使用 uvicorn 直接启动:

```bash
cd backend
uvicorn knowledge_dag.main:app --reload
```

### 前端热重载

前端默认开启热模块替换 (HMR)，修改代码会自动刷新。

## 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/` 目录。

### 部署后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

或使用生产级 ASGI 服务器:

```bash
uvicorn knowledge_dag.main:app --host 0.0.0.0 --port 8000
```

