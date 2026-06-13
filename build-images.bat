@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   英语学习平台 - 镜像构建打包脚本
echo ========================================
echo.

cd /d %~dp0

:: 设置镜像名称和版本
set BACKEND_IMAGE=english-learning-backend
set FRONTEND_IMAGE=english-learning-frontend
set VERSION=latest

:: 记录开始时间
set START_TIME=%time%

echo [信息] 镜像名称:
echo   - 后端: %BACKEND_IMAGE%:%VERSION%
echo   - 前端: %FRONTEND_IMAGE%:%VERSION%
echo.

:: 检查 Docker 是否运行
echo [1/6] 检查 Docker 环境...
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)
echo [完成] Docker 环境正常
echo.

:: 清理旧的 tar 文件
echo [2/6] 清理旧的镜像文件...
if exist "%BACKEND_IMAGE%.tar" (
    del /f /q "%BACKEND_IMAGE%.tar"
    echo   - 已删除 %BACKEND_IMAGE%.tar
)
if exist "%FRONTEND_IMAGE%.tar" (
    del /f /q "%FRONTEND_IMAGE%.tar"
    echo   - 已删除 %FRONTEND_IMAGE%.tar
)
echo [完成] 清理完成
echo.

:: 构建后端镜像
echo [3/6] 构建后端镜像...
echo.
docker build -t %BACKEND_IMAGE%:%VERSION% ./backend
if errorlevel 1 (
    echo [错误] 后端镜像构建失败
    pause
    exit /b 1
)
echo [完成] 后端镜像构建成功
echo.

:: 构建前端镜像
echo [4/6] 构建前端镜像...
echo.
docker build -t %FRONTEND_IMAGE%:%VERSION% ./frontend
if errorlevel 1 (
    echo [错误] 前端镜像构建失败
    pause
    exit /b 1
)
echo [完成] 前端镜像构建成功
echo.

:: 导出后端镜像
echo [5/6] 导出后端镜像文件...
docker save -o %BACKEND_IMAGE%.tar %BACKEND_IMAGE%:%VERSION%
if errorlevel 1 (
    echo [错误] 后端镜像导出失败
    pause
    exit /b 1
)
echo [完成] 后端镜像已导出: %BACKEND_IMAGE%.tar
echo.

:: 导出前端镜像
echo [6/6] 导出前端镜像文件...
docker save -o %FRONTEND_IMAGE%.tar %FRONTEND_IMAGE%:%VERSION%
if errorlevel 1 (
    echo [错误] 前端镜像导出失败
    pause
    exit /b 1
)
echo [完成] 前端镜像已导出: %FRONTEND_IMAGE%.tar
echo.

:: 显示结果
echo ========================================
echo   构建打包完成！
echo ========================================
echo.

:: 显示文件大小
for %%A in (%BACKEND_IMAGE%.tar) do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo   %BACKEND_IMAGE%.tar: !SIZE_MB! MB
)
for %%A in (%FRONTEND_IMAGE%.tar) do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo   %FRONTEND_IMAGE%.tar: !SIZE_MB! MB
)

echo.
echo   开始时间: %START_TIME%
echo   结束时间: %time%
echo.
echo ========================================
echo   后续步骤:
echo ----------------------------------------
echo   1. 上传文件到服务器:
echo      scp %BACKEND_IMAGE%.tar %FRONTEND_IMAGE%.tar docker-compose.yml .env root@server:/opt/english-learning/
echo.
echo   2. 服务器执行部署:
echo      cd /opt/english-learning
echo      docker load -i %BACKEND_IMAGE%.tar
echo      docker load -i %FRONTEND_IMAGE%.tar
echo      docker-compose up -d
echo ========================================
echo.

pause
