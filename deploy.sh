#!/bin/bash

# Gram Drive Docker 部署脚本
# 使用说明：chmod +x deploy.sh && ./deploy.sh

set -e

echo "=========================================="
echo "  Gram Drive Docker 部署工具"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否可用
if ! docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose 不可用"
    echo "请确保安装了 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "正在从 .env.example 创建 .env 文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env 文件已创建"
        echo "⚠️  请编辑 .env 文件，配置你的 BOT_TOKEN 和 CHANNEL_NAME"
        echo ""
        read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-vi} .env
        else
            echo "请稍后手动编辑 .env 文件后再启动服务"
            exit 0
        fi
    else
        echo "❌ 错误: .env.example 文件不存在"
        exit 1
    fi
fi

echo "✅ .env 文件已准备好"
echo ""

# 创建数据目录
if [ ! -d "data" ]; then
    echo "📁 创建数据目录..."
    mkdir -p data
fi

echo "✅ 数据目录准备完成"
echo ""

# 验证配置
echo "🔍 验证 Docker Compose 配置..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ 配置文件验证通过"
else
    echo "❌ 配置文件验证失败"
    exit 1
fi
echo ""

# 询问是否继续
echo "准备执行部署操作："
echo "  1. 构建 Docker 镜像"
echo "  2. 启动容器服务"
echo ""
read -p "是否继续？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 0
fi

# 构建并启动
echo ""
echo "🚀 开始构建和部署..."
echo "=========================================="
docker compose up -d --build

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📊 服务状态："
docker compose ps
echo ""
echo "🌐 访问地址: http://localhost:8000"
echo ""
echo "📝 常用命令："
echo "  查看日志:     docker compose logs -f"
echo "  停止服务:     docker compose down"
echo "  重启服务:     docker compose restart"
echo "  查看状态:     docker compose ps"
echo ""
echo "💡 提示: 使用 'docker compose logs -f' 查看实时日志"
