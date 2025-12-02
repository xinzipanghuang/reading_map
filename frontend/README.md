# 知识图谱构建器 - 前端

Vue 3 + Vite + Tailwind CSS 构建的前端应用。

## 安装

### 配置代理（可选）

如果需要使用代理，有以下几种方式：

#### 方式 1: 使用 .npmrc 文件（推荐）

编辑 `frontend/.npmrc` 文件，取消注释并设置你的代理：

```ini
proxy=http://127.0.0.1:7890
https-proxy=http://127.0.0.1:7890
```

#### 方式 2: 使用命令行参数

```bash
npm install --proxy=http://127.0.0.1:7890 --https-proxy=http://127.0.0.1:7890
```

#### 方式 3: 使用环境变量

**Windows (CMD):**
```cmd
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
npm install
```

**Windows (PowerShell):**
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
npm install
```

**Linux/Mac:**
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
npm install
```

### 使用国内镜像源（推荐）

如果网络较慢，可以使用国内镜像源加速。`.npmrc` 文件已默认配置为淘宝镜像：

```ini
registry=https://registry.npmmirror.com
```

如果需要切换回官方源，修改 `.npmrc`：

```ini
registry=https://registry.npmjs.org
```

### 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

## 开发

```bash
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 启动。

## 构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── App.vue        # 主组件
│   ├── main.js        # 应用入口
│   ├── style.css      # 全局样式
│   └── api.js         # API 封装
├── index.html         # HTML 入口
├── package.json       # 依赖配置
├── vite.config.js     # Vite 配置
├── tailwind.config.js # Tailwind 配置
├── postcss.config.js  # PostCSS 配置
└── .npmrc            # npm 配置文件
```

## 环境变量

创建 `.env` 文件（可选）：

```env
VITE_API_URL=http://localhost:8000
```

## 技术栈

- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Vis.js**: 网络图可视化库
- **Axios**: HTTP 客户端

## 常见问题

### npm install 失败

1. **检查网络连接**
   - 确保可以访问 npm 仓库
   - 如果使用代理，检查代理配置

2. **清除缓存**
   ```bash
   npm cache clean --force
   ```

3. **删除 node_modules 重新安装**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **使用国内镜像**
   - 已默认配置淘宝镜像
   - 或使用 cnpm: `npm install -g cnpm --registry=https://registry.npmmirror.com`

### 代理设置不生效

1. 检查 `.npmrc` 文件位置（应在 `frontend/` 目录下）
2. 检查代理地址和端口是否正确
3. 尝试使用命令行参数方式设置代理
4. 检查防火墙设置
