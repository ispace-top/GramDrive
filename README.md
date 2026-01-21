# TgCloud: 您的专属 Telegram 私有云存储

[![构建状态](https://github.com/ispace-top/tgstate-python/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ispace-top/tgstate-python/actions/workflows/docker-image.yml)
[![Python 版本](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![框架](https://img.shields.io/badge/框架-FastAPI-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![许可证](https://img.shields.io/badge/许可证-MIT-blue.svg)](LICENSE)
[![Docker 拉取量](https://img.shields.io/docker/pulls/wapedkj/tgcloud?logo=docker)](https://hub.docker.com/r/wapedkj/tgcloud)

[English Version](README.en.md)

**将您的 Telegram 账号转变为一个功能丰富、永久在线的私有云存储和媒体中心。**

TgCloud 利用 Telegram 无限的存储能力，提供一个优雅的网页界面，让您轻松管理文件、创建分享链接，甚至可以作为 PicGo 等服务的高效图床。所有数据都安全地存储在您选择的私有频道或群组中。

---

<!-- 建议在此处添加网页界面的截图或 GIF！ -->
<!-- ![TgCloud 截图](https://your-image-host.com/tgcloud_screenshot.png) -->

## ✨ 主要功能

-   **无限存储**：存储容量仅受 Telegram 本身限制。
-   **现代化网页界面**：简洁、响应式、直观的用户界面，支持亮色和暗色模式。
-   **文件管理**：轻松上传、下载、删除和搜索您的文件。支持批量操作。
-   **拖拽上传**：只需将文件拖拽到浏览器中即可无缝上传。大文件自动分块。
-   **短链接分享**：生成简洁的分享链接（例如 `/d/AbC123`），并自动适配当前访问域名。
-   **图床模式**：专用的图片画廊视图。支持一键复制 URL、Markdown 或 HTML 格式链接，完全兼容 PicGo。
-   **统计仪表板**：全面的仪表板，可视化您的存储使用情况、文件类型分布、下载次数等。
-   **下载管理器**：配置从您的频道自动下载文件到本地服务器存储，并直接从 UI 管理这些本地文件。
-   **高级文件服务**：
    -   **流媒体支持**：完全支持 HTTP Range 请求，用于流式传输音频和视频文件。无需等待即可随意拖动媒体播放进度。
    -   **智能内容处理**：自动在浏览器中预览可查看文件（图片、PDF、视频），并触发其他文件的下载。
    -   **强制下载**：通过在 URL 中添加 `?download=1` 参数，可强制下载任何文件。
-   **安全与隐私**：
    -   您的文件存储在您自己的私有频道/群组中。
    -   网页界面由您选择的密码保护。
    -   支持 API Key 认证，用于程序化上传（例如 PicGo）。
-   **实时更新**：文件列表会随着新文件的上传或删除而实时更新，这得益于服务器发送事件（SSE）。
-   **轻松部署**：可使用 Docker 即时部署，或直接从源代码运行。

## 🛠️ 技术栈

| 组件         | 技术               |
| :----------- | :----------------- |
| **后端框架**   | FastAPI            |
| **Telegram Bot 库** | `python-telegram-bot` |
| **异步 HTTP 客户端** | `httpx`            |
| **数据库**     | SQLite             |
| **Web 服务器** | Uvicorn            |
| **实时事件**   | `sse-starlette`    |
| **配置管理**   | `pydantic-settings` |
| **代码检查与格式化** | Ruff               |
| **容器化**     | Docker             |

## 🚀 快速开始

您可以通过 Docker（推荐用于生产环境）部署 TgCloud，也可以从源代码直接运行（用于开发）。

### 1. Docker 部署（推荐）

这是最简单、最可靠的上手方式。

```bash
# 1. 创建一个持久化卷用于存储数据（数据库等）
docker volume create tgcloud_data

# 2. 拉取最新镜像并运行容器
# 将 8000 替换为您的主机上偏好的任何端口
docker run -d \
  --name tgcloud \
  --restart unless-stopped \
  -p 8000:8000 \
  -v tgcloud_data:/app/data \
  wapedkj/tgcloud:latest
```

运行命令后，通过 `http://<您的服务器IP>:8000` 访问网页界面。

### 2. 本地开发（从源代码）

此方法适用于希望修改代码的开发者。

```bash
# 1. 克隆仓库
git clone https://github.com/ispace-top/tgstate-python.git
cd tgstate-python

# 2. 创建并激活虚拟环境
python -m venv venv
# 在 Windows 上：
# venv\Scripts\activate
# 在 macOS/Linux 上：
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置您的环境
cp .env.example .env
# 现在，编辑 .env 文件并填入您的设置（请参阅下面的配置说明）

# 5. 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

应用程序将通过 `http://localhost:8000` 访问。

## ⚙️ 初始配置

首次启动后，系统会提示您设置管理员密码。登录后，请导航到 **系统设置** 完成所有核心配置。

#### 步骤 1: 从 BotFather 获取 `BOT_TOKEN`

1.  打开 Telegram 并搜索官方 **[@BotFather](https://t.me/BotFather)**。
2.  开始聊天并发送 `/newbot` 命令。
3.  按照提示设置您的机器人的名称和用户名（用户名必须以 `bot` 结尾）。
4.  成功后，BotFather 会发送一条消息，其中 `Use this token to access the HTTP API:` 下方的那串字符就是您的 **`BOT_TOKEN`**。

#### 步骤 2: 获取 `CHANNEL_NAME` (聊天 ID)

1.  在 Telegram 中创建一个新的**私有**频道或群组。
2.  将您刚刚创建的机器人添加为该频道/群组的**管理员**。
3.  向您的频道/群组发送任意消息（例如“hello”）。
4.  将该消息转发给机器人 **[@userinfobot](https://t.me/userinfobot)**。
5.  它将回复详细信息，包括 `From Chat` ID。复制该 ID，它通常是一个以 `-100...` 开头的数字。这就是您的 **`CHANNEL_NAME`**。

现在，在网页 UI 的“系统设置”页面中填入这些值。

## 🔧 配置变量

所有设置都可以通过环境变量（在 `.env` 文件或 Docker 环境中）或在首次启动后通过网页 UI 进行配置。

| 变量          | 描述                                     | 默认值          |
| :----------- | :--------------------------------------- | :-------------- |
| `BOT_TOKEN`   | **必需。** 您的 Telegram Bot Token。     | `""`            |
| `CHANNEL_NAME` | **必需。** 您的私有频道/群组的 ID。      | `""`            |
| `PASS_WORD`   | 网页界面的管理员密码。如果为空，则无需认证。 | `""`            |
| `BASE_URL`    | 您的实例对外公开的 URL（例如 `https://tg.example.com`）。可选，但为了 Bot 回复链接的准确性，建议填写。 | `""`            |
| `PICGO_API_KEY`| 用于 PicGo 上传的 API Key。请设置一个安全的随机字符串。 | `""`            |

## 🙏 致谢与 Fork 信息

本项目是 **[ispace-top/tgstate-python](https://github.com/ispace-top/tgstate-python)** 仓库的一个 Fork，并在此基础上进行了大量增强。

衷心感谢原作者为本项目奠定了出色的基础。此 Fork 旨在通过新功能、错误修复和略有不同的架构方向来继续开发。

## 📄 许可证

本项目采用 **MIT 许可证**。详情请参阅 [LICENSE](LICENSE) 文件。
