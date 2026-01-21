# 🚀 Docker 部署快速指南

## ✅ 已完成的配置优化

1. **Docker Compose 配置** (`docker-compose.yml`)
   - ✅ 移除了硬编码的数据卷路径
   - ✅ 使用本地相对路径 `./data`（更通用）
   - ✅ 添加了环境变量配置
   - ✅ 添加了健康检查
   - ✅ 添加了网络配置
   - ✅ 移除了过时的 `version` 字段

2. **Dockerfile 优化**
   - ✅ 添加了 curl（用于健康检查）
   - ✅ 优化了镜像大小（清理 apt 缓存）

3. **新增文件**
   - ✅ `.dockerignore` - 优化构建速度和镜像大小
   - ✅ `deploy.sh` - Linux/macOS 一键部署脚本
   - ✅ `deploy.bat` - Windows 一键部署脚本
   - ✅ `DOCKER_DEPLOY.md` - 详细部署文档
   - ✅ `data/` 目录 - 数据持久化目录

---

## 🎯 一键部署（推荐）

### Windows 用户
```cmd
# 双击运行或在命令行执行
deploy.bat
```

### Linux/macOS 用户
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📝 手动部署

### 步骤 1: 准备环境变量

```bash
# 如果没有 .env 文件，从模板创建
cp .env.example .env

# 编辑 .env 文件，填写必要配置
# 必填项：BOT_TOKEN, CHANNEL_NAME
# 可选项：PASS_WORD, PICGO_API_KEY, BASE_URL
```

### 步骤 2: 验证配置

```bash
# 验证 docker-compose 配置
docker compose config
```

### 步骤 3: 构建并启动

```bash
# 一键构建和启动
docker compose up -d --build

# 查看启动日志
docker compose logs -f
```

---

## 🔧 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 停止并删除数据（慎用！）
docker compose down -v

# 重新构建镜像（无缓存）
docker compose build --no-cache

# 进入容器终端
docker compose exec gramdrive bash

# 查看健康状态
docker inspect --format='{{json .State.Health}}' gramdrive | jq
```

---

## 🌐 访问服务

服务启动后，访问：**http://localhost:8000**

如果修改了端口映射，请使用相应的端口号。

---

## 📊 健康检查

服务包含自动健康检查：
- **检查间隔**: 30秒
- **超时时间**: 10秒
- **重试次数**: 3次
- **启动等待**: 40秒

查看健康状态：
```bash
docker compose ps
# 或
docker inspect gramdrive | grep -A 10 Health
```

---

## 🗂️ 数据持久化

数据存储在 `./data` 目录，包括：
- SQLite 数据库（`tgstate.db`）
- 下载的文件
- 会话数据

**备份数据**：
```bash
# 停止服务
docker compose down

# 备份数据目录
cp -r data data_backup_$(date +%Y%m%d)

# 重启服务
docker compose up -d
```

---

## 🐛 故障排查

### 问题 1: 容器无法启动
```bash
# 查看详细错误日志
docker compose logs gramdrive

# 检查配置
docker compose config
```

### 问题 2: 端口被占用
修改 `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # 改用 8001 端口
```

### 问题 3: 权限问题
```bash
# Linux/macOS
sudo chown -R $(whoami):$(whoami) data

# Windows (以管理员运行)
icacls data /grant Users:F /T
```

### 问题 4: 环境变量未生效
```bash
# 检查 .env 文件是否存在
ls -la .env

# 重新加载环境变量
docker compose down
docker compose up -d
```

### 问题 5: 镜像构建失败
```bash
# 清理缓存重新构建
docker compose build --no-cache

# 检查 Docker 磁盘空间
docker system df

# 清理未使用的镜像
docker system prune -a
```

---

## 🔄 更新服务

### 方法 1: 拉取新代码后重新构建
```bash
git pull
docker compose up -d --build
```

### 方法 2: 完全重建
```bash
# 停止并删除容器
docker compose down

# 重新构建镜像
docker compose build --no-cache

# 启动服务
docker compose up -d
```

---

## 📦 完整清理

```bash
# 停止并删除所有容器、网络、卷
docker compose down -v

# 删除镜像
docker rmi tgstate-python-gramdrive

# 清理系统（慎用！）
docker system prune -a --volumes
```

---

## ✅ 部署检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] `.env` 文件已配置（BOT_TOKEN, CHANNEL_NAME）
- [ ] `data` 目录存在且有写权限
- [ ] 端口 8000 未被占用（或已修改配置）
- [ ] 防火墙允许 8000 端口（如需外部访问）
- [ ] 已运行 `docker compose config` 验证配置

---

## 🎉 部署成功！

如果一切正常，你应该能看到：

```bash
$ docker compose ps
NAME        IMAGE                    STATUS         PORTS
gramdrive   tgstate-python-gramdrive Up (healthy)   0.0.0.0:8000->8000/tcp
```

访问 http://localhost:8000 开始使用 Gram Drive！

---

## 📚 更多信息

- **详细文档**: 查看 `DOCKER_DEPLOY.md`
- **项目文档**: 查看 `README.md`
- **架构说明**: 查看 `CLAUDE.md`
