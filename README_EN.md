<div align="center">
  <img src="app/static/images/logo_word.png" alt="Gram Drive Logo" width="400"/>

  <p>
    <strong>Turn Telegram into Your Personal Cloud Storage</strong>
  </p>

  <p>
    <a href="https://github.com/ispace-top/GramDrive/releases"><img src="https://img.shields.io/github/v/release/ispace-top/GramDrive?color=blue" alt="Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python"></a>
    <a href="https://hub.docker.com/r/wapedkj/gramdrive"><img src="https://img.shields.io/docker/pulls/wapedkj/gramdrive" alt="Docker Pulls"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ispace-top/GramDrive" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg" alt="Platform"></a>
  </p>

  <p>
    📖 <a href="README.md">中文</a> • English
  </p>
</div>

---

## 📖 Overview

**Gram Drive** is a modern web-based file management system that leverages Telegram as unlimited cloud storage. Built with FastAPI and optimized for performance, it provides an intuitive interface to manage, preview, and share your files stored in Telegram channels.

## ✨ Key Features

### 🗂️ **File Management**
- **Multi-format Support**: Images, videos, audio, documents, and more
- **Smart Categories**: Auto-categorization by file type (image/video/audio/document/other)
- **Advanced Search**: Quick file search and filtering
- **Batch Operations**: Multi-select, batch delete, bulk link copying
- **File Preview**: Built-in preview for images, videos, PDFs, and text files with loading states

### 🖼️ **Image Hosting Mode**
- **Thumbnail Generation**: Automatic thumbnail creation with 3 size options (150x150, 300x300, 600x600)
- **Smart Caching**: Server-side caching for blazing-fast loading (~80% faster)
- **Link Formats**: Copy as URL, Markdown, or HTML
- **Grid View**: Beautiful responsive grid layout with hover effects

### ⬇️ **Intelligent Download Management**
- **Auto-Download**: Automatic file synchronization from Telegram
- **Organized Storage**: Files saved by type and date (`/downloads/image/2026-01-22/photo.jpg`)
- **Configurable Filters**: File type, size range, download location
- **Real-time Progress**: Live download status with progress tracking
- **Queue Management**: Concurrent downloads with configurable threads

### 🎨 **Modern UI/UX**
- **Dark Mode**: Auto-detection with manual toggle
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Compact Upload**: Space-efficient upload button design
- **Loading States**: Smooth loading animations and visual feedback

### 🔒 **Security & Performance**
- **Password Protection**: Secure login system
- **Session Management**: Auto-logout after inactivity
- **Connection Pooling**: High-performance HTTP client (500 concurrent connections)
- **Conflict Resolution**: Smart Telegram Bot conflict handling

### 📊 **Statistics Dashboard**
- **Storage Analytics**: Total files, storage usage, file type distribution
- **Upload Trends**: Daily/weekly upload charts
- **Category Breakdown**: Visual file category statistics

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended) or **Python 3.11+**
- **Telegram Bot Token** ([Create one via @BotFather](https://t.me/BotFather))
- **Telegram Channel** (create a private channel for file storage)

### 🐳 Docker Deployment (Recommended)

#### Quick Start (Using Pre-built Image)

The simplest way without building locally:

1. **Create directory structure**
   ```bash
   mkdir -p ../GramDrive/data ../GramDrive/downloads
   cd ../GramDrive
   ```

2. **Create `docker-compose.yml` file**
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

3. **Create `.env` file** (optional)
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **Pull image and start the application**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Access the web interface**
   ```
   http://localhost:8000
   ```

6. **Initial Setup**
   - Open the web interface
   - Set your admin password
   - Configure Bot Token and Channel Name in Settings
   - Click "Apply" to start the bot

#### Source Code Deployment (Build Locally)

If you need to modify the source code or use the latest development version:

1. **Clone the repository**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
   ```

2. **Create directory structure**
   ```bash
   mkdir -p ../GramDrive/data ../GramDrive/downloads
   ```

3. **Create `.env` file** (optional)
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **Build and start the application**
   ```bash
   docker-compose up -d --build
   ```

5. **Access the web interface**
   ```
   http://localhost:8000
   ```

6. **Initial Setup**
   - Open the web interface
   - Set your admin password
   - Configure Bot Token and Channel Name in Settings
   - Click "Apply" to start the bot

### 🔧 Manual Installation

**Prerequisites:**
```bash
python --version  # Should be 3.11+
pip --version
```

**Installation Steps:**

1. **Clone and setup**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Bot Token and Channel Name
   ```

4. **Create data directories**
   ```bash
   mkdir -p data downloads
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   ```
   http://localhost:8000
   ```

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ Yes | - | Telegram bot token from @BotFather |
| `CHANNEL_NAME` | ✅ Yes | - | Target Telegram channel (@name or -1001234567890) |
| `PASS_WORD` | ❌ No | - | Admin password (leave empty for no auth) |
| `PICGO_API_KEY` | ❌ No | - | API key for PicGo/image hosting integration |
| `BASE_URL` | ❌ No | `localhost` | Base URL for generated share links |

### Auto-Download Configuration

**In Web Settings:**

| Setting | Default | Description |
|---------|---------|-------------|
| `AUTO_DOWNLOAD_ENABLED` | `True` | Enable automatic file downloads |
| `DOWNLOAD_DIR` | `/app/downloads` | Directory to save downloads |
| `DOWNLOAD_FILE_TYPES` | `image,video` | Comma-separated file types to download |
| `DOWNLOAD_MAX_SIZE` | `52428800` (50MB) | Maximum file size to download (bytes) |
| `DOWNLOAD_MIN_SIZE` | `0` | Minimum file size to download (bytes) |
| `DOWNLOAD_THREADS` | `3` | Number of concurrent downloads |
| `DOWNLOAD_POLLING_INTERVAL` | `60` | Check interval in seconds |

**Directory Structure:**

Auto-downloaded files are organized by type and date:
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

## 📚 Usage Examples

### 🌐 Web Interface

1. **File Management**
   - Click on files to preview (images, videos, PDFs supported)
   - Multi-select for batch operations
   - Copy file links in multiple formats (URL, Markdown, HTML)
   - Auto-categorization by file type

2. **Image Hosting Mode**
   - Dedicated interface for image sharing
   - 3-size thumbnails (small/medium/large) with server-side caching
   - One-click copy to clipboard
   - Share with friends using short URLs

3. **Download Management**
   - Configure auto-download filters (file types, sizes)
   - Monitor download progress in real-time
   - View organized downloads by type and date

### 🔌 API Usage

**Get File List**
```bash
curl -X GET "http://localhost:8000/api/files" \
  -H "Cookie: tgstate_session=your_session_id"
```

**Upload File**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/file.jpg" \
  -H "Cookie: tgstate_session=your_session_id"
```

**Upload with PicGo**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@photo.jpg" \
  -H "x-api-key: your_api_key"
```

**Download File**
```bash
curl "http://localhost:8000/d/AbC123" -o downloaded_file.jpg
```

**Get Thumbnail**
```bash
# Available sizes: small (150x150), medium (300x300), large (600x600)
curl "http://localhost:8000/api/thumbnail/file_id?size=medium" -o thumb.jpg
```

**Delete File**
```bash
curl -X DELETE "http://localhost:8000/api/files/file_id" \
  -H "Cookie: tgstate_session=your_session_id"
```

### 🖼️ PicGo Configuration

Add to PicGo with custom uploader:

**PicGo Config (PicGo > Plugin > Piclist > Config):**
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

## 🐛 Troubleshooting

### Bot Conflict Error
**Error:** `Conflict: terminated by other getUpdates request`

**Causes:**
- Multiple app instances running simultaneously
- Old bot instance not fully shut down
- Running in both dev and production environments

**Solutions:**
```bash
# Complete restart
docker-compose down
sleep 10
docker-compose up -d --build

# Or manually
pkill -f "uvicorn app"
sleep 5
uvicorn app.main:app --reload
```

### Download Service Not Working
**Problem:** Auto-download is not starting files

**Checklist:**
- ✅ `AUTO_DOWNLOAD_ENABLED` is set to `True` in Settings
- ✅ `BOT_TOKEN` and `CHANNEL_NAME` are configured and applied
- ✅ Bot shows as "Ready" (green dot) in Settings
- ✅ Check logs: `docker logs gramdrive` for errors
- ✅ Directory exists: `/app/downloads` (or configured `DOWNLOAD_DIR`)

**Fix:**
```bash
# Check bot status in logs
docker logs gramdrive | grep -i "bot\|download"

# If bot failed, restart with fresh configuration
docker-compose restart gramdrive
```

### Thumbnail API Returning 400
**Problem:** Image preview/thumbnails not loading

**Solution:**
- Thumbnail service auto-detects missing `mime_type` and assumes images
- Check logs for warnings: `docker logs gramdrive | grep -i thumbnail`
- Clear thumbnail cache: `curl -X POST http://localhost:8000/api/thumbnail/clear-all`

### Connection Pool Timeout
**Error:** `All connections in the connection pool are occupied`

**Cause:** Too many concurrent image loads exhausting connection pool

**Solution (already optimized):**
- Connection pool increased to 500 max connections
- Thumbnails cached server-side (no repeated downloads)
- Update to latest version: `docker-compose up -d --build`

## 📋 System Requirements

| Component | Requirement | Notes |
|-----------|------------|-------|
| Python | 3.11+ | For manual installation |
| Docker | Latest | Recommended for deployment |
| Memory | 512MB | Minimum for light usage |
| Disk | Variable | Depends on stored files |
| Network | Stable internet | For Telegram connectivity |

## 🎉 Acknowledgments

This project is a second development based on **[buyi06/tgstate-python](https://github.com/buyi06/tgstate-python)**. Special thanks to the original author for the excellent code foundation.

We also greatly appreciate the following open source projects and technologies:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** - Telegram Bot API wrapper
- **[Pillow](https://python-pillow.org/)** - Image processing excellence
- **[httpx](https://www.python-httpx.org/)** - Elegant async HTTP client
- **[SQLite](https://www.sqlite.org/)** - Reliable embedded database
- **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[Docker](https://www.docker.com/)** - Containerization made simple
- **[Telegram](https://telegram.org/)** - Building on a secure platform

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/ispace-top/GramDrive/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ispace-top/GramDrive/discussions)
- **Email:** your-email@example.com

---

<div align="center">
  <p>
    <strong>Made with ❤️ for Telegram enthusiasts</strong><br>
    <a href="https://github.com/ispace-top/GramDrive">GitHub</a> •
    <a href="https://github.com/ispace-top/GramDrive/issues">Issues</a> •
    <a href="https://github.com/ispace-top/GramDrive/discussions">Discussions</a>
  </p>
</div>
