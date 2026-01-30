<div align="center">
  <img src="app/static/images/logo_word.png" alt="Gram Drive Logo" width="450"/>

  <p>
    <strong>将 Telegram 化身为企业级私有云存储</strong>
  </p>

  <p>
    <a href="https://github.com/ispace-top/GramDrive/releases"><img src="https://img.shields.io/github/v/release/ispace-top/GramDrive?color=blue&style=flat-square" alt="Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.11+-green.svg?style=flat-square" alt="Python"></a>
    <a href="https://hub.docker.com/r/wapedkj/gramdrive"><img src="https://img.shields.io/docker/pulls/wapedkj/gramdrive?style=flat-square" alt="Docker Pulls"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ispace-top/GramDrive?style=flat-square" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg?style=flat-square" alt="Platform"></a>
  </p>

  <p>
    中文 • <a href="README.en.md">English</a>
  </p>
</div>

---

## 🌟 项目简介

**Gram Drive** 是一款基于 **FastAPI** 构建的现代化文件管理系统，它巧妙地将 **Telegram 频道**转化为无限容量的私有云存储平台。通过优雅的 Web 界面，您可以轻松管理、预览、分享文件，同时享受 Telegram 带来的无限存储空间和全球 CDN 加速。

### 💡 为什么选择 Gram Drive？

- 🎯 **零存储成本** - 利用 Telegram 的无限免费存储空间
- 🚀 **全球 CDN 加速** - Telegram 的全球边缘节点确保极速访问
- 🔒 **企业级安全** - 端到端加密，私有频道保障数据安全
- 💻 **专业架构** - 异步高并发、智能缓存、队列管理
- 🎨 **现代化设计** - 响应式 UI、深色模式、流畅交互
- 🔧 **一键部署** - Docker 容器化，开箱即用

---

## ✨ 核心功能

### 📁 智能文件管理
- **多格式支持** - 图片、视频、音频、文档、压缩包等所有格式
- **自动分类** - 智能识别文件类型并自动归类（图片/视频/音频/文档/其他）
- **高级搜索与过滤** - 快速定位目标文件，支持文件名、类型、日期筛选
- **批量操作** - 多选文件进行批量删除、批量复制链接，高效管理
- **即时预览** - 支持图片、视频、音频、PDF、文本文件在线预览
- **大文件分块** - 自动处理超大文件（≥19.5MB），透明分块上传/下载
- **短链分享** - 生成简洁的短链接（`/d/AbC123`），方便分享

### 🖼️ 专业图床服务
- **多尺寸缩略图** - 自动生成三种规格缩略图（150x/300x/600x），节省带宽
- **智能缓存策略** - 服务端本地缓存，优先使用本地文件，响应速度提升 80%+
- **多格式输出** - 一键复制 URL、Markdown、HTML 格式链接
- **响应式网格** - 美观的瀑布流布局，完美适配各种屏幕
- **PicGo 集成** - 支持 PicGo 客户端直接上传，无缝集成工作流

### ⬇️ 自动下载引擎
- **智能同步** - 自动检测 Telegram 频道新文件并下载到本地
- **有序存储** - 按类型和日期组织目录（`downloads/image/2026-01-22/photo.jpg`）
- **灵活过滤** - 配置文件类型、大小范围、下载目录等参数
- **队列管理** - 支持并发下载，可配置线程数，避免阻塞
- **实时进度** - SSE 实时推送下载状态和进度，随时掌控
- **断点续传** - 支持大文件分块下载，自动重试失败任务
- **超长超时** - 优化网络配置，支持 2GB+ 大视频文件下载（60 分钟超时）

### 📊 数据统计看板
- **存储分析** - 实时统计文件数量、总存储量、各类型占比
- **上传趋势** - 可视化每日/每周上传量变化曲线
- **类型分布** - 饼图展示文件类型分布，一目了然
- **性能指标** - Bot 状态、下载队列、系统健康度监控

### 🎨 现代化界面
- **自适应主题** - 自动检测系统主题，支持亮色/暗色模式手动切换
- **响应式设计** - 完美适配桌面、平板、手机，流畅的移动端体验
- **流畅动画** - 精心设计的加载动画和过渡效果，提升用户体验
- **紧凑布局** - 优化空间利用，减少视觉干扰，专注内容本身

### 🔐 安全与性能
- **会话管理** - 基于 Cookie 的安全会话机制，自动过期保护
- **API 密钥** - 支持 PicGo API Key 认证，双重认证体系
- **高并发连接池** - 500 并发 HTTP 连接，支持高负载场景
- **异步架构** - 基于 asyncio 的全异步设计，充分利用系统资源
- **智能冲突处理** - 自动检测并恢复 Telegram Bot 冲突
- **版本管理** - 完整的版本追踪和 GitHub Release 自动化发布

---

## 🏗️ 技术架构

### 核心技术栈

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **FastAPI** | 0.110+ | 现代异步 Web 框架 |
| **Python** | 3.11+ | 主要开发语言 |
| **python-telegram-bot** | 20.0+ | Telegram Bot API 封装 |
| **httpx** | Latest | 高性能异步 HTTP 客户端 |
| **SQLite** | 3.x | 轻量级嵌入式数据库 |
| **Uvicorn** | Latest | 高性能 ASGI 服务器 |
| **Pillow** | Latest | 图像处理引擎 |
| **Docker** | Latest | 容器化部署 |

### 关键设计模式

#### 1️⃣ **复合文件 ID 系统**
- Telegram 的 `file_id` 在不同 Bot 实例间会失效
- 创新使用 `{message_id}:{file_id}` 复合格式存储
- Message ID 在频道内永久有效，确保文件可靠访问和删除

#### 2️⃣ **智能分块机制**
- 文件 ≥19.5MB 自动分块（Telegram 20MB 下载限制）
- 生成 `.manifest` 清单文件记录分块信息
- 下载时透明拼接，删除时并发清理所有分块

#### 3️⃣ **事件驱动架构**
- 基于 `BroadcastEventBus` 的发布/订阅模式
- 文件变更实时广播到所有 SSE 订阅客户端
- 零延迟 UI 更新，极致的实时体验

#### 4️⃣ **分层配置系统**
- 优先级：数据库配置 > 环境变量 > 默认值
- 运行时动态修改配置，无需重启服务
- 敏感信息加密存储，安全可靠

#### 5️⃣ **本地缓存优化**
- 缩略图优先使用本地已下载文件生成
- 避免重复请求 Telegram API，节省带宽
- 响应速度提升 80%+，用户体验显著改善

---

## 🚀 快速开始

### 前置条件

- ✅ **Docker & Docker Compose**（推荐）或 **Python 3.11+**
- ✅ **Telegram Bot Token** - [通过 @BotFather 创建](https://t.me/BotFather)
- ✅ **Telegram 私有频道** - 创建一个私有频道用于文件存储

### 🐳 Docker 部署（推荐）

#### 方式一：使用预构建镜像（最快）

1. **创建项目目录**
   ```bash
   mkdir -p GramDrive/{data,downloads}
   cd GramDrive
   ```

2. **创建 `docker-compose.yml`**
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
         - BASE_URL=${BASE_URL:-http://localhost:8000}
       env_file:
         - .env
       healthcheck:
         test: ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s
   ```

3. **创建 `.env` 配置文件**（可选，也可在 Web 界面配置）
   ```bash
   cat > .env << 'EOF'
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key_for_picgo
   BASE_URL=http://localhost:8000
   EOF
   ```

4. **启动服务**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **访问 Web 界面**
   ```
   🌐 http://localhost:8000
   ```

6. **首次配置**
   - 打开浏览器访问 http://localhost:8000
   - 设置管理员密码（首次访问会自动跳转）
   - 进入"系统设置"页面配置 Bot Token 和频道名称
   - 点击"验证并应用"启动服务

#### 方式二：从源码构建

```bash
# 克隆仓库
git clone https://github.com/ispace-top/GramDrive.git
cd GramDrive

# 创建数据目录
mkdir -p data downloads

# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

### 💻 手动安装

**适合开发者或需要自定义的场景**

1. **环境准备**
   ```bash
   # 检查 Python 版本（需要 3.11+）
   python --version

   # 克隆仓库
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive

   # 创建虚拟环境
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
   # 复制示例配置
   cp .env.example .env

   # 编辑 .env 文件填入你的配置
   nano .env  # 或使用其他编辑器
   ```

4. **初始化数据目录**
   ```bash
   mkdir -p data downloads
   ```

5. **启动服务**
   ```bash
   # 开发模式（带热重载）
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # 生产模式
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

6. **访问应用**
   ```
   🌐 http://localhost:8000
   ```

---

## ⚙️ 配置指南

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|:----:|--------|------|
| `BOT_TOKEN` | ✅ | - | Telegram Bot Token（从 @BotFather 获取） |
| `CHANNEL_NAME` | ✅ | - | Telegram 频道标识（@channelname 或 -1001234567890） |
| `PASS_WORD` | ❌ | - | 管理员密码（留空表示无密码保护） |
| `PICGO_API_KEY` | ❌ | - | PicGo 上传 API 密钥（用于第三方工具集成） |
| `BASE_URL` | ❌ | `http://localhost:8000` | 生成分享链接的基础 URL |

### 自动下载配置

可在 Web 界面"下载管理"页面配置以下参数：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `AUTO_DOWNLOAD_ENABLED` | `True` | 是否启用自动下载 |
| `DOWNLOAD_DIR` | `/app/downloads` | 下载文件保存目录 |
| `DOWNLOAD_FILE_TYPES` | `image,video` | 下载的文件类型（逗号分隔） |
| `DOWNLOAD_MAX_SIZE` | `52428800` (50MB) | 单文件最大下载大小（字节） |
| `DOWNLOAD_MIN_SIZE` | `0` | 单文件最小下载大小（字节） |
| `DOWNLOAD_THREADS` | `3` | 并发下载线程数 |
| `DOWNLOAD_POLLING_INTERVAL` | `60` | 轮询检查间隔（秒） |

**目录结构示例：**

```
downloads/
├── image/
│   ├── 2026-01-30/
│   │   ├── photo_001.jpg
│   │   ├── photo_002.png
│   │   └── screenshot.webp
│   └── 2026-01-29/
│       └── vacation_photo.jpg
├── video/
│   ├── 2026-01-30/
│   │   └── meeting_recording.mp4
│   └── 2026-01-28/
│       └── tutorial_video.mkv
├── audio/
│   └── 2026-01-30/
│       └── podcast_episode.mp3
└── document/
    ├── 2026-01-30/
    │   └── contract_signed.pdf
    └── 2026-01-25/
        └── presentation.pptx
```

---

## 📚 使用指南

### 🌐 Web 界面操作

#### 1. 文件管理
- **上传文件** - 点击右上角"上传"按钮，支持拖拽上传
- **查看文件** - 点击文件卡片预览（支持图片、视频、音频、PDF、文本）
- **搜索文件** - 使用搜索框快速定位文件
- **分类筛选** - 点击类型标签过滤（全部/图片/视频/音频/文档/其他）
- **批量操作** - 勾选多个文件后，批量删除或复制链接
- **复制链接** - 点击"复制链接"按钮，选择格式（URL/Markdown/HTML）

#### 2. 图床模式
- **查看图片** - 自动生成缩略图，网格展示所有图片
- **复制链接** - 点击图片卡片上的"复制"按钮
- **选择尺寸** - 复制时可选择原图或不同尺寸的缩略图链接
- **快速分享** - 使用短链接 `/d/AbC123` 方便分享

#### 3. 下载管理
- **配置规则** - 点击"设置"按钮配置自动下载过滤器
- **查看进度** - 实时查看正在下载的文件和进度
- **浏览文件** - 查看已下载的本地文件，按日期和类型组织

#### 4. 数据统计
- **存储概览** - 查看总文件数、存储使用量
- **类型分布** - 饼图展示各类型文件占比
- **上传趋势** - 折线图展示上传量变化

#### 5. 系统设置
- **Bot 配置** - 配置和验证 Telegram Bot Token
- **频道配置** - 设置 Telegram 存储频道
- **密码管理** - 修改管理员密码
- **API 密钥** - 配置 PicGo API Key
- **基础 URL** - 设置分享链接的域名

### 🔌 API 接口

#### 文件操作 API

**获取文件列表**
```bash
curl -X GET "http://localhost:8000/api/files" \
  -H "Cookie: tgstate_session=your_session_id"
```

**上传文件（Web 认证）**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/file.jpg" \
  -H "Cookie: tgstate_session=your_session_id"
```

**上传文件（API Key 认证）**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@photo.jpg" \
  -H "x-api-key: your_picgo_api_key"
```

**下载文件**
```bash
# 通过 short_id 下载
curl "http://localhost:8000/d/AbC123" -o downloaded_file.jpg

# 带 Range 请求（支持断点续传）
curl -H "Range: bytes=0-1048575" "http://localhost:8000/d/AbC123" -o part1.jpg
```

**获取缩略图**
```bash
# 可用尺寸：small (150x150)、medium (300x300)、large (600x600)
curl "http://localhost:8000/api/thumbnail/AbC123?size=medium" -o thumbnail.jpg
```

**删除文件**
```bash
curl -X DELETE "http://localhost:8000/api/files/file_id" \
  -H "Cookie: tgstate_session=your_session_id"
```

**清除缩略图缓存**
```bash
# 清除单个文件的缩略图
curl -X POST "http://localhost:8000/api/thumbnail/clear/file_id"

# 清除所有缩略图缓存
curl -X POST "http://localhost:8000/api/thumbnail/clear-all"
```

#### 实时更新 API

**订阅文件更新（SSE）**
```bash
curl -N "http://localhost:8000/api/file-updates" \
  -H "Cookie: tgstate_session=your_session_id"
```

响应格式：
```json
{
  "action": "add",
  "file_id": "12345:ABCDEF...",
  "short_id": "AbC123",
  "filename": "photo.jpg",
  "filesize": 1048576,
  "mime_type": "image/jpeg",
  "upload_date": "2026-01-30 12:34:56"
}
```

### 🖼️ PicGo 集成

**Typora + PicGo 配置示例**

1. **安装 PicGo**
   - 下载并安装 [PicGo](https://github.com/Molunerfinn/PicGo/releases)

2. **配置自定义图床**

   打开 PicGo，进入"图床设置" → "自定义Web图床"，填入以下配置：

   - **API 地址：** `http://your-server:8000/api/upload`
   - **POST 参数名：** `file`
   - **JSON 路径：** 留空
   - **自定义 Headers：**
     ```json
     {
       "x-api-key": "your_picgo_api_key"
     }
     ```
   - **自定义 Body：** 留空

3. **Typora 配置**

   打开 Typora，进入"偏好设置" → "图像"：
   - **插入图片时：** 选择"上传图片"
   - **上传服务：** 选择"PicGo (app)"
   - **PicGo 路径：** 选择 PicGo 可执行文件路径

4. **测试上传**
   - 在 Typora 中粘贴图片或拖入图片
   - 图片自动上传到 Gram Drive
   - 自动替换为分享链接

---

## 🐛 故障排除

### ❌ Bot 冲突错误

**错误信息：**
```
Conflict: terminated by other getUpdates request
```

**原因分析：**
- 同一个 Bot Token 被多个实例同时使用
- 旧的 Bot 实例未正常关闭
- 在开发环境和生产环境同时运行

**解决方案：**

```bash
# 方法 1：完全重启 Docker 容器
docker-compose down
sleep 10
docker-compose up -d

# 方法 2：手动重启应用
pkill -f "uvicorn app.main"
sleep 5
uvicorn app.main:app --reload

# 方法 3：在 Web 界面重新应用配置
# 进入"系统设置" → 点击"验证并应用"按钮
```

### ❌ 下载服务不工作

**症状：** 自动下载功能无响应，文件不会自动下载到本地

**检查清单：**
- ✅ 设置页面中 `自动下载` 开关是否开启
- ✅ `BOT_TOKEN` 和 `CHANNEL_NAME` 是否正确配置
- ✅ Bot 状态是否显示为"就绪"（绿色指示灯）
- ✅ 下载目录是否有写权限（Docker: `/app/downloads`）
- ✅ 文件类型和大小是否符合过滤规则

**排查方法：**

```bash
# 查看完整日志
docker logs gramdrive --tail 100

# 过滤下载相关日志
docker logs gramdrive 2>&1 | grep -i "download"

# 过滤 Bot 相关日志
docker logs gramdrive 2>&1 | grep -i "bot"

# 实时查看日志
docker logs -f gramdrive
```

**常见问题：**
1. **文件类型不匹配** - 检查 `DOWNLOAD_FILE_TYPES` 是否包含目标类型
2. **文件过大** - 检查 `DOWNLOAD_MAX_SIZE` 是否足够大
3. **权限问题** - 确保 `downloads/` 目录有写权限

### ❌ 缩略图无法加载

**错误信息：**
```
400 Bad Request: Thumbnail generation failed
```

**解决方案：**

```bash
# 1. 检查缩略图服务日志
docker logs gramdrive 2>&1 | grep -i "thumbnail"

# 2. 清除所有缩略图缓存
curl -X POST "http://localhost:8000/api/thumbnail/clear-all" \
  -H "Cookie: tgstate_session=your_session_id"

# 3. 重启服务
docker-compose restart gramdrive
```

**注意事项：**
- 缩略图服务会自动检测 `mime_type` 缺失并假定为图片
- 只有图片文件（JPEG、PNG、WebP、GIF）支持缩略图
- 损坏的图片文件会导致缩略图生成失败

### ❌ 连接池耗尽

**错误信息：**
```
All connections in the connection pool are occupied
```

**原因：** 并发请求过多，连接池资源耗尽

**解决方案：**

当前版本已优化：
- ✅ 连接池增加到 **500 最大连接数**
- ✅ 缩略图服务端缓存，避免重复下载
- ✅ 本地文件优先策略，减少网络请求

更新到最新版本：
```bash
docker-compose pull
docker-compose up -d
```

### ❌ 大文件下载超时

**错误信息：**
```
Read timeout occurred
```

**解决方案：**

当前版本已优化：
- ✅ HTTP 读取超时增加到 **60 分钟**
- ✅ 支持 **2GB+** 大文件下载
- ✅ 最低支持 **0.57 MB/s** 下载速度

如果仍然超时，可手动调整配置：

编辑 `app/core/http_client.py`，修改 `read_timeout` 值：
```python
timeout = httpx.Timeout(
    connect=30.0,
    read=7200.0,  # 增加到 120 分钟
    write=300.0,
    pool=10.0
)
```

### ❌ 频道权限错误

**错误信息：**
```
Chat not found / Bot is not a member of the channel
```

**解决步骤：**
1. 确认频道是否存在且可访问
2. 将 Bot 添加为频道管理员
3. 给予 Bot 以下权限：
   - ✅ 发送消息
   - ✅ 删除消息
   - ✅ 上传文件
4. 在 Web 界面点击"验证频道"按钮测试连接

---

## 📋 系统要求

### 最低配置

| 组件 | 要求 | 说明 |
|------|------|------|
| **操作系统** | Linux / Windows / macOS | 推荐使用 Linux |
| **Python** | 3.11+ | 手动安装时需要 |
| **Docker** | 20.10+ | 容器化部署时需要 |
| **内存** | 512 MB | 轻量级使用 |
| **磁盘** | 1 GB + 存储空间 | 取决于本地缓存和下载文件 |
| **网络** | 稳定互联网连接 | 访问 Telegram API |

### 推荐配置

| 组件 | 推荐 | 说明 |
|------|------|------|
| **CPU** | 2 核心+ | 处理并发请求和缩略图生成 |
| **内存** | 2 GB+ | 更好的缓存性能 |
| **磁盘** | SSD | 提升文件读写速度 |
| **带宽** | 10 Mbps+ | 大文件上传下载流畅 |

---

## 🎉 致谢

本项目基于 **[buyi06/tgstate-python](https://github.com/buyi06/tgstate-python)** 进行深度二次开发，在原有基础上进行了全面的功能增强和架构优化。

特别感谢以下开源项目和技术栈：

| 项目 | 用途 |
|-----|------|
| **[FastAPI](https://fastapi.tiangolo.com/)** | 现代、快速、易用的 Web 框架 |
| **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** | 强大的 Telegram Bot API 封装库 |
| **[Pillow](https://python-pillow.org/)** | 专业的 Python 图像处理库 |
| **[httpx](https://www.python-httpx.org/)** | 优雅的异步 HTTP 客户端 |
| **[SQLite](https://www.sqlite.org/)** | 轻量级嵌入式关系数据库 |
| **[Uvicorn](https://www.uvicorn.org/)** | 闪电般快速的 ASGI 服务器 |
| **[Docker](https://www.docker.com/)** | 容器化部署简化运维 |
| **[Telegram](https://telegram.org/)** | 提供无限免费存储和全球 CDN |

---

## 📄 开源许可

本项目采用 [MIT 许可证](LICENSE) 开源，您可以自由使用、修改和分发。

```
MIT License

Copyright (c) 2026 ispace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🤝 贡献指南

欢迎各种形式的贡献！无论是报告 Bug、提出新功能建议、改进文档，还是提交代码，我们都非常感激。

### 如何贡献

1. **Fork 本仓库** 到你的 GitHub 账号
2. **创建特性分支** (`git checkout -b feature/amazing-feature`)
3. **提交更改** (`git commit -m 'feat: 添加某某功能'`)
4. **推送到分支** (`git push origin feature/amazing-feature`)
5. **创建 Pull Request** 并描述你的改动

### 提交规范

请遵循 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 规范：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 重构代码
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 代码质量

```bash
# 代码检查
ruff check app/

# 自动修复
ruff check --fix app/

# 代码格式化
ruff format app/
```

---

## 💬 联系与支持

### 获取帮助

- 📖 **使用文档** - 查看本 README 和项目内"使用引导"页面
- 🐛 **问题反馈** - [GitHub Issues](https://github.com/ispace-top/GramDrive/issues)
- 💬 **讨论交流** - [GitHub Discussions](https://github.com/ispace-top/GramDrive/discussions)
- 📧 **邮件联系** - kindom162@gmail.com

### 项目信息

- 🏠 **项目主页** - https://github.com/ispace-top/GramDrive
- 📦 **Docker 镜像** - https://hub.docker.com/r/wapedkj/gramdrive
- 🔖 **版本发布** - https://github.com/ispace-top/GramDrive/releases
- 👤 **作者主页** - https://github.com/ispace-top

### 支持项目

如果这个项目对你有帮助，欢迎：

- ⭐ 给项目点个 Star
- 🔀 Fork 项目参与开发
- 📢 分享给更多人
- 💰 [赞助项目](https://github.com/sponsors/ispace-top)（如果可能）

---

<div align="center">
  <p>
    <strong>用 ❤️ 打造，为 Telegram 爱好者服务</strong>
  </p>
  <p>
    <a href="https://github.com/ispace-top/GramDrive">🏠 主页</a> •
    <a href="https://github.com/ispace-top/GramDrive/issues">🐛 反馈</a> •
    <a href="https://github.com/ispace-top/GramDrive/discussions">💬 讨论</a> •
    <a href="https://github.com/ispace-top/GramDrive/releases">📦 下载</a>
  </p>
  <p>
    <sub>Built with FastAPI • Powered by Telegram</sub>
  </p>
</div>
