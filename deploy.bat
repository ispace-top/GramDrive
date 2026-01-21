@echo off
REM Gram Drive Docker 部署脚本 (Windows)
REM 使用说明：双击运行或在命令行执行 deploy.bat

echo ==========================================
echo   Gram Drive Docker 部署工具
echo ==========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker 未安装
    echo 请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否可用
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker Compose 不可用
    echo 请确保 Docker Desktop 正在运行
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过
echo.

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  警告: .env 文件不存在
    if exist .env.example (
        echo 正在从 .env.example 创建 .env 文件...
        copy .env.example .env >nul
        echo ✅ .env 文件已创建
        echo ⚠️  请编辑 .env 文件，配置你的 BOT_TOKEN 和 CHANNEL_NAME
        echo.
        set /p EDIT="是否现在打开 .env 文件编辑？(y/n) "
        if /i "%EDIT%"=="y" (
            notepad .env
        ) else (
            echo 请稍后手动编辑 .env 文件后再启动服务
            pause
            exit /b 0
        )
    ) else (
        echo ❌ 错误: .env.example 文件不存在
        pause
        exit /b 1
    )
)

echo ✅ .env 文件已准备好
echo.

REM 创建数据目录
if not exist data (
    echo 📁 创建数据目录...
    mkdir data
)

echo ✅ 数据目录准备完成
echo.

REM 验证配置
echo 🔍 验证 Docker Compose 配置...
docker compose config >nul 2>&1
if errorlevel 1 (
    echo ❌ 配置文件验证失败
    pause
    exit /b 1
)
echo ✅ 配置文件验证通过
echo.

REM 询问是否继续
echo 准备执行部署操作：
echo   1. 构建 Docker 镜像
echo   2. 启动容器服务
echo.
set /p CONTINUE="是否继续？(y/n) "
if /i not "%CONTINUE%"=="y" (
    echo 部署已取消
    pause
    exit /b 0
)

REM 构建并启动
echo.
echo 🚀 开始构建和部署...
echo ==========================================
docker compose up -d --build

echo.
echo ==========================================
echo ✅ 部署完成！
echo ==========================================
echo.
echo 📊 服务状态：
docker compose ps
echo.
echo 🌐 访问地址: http://localhost:8000
echo.
echo 📝 常用命令：
echo   查看日志:     docker compose logs -f
echo   停止服务:     docker compose down
echo   重启服务:     docker compose restart
echo   查看状态:     docker compose ps
echo.
echo 💡 提示: 使用 'docker compose logs -f' 查看实时日志
echo.
pause
