# Docker Compose 快速部署脚本使用说明

## 前置要求

1. 安装 Docker 和 Docker Compose
2. 配置 .env 文件（参考 .env.example）

## 一键部署

```bash
# 1. 构建并启动服务（后台运行）
docker-compose up -d --build

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down

# 4. 完全清理（包括数据卷）
docker-compose down -v
```

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec gramdrive bash

# 查看实时日志
docker-compose logs -f gramdrive

# 仅重新构建镜像
docker-compose build

# 强制重新构建（无缓存）
docker-compose build --no-cache
```

## 数据持久化

数据存储在 `./data` 目录中，包括：
- SQLite 数据库
- 下载的文件
- 会话数据

## 环境变量配置

确保 `.env` 文件包含以下必要配置：

```env
BOT_TOKEN=your_telegram_bot_token
CHANNEL_NAME=@your_channel
PASS_WORD=your_password
BASE_URL=http://localhost:8000
```

## 访问服务

服务启动后，访问：http://localhost:8000

## 健康检查

服务包含自动健康检查，每30秒检查一次。
查看健康状态：

```bash
docker inspect --format='{{json .State.Health}}' gramdrive
```

## 故障排查

### 容器无法启动
```bash
# 查看详细错误日志
docker-compose logs gramdrive

# 检查配置文件
docker-compose config
```

### 端口被占用
修改 docker-compose.yml 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 改用 8001 端口
```

### 数据权限问题
```bash
# 修复数据目录权限
chmod 755 data
```
