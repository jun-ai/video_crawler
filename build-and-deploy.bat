@echo off
chcp 65001 > nul
echo ========================================
echo   本地打包镜像脚本 (Windows)
echo ========================================
echo.

set PROJECT_ROOT=D:\PythonTools\PythonProject\video_crawler
set SERVER_USER=root
set SERVER_HOST=iZbp17q7glyoc8l9z0s3ylZ
set SERVER_PATH=/opt/english-learning

REM 1. 构建前端
echo [1/5] 构建前端...
cd /d %PROJECT_ROOT%\frontend
call npm run build
if errorlevel 1 (
    echo 前端构建失败!
    pause
    exit /b 1
)
echo 前端构建完成

REM 2. 打包后端镜像
echo [2/5] 打包后端镜像...
cd /d %PROJECT_ROOT%\backend
call docker build -t english-learning-backend:latest .
call docker save english-learning-backend:latest | gzip > %PROJECT_ROOT%\english-learning-backend.tar
echo 后端镜像打包完成

REM 3. 打包前端镜像
echo [3/5] 打包前端镜像...
cd /d %PROJECT_ROOT%\frontend
call docker build -t english-learning-frontend:latest .
call docker save english-learning-frontend:latest | gzip > %PROJECT_ROOT%\english-learning-frontend.tar
echo 前端镜像打包完成

REM 4. 上传到服务器
echo [4/5] 上传镜像到服务器...
echo 上传后端镜像...
scp %PROJECT_ROOT%\english-learning-backend.tar %SERVER_USER%@%SERVER_HOST%:%SERVER_PATH%\
echo 上传前端镜像...
scp %PROJECT_ROOT%\english-learning-frontend.tar %SERVER_USER%@%SERVER_HOST%:%SERVER_PATH%\
echo 镜像上传完成

echo.
echo ========================================
echo   完成!
echo ========================================
echo.
echo 请在服务器上执行:
echo   cd /opt/english-learning
echo   cp deploy/prod.env .env
echo   ./deploy-server.sh
echo.
pause