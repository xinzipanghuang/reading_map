// Electron main process for both development and production.
// Dev:   连接 Vite 开发服务器 + 你手动启动的 FastAPI
// Prod:  加载打包后的 dist/index.html，并自动拉起 FastAPI 后端

const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let backendProcess = null;

function isDev() {
  return process.env.ELECTRON_DEV === "true";
}

function startBackend() {
  // 只在打包/生产环境自动启动后端
  if (isDev()) {
    return;
  }

  // 假设用户机器上已安装 Python，并且在项目根目录运行打包好的应用
  // 后端路径：../backend/run.py
  const backendScript = path.join(__dirname, "..", "backend", "run.py");

  backendProcess = spawn("python", [backendScript], {
    cwd: path.join(__dirname, "..", "backend"),
    stdio: "inherit",
    shell: true,
  });

  backendProcess.on("exit", (code) => {
    console.log("Backend process exited with code", code);
  });
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev()) {
    // 开发模式：连接本地 Vite 服务器
    win.loadURL("http://localhost:5173");
  } else {
    // 生产模式：加载打包后的前端
    const indexPath = path.join(__dirname, "dist", "index.html");
    win.loadFile(indexPath);
  }
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopBackend();
});

