<div align="center">
  <img src="app/static/images/logo_word.png" alt="Gram Drive Logo" width="450"/>

  <p>
    <strong>Transform Telegram into Enterprise-Grade Private Cloud Storage</strong>
  </p>

  <p>
    <a href="https://github.com/ispace-top/GramDrive/releases"><img src="https://img.shields.io/github/v/release/ispace-top/GramDrive?color=blue&style=flat-square" alt="Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.11+-green.svg?style=flat-square" alt="Python"></a>
    <a href="https://hub.docker.com/r/wapedkj/gramdrive"><img src="https://img.shields.io/docker/pulls/wapedkj/gramdrive?style=flat-square" alt="Docker Pulls"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ispace-top/GramDrive?style=flat-square" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg?style=flat-square" alt="Platform"></a>
  </p>

  <p>
    <a href="README.md">中文</a> • English
  </p>
</div>

---

## 🌟 Project Overview

**Gram Drive** is a modern file management system built with **FastAPI**, ingeniously transforming **Telegram channels** into unlimited private cloud storage platforms. Through an elegant web interface, you can easily manage, preview, and share files while enjoying Telegram's unlimited storage space and global CDN acceleration.

### 💡 Why Choose Gram Drive?

- 🎯 **Zero Storage Cost** - Leverage Telegram's unlimited free storage space
- 🚀 **Global CDN Acceleration** - Telegram's worldwide edge nodes ensure lightning-fast access
- 🔒 **Enterprise-Level Security** - End-to-end encryption, private channels safeguard your data
- 💻 **Professional Architecture** - Async high-concurrency, intelligent caching, queue management
- 🎨 **Modern Design** - Responsive UI, dark mode, fluid interactions
- 🔧 **One-Click Deployment** - Dockerized, ready out of the box

---

## ✨ Core Features

### 📁 Intelligent File Management
- **Multi-Format Support** - Images, videos, audio, documents, archives - all file types
- **Automatic Categorization** - Smart type recognition and auto-classification (Image/Video/Audio/Document/Other)
- **Advanced Search & Filter** - Quickly locate target files, filter by name, type, and date
- **Batch Operations** - Multi-select for bulk deletion and link copying
- **Instant Preview** - Online preview for images, videos, audio, PDF, and text files
- **Large File Chunking** - Automatic handling of oversized files (≥19.5MB) with transparent chunked upload/download
- **Short Link Sharing** - Generate concise short links (`/d/AbC123`) for easy sharing

### 🖼️ Professional Image Hosting Service
- **Multi-Size Thumbnails** - Auto-generate three sizes (150x/300x/600x) to save bandwidth
- **Smart Caching Strategy** - Server-side local caching, prioritizes local files, 80%+ speed boost
- **Multi-Format Output** - One-click copy in URL, Markdown, or HTML format
- **Responsive Grid** - Beautiful masonry layout, perfectly adapts to all screens
- **PicGo Integration** - Support PicGo client direct upload, seamlessly integrate workflows

### ⬇️ Auto Download Engine
- **Smart Sync** - Automatically detect and download new files from Telegram channel
- **Organized Storage** - Files organized by type and date (`downloads/image/2026-01-22/photo.jpg`)
- **Flexible Filtering** - Configure file types, size ranges, download directories
- **Queue Management** - Concurrent downloads with configurable thread count
- **Real-Time Progress** - SSE real-time push for download status and progress
- **Resume Support** - Large file chunked downloads with auto-retry for failed tasks
- **Extended Timeout** - Optimized network config, supports 2GB+ large video downloads (60-minute timeout)

### 📊 Data Statistics Dashboard
- **Storage Analysis** - Real-time stats for file count, total storage, type distribution
- **Upload Trends** - Visualize daily/weekly upload volume curves
- **Type Distribution** - Pie charts showing file type breakdown at a glance
- **Performance Metrics** - Monitor Bot status, download queue, system health

### 🎨 Modern Interface
- **Adaptive Theme** - Auto-detect system theme, manual toggle between light/dark modes
- **Responsive Design** - Perfect adaptation for desktop, tablet, and mobile with fluid mobile experience
- **Smooth Animations** - Carefully crafted loading animations and transitions to enhance UX
- **Compact Layout** - Optimized space utilization, reduced visual clutter, focused content

### 🔐 Security & Performance
- **Session Management** - Cookie-based secure session mechanism with auto-expiration protection
- **API Keys** - Support PicGo API Key authentication, dual authentication system
- **High-Concurrency Connection Pool** - 500 concurrent HTTP connections, handles high load scenarios
- **Async Architecture** - Full async design based on asyncio, maximizes system resources
- **Smart Conflict Handling** - Auto-detect and recover Telegram Bot conflicts
- **Version Management** - Complete version tracking with GitHub Release automation

---

## 🏗️ Technical Architecture

### Core Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.110+ | Modern async web framework |
| **Python** | 3.11+ | Primary development language |
| **python-telegram-bot** | 20.0+ | Telegram Bot API wrapper |
| **httpx** | Latest | High-performance async HTTP client |
| **SQLite** | 3.x | Lightweight embedded database |
| **Uvicorn** | Latest | High-performance ASGI server |
| **Pillow** | Latest | Image processing engine |
| **Docker** | Latest | Containerized deployment |

### Key Design Patterns

#### 1️⃣ **Composite File ID System**
- Telegram's `file_id` becomes invalid across different Bot instances
- Innovative use of `{message_id}:{file_id}` composite format for storage
- Message IDs are permanently valid within a channel, ensuring reliable file access and deletion

#### 2️⃣ **Smart Chunking Mechanism**
- Files ≥19.5MB automatically chunked (Telegram's 20MB download limit)
- Generate `.manifest` manifest file to record chunk information
- Transparent assembly on download, concurrent cleanup on delete

#### 3️⃣ **Event-Driven Architecture**
- Publish/Subscribe pattern based on `BroadcastEventBus`
- File changes broadcast in real-time to all SSE subscribed clients
- Zero-latency UI updates, ultimate real-time experience

#### 4️⃣ **Layered Configuration System**
- Priority: Database config > Environment variables > Default values
- Runtime dynamic config modification without service restart
- Encrypted storage for sensitive information, secure and reliable

#### 5️⃣ **Local Cache Optimization**
- Thumbnails prioritize locally downloaded files for generation
- Avoid repeated Telegram API requests, save bandwidth
- 80%+ response speed improvement, significantly enhanced UX

---

## 🚀 Quick Start

### Prerequisites

- ✅ **Docker & Docker Compose** (Recommended) or **Python 3.11+**
- ✅ **Telegram Bot Token** - [Create via @BotFather](https://t.me/BotFather)
- ✅ **Telegram Private Channel** - Create a private channel for file storage

### 🐳 Docker Deployment (Recommended)

#### Method 1: Use Pre-Built Image (Fastest)

1. **Create Project Directory**
   ```bash
   mkdir -p GramDrive/{data,downloads}
   cd GramDrive
   ```

2. **Create `docker-compose.yml`**
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

3. **Create `.env` Configuration File** (Optional, can also configure via web UI)
   ```bash
   cat > .env << 'EOF'
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key_for_picgo
   BASE_URL=http://localhost:8000
   EOF
   ```

4. **Start Service**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Access Web Interface**
   ```
   🌐 http://localhost:8000
   ```

6. **Initial Configuration**
   - Open browser and visit http://localhost:8000
   - Set admin password (first-time access auto-redirects)
   - Navigate to "System Settings" page to configure Bot Token and channel name
   - Click "Verify and Apply" to start service

#### Method 2: Build from Source

```bash
# Clone repository
git clone https://github.com/ispace-top/GramDrive.git
cd GramDrive

# Create data directories
mkdir -p data downloads

# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 💻 Manual Installation

**For developers or custom deployment scenarios**

1. **Environment Setup**
   ```bash
   # Check Python version (requires 3.11+)
   python --version

   # Clone repository
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy example config
   cp .env.example .env

   # Edit .env file with your configuration
   nano .env  # or use another editor
   ```

4. **Initialize Data Directories**
   ```bash
   mkdir -p data downloads
   ```

5. **Start Service**
   ```bash
   # Development mode (with hot reload)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

6. **Access Application**
   ```
   🌐 http://localhost:8000
   ```

---

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `BOT_TOKEN` | ✅ | - | Telegram Bot Token (from @BotFather) |
| `CHANNEL_NAME` | ✅ | - | Telegram channel identifier (@channelname or -1001234567890) |
| `PASS_WORD` | ❌ | - | Admin password (leave empty for no password protection) |
| `PICGO_API_KEY` | ❌ | - | PicGo upload API key (for third-party tool integration) |
| `BASE_URL` | ❌ | `http://localhost:8000` | Base URL for generated share links |

### Auto Download Configuration

Configure the following parameters in the "Download Management" page of the web UI:

| Configuration | Default | Description |
|--------------|---------|-------------|
| `AUTO_DOWNLOAD_ENABLED` | `True` | Enable automatic downloads |
| `DOWNLOAD_DIR` | `/app/downloads` | Directory for downloaded files |
| `DOWNLOAD_FILE_TYPES` | `image,video` | File types to download (comma-separated) |
| `DOWNLOAD_MAX_SIZE` | `52428800` (50MB) | Maximum download file size (bytes) |
| `DOWNLOAD_MIN_SIZE` | `0` | Minimum download file size (bytes) |
| `DOWNLOAD_THREADS` | `3` | Concurrent download thread count |
| `DOWNLOAD_POLLING_INTERVAL` | `60` | Polling check interval (seconds) |

**Directory Structure Example:**

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

## 📚 User Guide

### 🌐 Web Interface Operations

#### 1. File Management
- **Upload Files** - Click "Upload" button in top-right corner, supports drag-and-drop
- **View Files** - Click file card to preview (supports images, videos, audio, PDF, text)
- **Search Files** - Use search box to quickly locate files
- **Filter by Category** - Click type tags to filter (All/Image/Video/Audio/Document/Other)
- **Batch Operations** - Select multiple files for bulk deletion or link copying
- **Copy Links** - Click "Copy Link" button, choose format (URL/Markdown/HTML)

#### 2. Image Hosting Mode
- **View Images** - Auto-generate thumbnails, grid display all images
- **Copy Links** - Click "Copy" button on image card
- **Select Size** - Choose original or different thumbnail sizes when copying
- **Quick Share** - Use short links `/d/AbC123` for convenient sharing

#### 3. Download Management
- **Configure Rules** - Click "Settings" button to configure auto-download filters
- **View Progress** - Real-time view of downloading files and progress
- **Browse Files** - View locally downloaded files organized by date and type

#### 4. Data Statistics
- **Storage Overview** - View total file count and storage usage
- **Type Distribution** - Pie chart showing file type breakdown
- **Upload Trends** - Line chart displaying upload volume changes

#### 5. System Settings
- **Bot Configuration** - Configure and verify Telegram Bot Token
- **Channel Configuration** - Set Telegram storage channel
- **Password Management** - Change admin password
- **API Keys** - Configure PicGo API Key
- **Base URL** - Set domain for share links

### 🔌 API Endpoints

#### File Operations API

**Get File List**
```bash
curl -X GET "http://localhost:8000/api/files" \
  -H "Cookie: tgstate_session=your_session_id"
```

**Upload File (Web Auth)**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/file.jpg" \
  -H "Cookie: tgstate_session=your_session_id"
```

**Upload File (API Key Auth)**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@photo.jpg" \
  -H "x-api-key: your_picgo_api_key"
```

**Download File**
```bash
# Download via short_id
curl "http://localhost:8000/d/AbC123" -o downloaded_file.jpg

# With Range request (supports resume)
curl -H "Range: bytes=0-1048575" "http://localhost:8000/d/AbC123" -o part1.jpg
```

**Get Thumbnail**
```bash
# Available sizes: small (150x150), medium (300x300), large (600x600)
curl "http://localhost:8000/api/thumbnail/AbC123?size=medium" -o thumbnail.jpg
```

**Delete File**
```bash
curl -X DELETE "http://localhost:8000/api/files/file_id" \
  -H "Cookie: tgstate_session=your_session_id"
```

**Clear Thumbnail Cache**
```bash
# Clear single file's thumbnail
curl -X POST "http://localhost:8000/api/thumbnail/clear/file_id"

# Clear all thumbnail cache
curl -X POST "http://localhost:8000/api/thumbnail/clear-all"
```

#### Real-Time Update API

**Subscribe to File Updates (SSE)**
```bash
curl -N "http://localhost:8000/api/file-updates" \
  -H "Cookie: tgstate_session=your_session_id"
```

Response format:
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

### 🖼️ PicGo Integration

**Typora + PicGo Configuration Example**

1. **Install PicGo**
   - Download and install [PicGo](https://github.com/Molunerfinn/PicGo/releases)

2. **Configure Custom Image Bed**

   Open PicGo, navigate to "Image Bed Settings" → "Custom Web Image Bed", fill in:

   - **API URL:** `http://your-server:8000/api/upload`
   - **POST Parameter Name:** `file`
   - **JSON Path:** Leave empty
   - **Custom Headers:**
     ```json
     {
       "x-api-key": "your_picgo_api_key"
     }
     ```
   - **Custom Body:** Leave empty

3. **Typora Configuration**

   Open Typora, go to "Preferences" → "Image":
   - **When Insert Image:** Select "Upload Image"
   - **Upload Service:** Select "PicGo (app)"
   - **PicGo Path:** Select PicGo executable file path

4. **Test Upload**
   - Paste or drag image into Typora
   - Image auto-uploads to Gram Drive
   - Automatically replaced with share link

---

## 🐛 Troubleshooting

### ❌ Bot Conflict Error

**Error Message:**
```
Conflict: terminated by other getUpdates request
```

**Analysis:**
- Same Bot Token used by multiple instances simultaneously
- Old Bot instance not properly shut down
- Running in both development and production environments

**Solutions:**

```bash
# Method 1: Full Docker container restart
docker-compose down
sleep 10
docker-compose up -d

# Method 2: Manual application restart
pkill -f "uvicorn app.main"
sleep 5
uvicorn app.main:app --reload

# Method 3: Reapply config in web UI
# Go to "System Settings" → Click "Verify and Apply" button
```

### ❌ Download Service Not Working

**Symptoms:** Auto-download feature unresponsive, files not downloading locally

**Checklist:**
- ✅ `Auto Download` toggle enabled in settings page
- ✅ `BOT_TOKEN` and `CHANNEL_NAME` correctly configured
- ✅ Bot status shows "Ready" (green indicator)
- ✅ Download directory has write permissions (Docker: `/app/downloads`)
- ✅ File type and size match filter rules

**Diagnostic Methods:**

```bash
# View full logs
docker logs gramdrive --tail 100

# Filter download-related logs
docker logs gramdrive 2>&1 | grep -i "download"

# Filter Bot-related logs
docker logs gramdrive 2>&1 | grep -i "bot"

# View logs in real-time
docker logs -f gramdrive
```

**Common Issues:**
1. **File type mismatch** - Check if `DOWNLOAD_FILE_TYPES` includes target type
2. **File too large** - Check if `DOWNLOAD_MAX_SIZE` is sufficiently large
3. **Permission issues** - Ensure `downloads/` directory has write permissions

### ❌ Thumbnails Won't Load

**Error Message:**
```
400 Bad Request: Thumbnail generation failed
```

**Solutions:**

```bash
# 1. Check thumbnail service logs
docker logs gramdrive 2>&1 | grep -i "thumbnail"

# 2. Clear all thumbnail cache
curl -X POST "http://localhost:8000/api/thumbnail/clear-all" \
  -H "Cookie: tgstate_session=your_session_id"

# 3. Restart service
docker-compose restart gramdrive
```

**Notes:**
- Thumbnail service auto-detects missing `mime_type` and assumes image
- Only image files (JPEG, PNG, WebP, GIF) support thumbnails
- Corrupted image files will cause thumbnail generation to fail

### ❌ Connection Pool Exhausted

**Error Message:**
```
All connections in the connection pool are occupied
```

**Cause:** Too many concurrent requests, connection pool resources exhausted

**Solution:**

Current version optimized:
- ✅ Connection pool increased to **500 max connections**
- ✅ Thumbnail server-side caching, avoid duplicate downloads
- ✅ Local file priority strategy, reduce network requests

Update to latest version:
```bash
docker-compose pull
docker-compose up -d
```

### ❌ Large File Download Timeout

**Error Message:**
```
Read timeout occurred
```

**Solution:**

Current version optimized:
- ✅ HTTP read timeout increased to **60 minutes**
- ✅ Supports **2GB+** large file downloads
- ✅ Minimum support for **0.57 MB/s** download speed

If still timing out, manually adjust configuration:

Edit `app/core/http_client.py`, modify `read_timeout` value:
```python
timeout = httpx.Timeout(
    connect=30.0,
    read=7200.0,  # Increase to 120 minutes
    write=300.0,
    pool=10.0
)
```

### ❌ Channel Permission Error

**Error Message:**
```
Chat not found / Bot is not a member of the channel
```

**Resolution Steps:**
1. Confirm channel exists and is accessible
2. Add Bot as channel administrator
3. Grant Bot the following permissions:
   - ✅ Send messages
   - ✅ Delete messages
   - ✅ Upload files
4. Click "Verify Channel" button in web UI to test connection

---

## 📋 System Requirements

### Minimum Configuration

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Operating System** | Linux / Windows / macOS | Linux recommended |
| **Python** | 3.11+ | Required for manual installation |
| **Docker** | 20.10+ | Required for containerized deployment |
| **Memory** | 512 MB | For lightweight usage |
| **Disk** | 1 GB + storage space | Depends on local cache and downloaded files |
| **Network** | Stable internet connection | Access Telegram API |

### Recommended Configuration

| Component | Recommendation | Notes |
|-----------|---------------|-------|
| **CPU** | 2+ cores | Handle concurrent requests and thumbnail generation |
| **Memory** | 2 GB+ | Better caching performance |
| **Disk** | SSD | Improve file read/write speed |
| **Bandwidth** | 10 Mbps+ | Smooth large file upload/download |

---

## 🎉 Acknowledgments

This project is based on **[buyi06/tgstate-python](https://github.com/buyi06/tgstate-python)** with deep secondary development, featuring comprehensive enhancements and architectural optimizations.

Special thanks to the following open-source projects and technology stack:

| Project | Purpose |
|---------|---------|
| **[FastAPI](https://fastapi.tiangolo.com/)** | Modern, fast, easy-to-use web framework |
| **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** | Powerful Telegram Bot API wrapper library |
| **[Pillow](https://python-pillow.org/)** | Professional Python image processing library |
| **[httpx](https://www.python-httpx.org/)** | Elegant async HTTP client |
| **[SQLite](https://www.sqlite.org/)** | Lightweight embedded relational database |
| **[Uvicorn](https://www.uvicorn.org/)** | Blazingly fast ASGI server |
| **[Docker](https://www.docker.com/)** | Simplified containerized deployment |
| **[Telegram](https://telegram.org/)** | Provides unlimited free storage and global CDN |

---

## 📄 Open Source License

This project is open-sourced under the [MIT License](LICENSE). You are free to use, modify, and distribute.

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

## 🤝 Contribution Guidelines

All forms of contribution are welcome! Whether reporting bugs, suggesting new features, improving documentation, or submitting code, we greatly appreciate it.

### How to Contribute

1. **Fork this repository** to your GitHub account
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'feat: add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Create Pull Request** and describe your changes

### Commit Conventions

Please follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `style:` Code formatting (no functional impact)
- `refactor:` Code refactoring
- `perf:` Performance optimization
- `test:` Testing related
- `chore:` Build/toolchain related

### Code Quality

```bash
# Code check
ruff check app/

# Auto-fix
ruff check --fix app/

# Code formatting
ruff format app/
```

---

## 💬 Contact & Support

### Get Help

- 📖 **Documentation** - See this README and in-app "User Guide" page
- 🐛 **Issue Reporting** - [GitHub Issues](https://github.com/ispace-top/GramDrive/issues)
- 💬 **Discussion** - [GitHub Discussions](https://github.com/ispace-top/GramDrive/discussions)
- 📧 **Email Contact** - kindom162@gmail.com

### Project Information

- 🏠 **Project Homepage** - https://github.com/ispace-top/GramDrive
- 📦 **Docker Image** - https://hub.docker.com/r/wapedkj/gramdrive
- 🔖 **Releases** - https://github.com/ispace-top/GramDrive/releases
- 👤 **Author Profile** - https://github.com/ispace-top

### Support the Project

If this project helps you, welcome to:

- ⭐ Star the project
- 🔀 Fork and participate in development
- 📢 Share with more people
- 💰 [Sponsor the project](https://github.com/sponsors/ispace-top) (if possible)

---

<div align="center">
  <p>
    <strong>Built with ❤️ for Telegram Enthusiasts</strong>
  </p>
  <p>
    <a href="https://github.com/ispace-top/GramDrive">🏠 Home</a> •
    <a href="https://github.com/ispace-top/GramDrive/issues">🐛 Issues</a> •
    <a href="https://github.com/ispace-top/GramDrive/discussions">💬 Discussions</a> •
    <a href="https://github.com/ispace-top/GramDrive/releases">📦 Releases</a>
  </p>
  <p>
    <sub>Built with FastAPI • Powered by Telegram</sub>
  </p>
</div>
