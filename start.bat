@echo off
chcp 65001 >nul
echo ========================================
echo    ReadMap - 知识图谱构建工具
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 启动后端服务 (FastAPI)...
start /b cmd /c "cd backend && C:\Users\zhangbingtao\.conda\envs\nn\python run.py"
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务 (Vite)...
echo.
echo ========================================
echo    服务运行中...
echo ========================================
echo.
echo 本地访问:
echo   后端地址: http://localhost:8000
echo   前端地址: http://localhost:5173
echo.
echo 局域网访问:
echo   后端地址: http://%COMPUTERNAME%:8000 (或使用本机 IP)
echo   前端地址: http://%COMPUTERNAME%:5173 (或使用本机 IP)
echo.
echo 提示: 
echo   - 按 Ctrl+C 可停止服务
echo   - 其他设备可通过局域网 IP 访问
echo   - 查看本机 IP: ipconfig
echo ========================================
echo.

cd frontend
npm run dev

