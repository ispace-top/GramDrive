<div align="center">
  <img src="app/static/images/logo_word.png" alt="Gram Drive Logo" width="400"/>

  <p>
    <strong>将 Telegram 变成你的私人云存储</strong>
  </p>

  <p>
    <a href="https://github.com/ispace-top/GramDrive/releases"><img src="https://img.shields.io/github/v/release/ispace-top/GramDrive?color=blue" alt="Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python"></a>
    <a href="https://hub.docker.com/r/wapedkj/gramdrive"><img src="https://img.shields.io/docker/pulls/wapedkj/gramdrive" alt="Docker Pulls"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ispace-top/GramDrive" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg" alt="Platform"></a>
  </p>

  <p>
    中文 • <a href="README_EN.md">English</a>
  </p>
</div>

---

## 📖 项目简介

**Gram Drive** 是一个现代化的网页文件管理系统，利用 Telegram 作为无限云存储。基于 FastAPI 构建并优化了性能，它提供了直观的界面来管理、预览和分享存储在 Telegram 频道中的文件。

## ✨ 主要功能

### 🗂️ **文件管理**
- **多格式支持**：图片、视频、音频、文档等
- **智能分类**：按文件类型自动分类（图片/视频/音频/文档/其他）
- **高级搜索**：快速查找和过滤文件
- **批量操作**：多选、批量删除、批量复制链接
- **文件预览**：支持图片、视频、PDF 和文本文件预览，带加载状态

### 🖼️ **图床模式**
- **缩略图生成**：自动生成 3 种尺寸缩略图（150x150、300x300、600x600）
- **智能缓存**：服务端缓存，加载快 80%
- **多种格式**：支持复制 URL、Markdown 或 HTML 链接
- **网格视图**：美观的响应式网格布局，悬停效果

### ⬇️ **智能下载管理**
- **自动下载**：自动同步 Telegram 中的文件
- **有序存储**：按类型和日期保存文件（`/downloads/image/2026-01-22/photo.jpg`）
- **可配置过滤器**：文件类型、文件大小、下载位置
- **实时进度**：在线下载状态和进度跟踪
- **队列管理**：支持并发下载，可配置线程数

### 🎨 **现代化 UI/UX**
- **深色模式**：自动检测和手动切换
- **响应式设计**：适配桌面、平板和移动设备
- **紧凑上传**：节省空间的上传按钮设计
- **加载状态**：平滑的加载动画和视觉反馈

### 🔒 **安全与性能**
- **密码保护**：安全的登录系统
- **会话管理**：长时间不操作自动退出
- **连接池**：高性能 HTTP 客户端（500 并发连接）
- **冲突处理**：智能 Telegram Bot 冲突处理

### 📊 **统计仪表板**
- **存储分析**：总文件数、存储使用量、文件类型分布
- **上传趋势**：每日/每周上传图表
- **分类统计**：可视化文件分类统计

## 🚀 快速开始

### 前置条件

- **Docker & Docker Compose**（推荐）或 **Python 3.11+**
- **Telegram Bot Token**（[通过 @BotFather 创建](https://t.me/BotFather)）
- **Telegram 频道**（创建私人频道用于文件存储）

### 🐳 Docker 部署（推荐）

#### 快速开始（使用预构建镜像）

最简单的方式，无需本地构建：

1. **创建目录结构**
   ```bash
   mkdir -p ../GramDrive/data ../GramDrive/downloads
   cd ../GramDrive
   ```

2. **创建 `docker-compose.yml` 文件**
   ```yaml
   version: '3.8'
   services:
     gramdrive:
       image: wapedkj/gramdrive:latest
       container_name: gramdrive
       restart: unless-stopped
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
         - ./downloads:/app/downloads
       environment:
         - PYTHONUNBUFFERED=1
         - BOT_TOKEN=${BOT_TOKEN:-}
         - CHANNEL_NAME=${CHANNEL_NAME:-}
         - PASS_WORD=${PASS_WORD:-}
         - PICGO_API_KEY=${PICGO_API_KEY:-}
         - BASE_URL=localhost
       env_file:
         - .env
       healthcheck:
         test: ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s
   ```

3. **创建 `.env` 文件**（可选）
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **拉取镜像并启动应用**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **访问 Web 界面**
   ```
   http://localhost:8000
   ```

6. **初始配置**
   - 打开 Web 界面
   - 设置管理员密码
   - 在设置中配置 Bot Token 和频道名称
   - 点击"应用"启动机器人

#### 源代码部署（本地构建）

如果需要修改源代码或使用最新开发版本：

1. **克隆仓库**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
   ```

2. **创建目录结构**
   ```bash
   mkdir -p ../GramDrive/data ../GramDrive/downloads
   ```

3. **创建 `.env` 文件**（可选）
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **构建并启动应用**
   ```bash
   docker-compose up -d --build
   ```

5. **访问 Web 界面**
   ```
   http://localhost:8000
   ```

6. **初始配置**
   - 打开 Web 界面
   - 设置管理员密码
   - 在设置中配置 Bot Token 和频道名称
   - 点击"应用"启动机器人

### 🔧 手动安装

**前置条件：**
```bash
python --version  # 需要 3.11+
pip --version
```

**安装步骤：**

1. **克隆并设置**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的 Bot Token 和频道名称
   ```

4. **创建数据目录**
   ```bash
   mkdir -p data downloads
   ```

5. **运行应用**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **访问应用**
   ```
   http://localhost:8000
   ```

## ⚙️ 配置指南

### 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `BOT_TOKEN` | ✅ 是 | - | Telegram 机器人令牌（来自 @BotFather） |
| `CHANNEL_NAME` | ✅ 是 | - | 目标 Telegram 频道（@name 或 -1001234567890） |
| `PASS_WORD` | ❌ 否 | - | 管理员密码（留空表示无认证） |
| `PICGO_API_KEY` | ❌ 否 | - | PicGo/图床集成的 API 密钥 |
| `BASE_URL` | ❌ 否 | `localhost` | 生成分享链接的基础 URL |

### 自动下载配置

**在 Web 设置中：**

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| `AUTO_DOWNLOAD_ENABLED` | `True` | 启用自动下载 |
| `DOWNLOAD_DIR` | `/app/downloads` | 保存下载的目录 |
| `DOWNLOAD_FILE_TYPES` | `image,video` | 逗号分隔的文件类型 |
| `DOWNLOAD_MAX_SIZE` | `52428800`（50MB） | 最大下载文件大小（字节） |
| `DOWNLOAD_MIN_SIZE` | `0` | 最小下载文件大小（字节） |
| `DOWNLOAD_THREADS` | `3` | 并发下载数 |
| `DOWNLOAD_POLLING_INTERVAL` | `60` | 检查间隔（秒） |

**目录结构：**

自动下载的文件按类型和日期组织：
```
downloads/
├── image/
│   ├── 2026-01-22/
│   │   ├── photo_001.jpg
│   │   ├── photo_002.png
│   │   └── screenshot.png
│   └── 2026-01-21/
│       └── vacation.jpg
├── video/
│   ├── 2026-01-22/
│   │   └── meeting_recording.mp4
│   └── 2026-01-20/
│       └── tutorial.mkv
└── document/
    ├── 2026-01-22/
    │   └── contract.pdf
    └── 2026-01-15/
        └── presentation.pptx
```

## 📚 使用示例

### 🌐 Web 界面

1. **文件管理**
   - 点击文件预览（支持图片、视频、PDF）
   - 多选进行批量操作
   - 以多种格式复制文件链接（URL、Markdown、HTML）
   - 按文件类型自动分类

2. **图床模式**
   - 专为图片分享设计的界面
   - 3 种尺寸缩略图（小/中/大），服务端缓存
   - 一键复制到剪贴板
   - 使用短链接与朋友分享

3. **下载管理**
   - 配置自动下载过滤器（文件类型、大小）
   - 实时监测下载进度
   - 查看按类型和日期组织的下载文件

### 🔌 API 使用

**获取文件列表**
```bash
curl -X GET "http://localhost:8000/api/files" \
  -H "Cookie: tgstate_session=your_session_id"
```

**上传文件**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/file.jpg" \
  -H "Cookie: tgstate_session=your_session_id"
```

**使用 PicGo 上传**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@photo.jpg" \
  -H "x-api-key: your_api_key"
```

**下载文件**
```bash
curl "http://localhost:8000/d/AbC123" -o downloaded_file.jpg
```

**获取缩略图**
```bash
# 可用尺寸：small（150x150）、medium（300x300）、large（600x600）
curl "http://localhost:8000/api/thumbnail/file_id?size=medium" -o thumb.jpg
```

**删除文件**
```bash
curl -X DELETE "http://localhost:8000/api/files/file_id" \
  -H "Cookie: tgstate_session=your_session_id"
```

### 🖼️ PicGo 配置

添加到 PicGo 自定义上传器：

**PicGo 配置（PicGo > 插件 > Piclist > 配置）：**
```json
{
  "picBed": {
    "custom": {
      "show": true,
      "name": "Gram Drive",
      "url": "http://your-server:8000/d/$filename",
      "body": [
        {
          "key": "file",
          "type": "file",
          "required": true
        }
      ],
      "headers": [
        {
          "key": "x-api-key",
          "value": "your_api_key"
        }
      ],
      "customBody": "multipart/form-data",
      "httpPlugin": "request"
    }
  }
}
```

## 🐛 故障排除

### Bot 冲突错误
**错误：** `Conflict: terminated by other getUpdates request`

**原因：**
- 多个应用实例同时运行
- 旧的 Bot 实例未完全关闭
- 在开发和生产环境中同时运行

**解决方案：**
```bash
# 完全重启
docker-compose down
sleep 10
docker-compose up -d --build

# 或手动重启
pkill -f "uvicorn app"
sleep 5
uvicorn app.main:app --reload
```

### 下载服务不工作
**问题：** 自动下载无法启动文件

**检查清单：**
- ✅ 设置中 `AUTO_DOWNLOAD_ENABLED` 设为 `True`
- ✅ 已配置和应用 `BOT_TOKEN` 和 `CHANNEL_NAME`
- ✅ Bot 在设置中显示为"就绪"（绿色点）
- ✅ 检查日志：`docker logs gramdrive` 查找错误
- ✅ 目录存在：`/app/downloads`（或配置的 `DOWNLOAD_DIR`）

**修复方法：**
```bash
# 检查 Bot 状态日志
docker logs gramdrive | grep -i "bot\|download"

# 如果 Bot 失败，以新配置重启
docker-compose restart gramdrive
```

### 缩略图 API 返回 400
**问题：** 图片预览/缩略图无法加载

**解决方案：**
- 缩略图服务会自动检测缺失的 `mime_type` 并假定为图片类型
- 检查日志中的警告：`docker logs gramdrive | grep -i thumbnail`
- 清除缩略图缓存：`curl -X POST http://localhost:8000/api/thumbnail/clear-all`

### 连接池超时
**错误：** `All connections in the connection pool are occupied`

**原因：** 过多并发图片加载导致连接池耗尽

**解决方案（已优化）：**
- 连接池已增加到 500 最大连接数
- 缩略图在服务端缓存（无重复下载）
- 更新到最新版本：`docker-compose up -d --build`

## 📋 系统要求

| 组件 | 要求 | 备注 |
|------|------|------|
| Python | 3.11+ | 手动安装时需要 |
| Docker | 最新版 | 推荐用于部署 |
| 内存 | 512MB | 轻度使用最低配置 |
| 磁盘 | 可变 | 取决于存储文件数量 |
| 网络 | 稳定网络 | 用于 Telegram 连接 |

## 🗺️ 开发路线图

**v2.0.0**（当前版本）
- ✅ 文件管理和预览
- ✅ 图床模式
- ✅ 自动下载和组织
- ✅ 缩略图缓存
- ✅ 连接池优化
- ✅ Bot 冲突处理

**v2.1.0**（计划中）
- 📌 WebDAV 协议支持
- 📌 直接 Telegram 频道集成
- 📌 高级搜索和过滤
- 📌 有过期时间的文件分享
- 📌 多频道支持

**v2.2.0**（未来版本）
- 📌 S3 兼容 API
- 📌 FTP 服务器接口
- 📌 移动端应用（PWA）
- 📌 上传时视频转码
- 📌 评论和注释功能

## 🎉 致谢

本项目站在巨人的肩膀上。特别感谢：

- **[FastAPI](https://fastapi.tiangolo.com/)** - 现代、快速的 Web 框架
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** - Telegram Bot API 包装器
- **[Pillow](https://python-pillow.org/)** - 卓越的图片处理库
- **[httpx](https://www.python-httpx.org/)** - 优雅的异步 HTTP 客户端
- **[SQLite](https://www.sqlite.org/)** - 可靠的嵌入式数据库
- **[Uvicorn](https://www.uvicorn.org/)** - 闪电般快速的 ASGI 服务器
- **[Docker](https://www.docker.com/)** - 简化容器化
- **[Telegram](https://telegram.org/)** - 在安全平台上构建

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 详见 LICENSE 文件。

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开 Pull Request

## 💬 联系与支持

- **问题反馈：** [GitHub Issues](https://github.com/ispace-top/GramDrive/issues)
- **讨论区：** [GitHub Discussions](https://github.com/ispace-top/GramDrive/discussions)
- **邮件：** your-email@example.com

---

<div align="center">
  <p>
    <strong>Made with ❤️ for Telegram enthusiasts</strong><br>
    <a href="https://github.com/ispace-top/GramDrive">GitHub</a> •
    <a href="https://github.com/ispace-top/GramDrive/issues">Issues</a> •
    <a href="https://github.com/ispace-top/GramDrive/discussions">Discussions</a>
  </p>
</div>
