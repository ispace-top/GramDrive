<div align="center">
  <img src="app/static/images/logo_word.png" alt="Gram Drive Logo" width="400"/>

  <p>
    <strong>Turn Telegram into Your Private Cloud Storage</strong>
  </p>

  <p>
    <a href="https://github.com/ispace-top/GramDrive/releases"><img src="https://img.shields.io/github/v/release/ispace-top/GramDrive?color=blue" alt="Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python"></a>
    <a href="https://hub.docker.com/r/wapedkj/gramdrive"><img src="https://img.shields.io/docker/pulls/wapedkj/gramdrive" alt="Docker Pulls"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ispace-top/GramDrive" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg" alt="Platform"></a>
  </p>

  <p>
    <a href="README.md">中文</a> • English
  </p>
</div>

---

## 📖 Project Introduction

**Gram Drive** is a modern web-based file management system that leverages Telegram as an unlimited cloud storage. Built on FastAPI and optimized for performance, it provides an intuitive interface to manage, preview, and share files stored in your Telegram channel.

## ✨ Key Features

### 🗂️ **File Management**
- **Multi-format Support**: Images, videos, audio, documents, etc.
- **Smart Categorization**: Files are automatically categorized by type (Images/Videos/Audio/Documents/Others).
- **Advanced Search**: Quickly find and filter files.
- **Batch Operations**: Multi-select, batch delete, batch copy links.
- **File Preview**: Supports image, video, PDF, and text file previews with loading states.

### 🖼️ **Image Hosting Mode**
- **Thumbnail Generation**: Automatically generates thumbnails in 3 sizes (150x150, 300x300, 600x600).
- **Smart Caching**: Server-side caching for 80% faster loading.
- **Multiple Formats**: Supports copying URL, Markdown, or HTML links.
- **Grid View**: Beautiful responsive grid layout with hover effects.

### ⬇️ **Smart Download Management**
- **Automatic Downloads**: Automatically sync files from Telegram.
- **Organized Storage**: Files are saved by type and date (`/downloads/image/2026-01-22/photo.jpg`).
- **Configurable Filters**: File type, file size, download location.
- **Real-time Progress**: Online download status and progress tracking.
- **Queue Management**: Supports concurrent downloads with configurable thread count.

### 🎨 **Modern UI/UX**
- **Dark Mode**: Automatic detection and manual switching.
- **Responsive Design**: Adapts to desktop, tablet, and mobile devices.
- **Compact Upload**: Space-saving upload button design.
- **Loading States**: Smooth loading animations and visual feedback.

### 🔒 **Security & Performance**
- **Password Protection**: Secure login system.
- **Session Management**: Automatic logout after extended inactivity.
- **Connection Pool**: High-performance HTTP client (500 concurrent connections).
- **Conflict Resolution**: Smart Telegram Bot conflict handling.

### 📊 **Statistics Dashboard**
- **Storage Analysis**: Total files, storage usage, file type distribution.
- **Upload Trends**: Daily/weekly upload charts.
- **Category Statistics**: Visualized file category statistics.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (Recommended) or **Python 3.11+**
- **Telegram Bot Token** ([Create via @BotFather](https://t.me/BotFather))
- **Telegram Channel** (Create a private channel for file storage)

### 🐳 Docker Deployment (Recommended)

#### Quick Start (Using Pre-built Image)

The simplest way, no local build required:

1. **Create Directory Structure**
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

3. **Create `.env` file** (Optional)
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **Pull Image and Start Application**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Access Web Interface**
   ```
   http://localhost:8000
   ```

6. **Initial Configuration**
   - Open Web Interface
   - Set Admin Password
   - Configure Bot Token and Channel Name in Settings
   - Click "Apply" to start the bot

#### Source Code Deployment (Local Build)

If you need to modify the source code or use the latest development version:

1. **Clone Repository**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
   ```

2. **Create Directory Structure**
   ```bash
   mkdir -p ../GramDrive/data ../GramDrive/downloads
   ```

3. **Create `.env` file** (Optional)
   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_bot_token_here
   CHANNEL_NAME=@your_channel_name
   PASS_WORD=your_admin_password
   PICGO_API_KEY=optional_api_key
   BASE_URL=localhost
   EOF
   ```

4. **Build and Start Application**
   ```bash
   docker-compose up -d --build
   ```

5. **Access Web Interface**
   ```
   http://localhost:8000
   ```

6. **Initial Configuration**
   - Open Web Interface
   - Set Admin Password
   - Configure Bot Token and Channel Name in Settings
   - Click "Apply" to start the bot

### 🔧 Manual Installation

**Prerequisites:**
```bash
python --version  # Requires 3.11+
pip --version
```

**Installation Steps:**

1. **Clone and Setup**
   ```bash
   git clone https://github.com/ispace-top/GramDrive.git
   cd GramDrive
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
   cp .env.example .env
   # Edit .env file, fill in your Bot Token and Channel Name
   ```

4. **Create Data Directories**
   ```bash
   mkdir -p data downloads
   ```

5. **Run Application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access Application**
   ```
   http://localhost:8000
   ```

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | ✅ Yes | - | Telegram Bot Token (from @BotFather) |
| `CHANNEL_NAME` | ✅ Yes | - | Target Telegram Channel (@name or -1001234567890) |
| `PASS_WORD` | ❌ No | - | Admin Password (leave empty for no authentication) |
| `PICGO_API_KEY` | ❌ No | - | API Key for PicGo/Image Host integration |
| `BASE_URL` | ❌ No | `localhost` | Base URL for generated share links |

### Auto Download Configuration

**In Web Settings:**

| Setting | Default | Description |
|---|---|---|
| `AUTO_DOWNLOAD_ENABLED` | `True` | Enable automatic downloads |
| `DOWNLOAD_DIR` | `/app/downloads` | Directory to save downloads |
| `DOWNLOAD_FILE_TYPES` | `image,video` | Comma-separated file types |
| `DOWNLOAD_MAX_SIZE` | `52428800` (50MB) | Maximum download file size (bytes) |
| `DOWNLOAD_MIN_SIZE` | `0` | Minimum download file size (bytes) |
| `DOWNLOAD_THREADS` | `3` | Concurrent downloads |
| `DOWNLOAD_POLLING_INTERVAL` | `60` | Check interval (seconds) |

**Directory Structure:**

Automatically downloaded files are organized by type and date:
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
   - Click to preview files (supports images, videos, PDFs)
   - Multi-select for batch operations
   - Copy file links in various formats (URL, Markdown, HTML)
   - Automatic categorization by file type

2. **Image Hosting Mode**
   - Dedicated interface for image sharing
   - 3 thumbnail sizes (small/medium/large), server-side cached
   - One-click copy to clipboard
   - Share with friends using short links

3. **Download Management**
   - Configure auto-download filters (file type, size)
   - Real-time monitoring of download progress
   - View downloaded files organized by type and date

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

Add to PicGo Custom Uploader:

**PicGo Configuration (PicGo > Plugins > Piclist > Configuration):**
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

**Cause:**
- Multiple application instances running simultaneously
- Old Bot instances not fully shut down
- Running in both development and production environments concurrently

**Solution:**
```bash
# Full restart
docker-compose down
sleep 10
docker-compose up -d --build

# Or manual restart
pkill -f "uvicorn app"
sleep 5
uvicorn app.main:app --reload
```

### Download Service Not Working
**Problem:** Automatic downloads fail to start files

**Checklist:**
- ✅ `AUTO_DOWNLOAD_ENABLED` is set to `True` in settings
- ✅ `BOT_TOKEN` and `CHANNEL_NAME` are configured and applied
- ✅ Bot shows "Ready" (green dot) in settings
- ✅ Check logs: `docker logs gramdrive` for errors
- ✅ Directory exists: `/app/downloads` (or configured `DOWNLOAD_DIR`)

**Fix Method:**
```bash
# Check Bot status logs
docker logs gramdrive | grep -i "bot\|download"

# If Bot fails, restart with new configuration
docker-compose restart gramdrive
```

### Thumbnail API Returns 400
**Problem:** Image preview/thumbnails fail to load

**Solution:**
- The thumbnail service automatically detects missing `mime_type` and assumes an image type.
- Check logs for warnings: `docker logs gramdrive | grep -i thumbnail`
- Clear thumbnail cache: `curl -X POST http://localhost:8000/api/thumbnail/clear-all`

### Connection Pool Timeout
**Error:** `All connections in the connection pool are occupied`

**Cause:** Too many concurrent image loads exhaust the connection pool.

**Solution (Optimized):**
- Connection pool increased to 500 maximum connections.
- Thumbnails are server-side cached (no duplicate downloads).
- Update to the latest version: `docker-compose up -d --build`

## 📋 System Requirements

| Component | Requirement | Notes |
|---|---|---|
| Python | 3.11+ | Required for manual installation |
| Docker | Latest | Recommended for deployment |
| Memory | 512MB | Minimum for light usage |
| Disk | Variable | Depends on the number of stored files |
| Network | Stable Network | For Telegram connection |

## 🎉 Acknowledgments

This project is a secondary development based on **[buyi06/tgstate-python](https://github.com/buyi06/tgstate-python)**. We sincerely thank the original author for their excellent code foundation.

Special thanks also to the following open-source projects and technologies:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** - Telegram Bot API wrapper
- **[Pillow](https://python-pillow.org/)** - Excellent image processing library
- **[httpx](https://www.python-httpx.org/)** - Elegant asynchronous HTTP client
- **[SQLite](https://www.sqlite.org/)** - Reliable embedded database
- **[Uvicorn](https://www.uvicorn.org/)** - Blazingly fast ASGI server
- **[Docker](https://www.docker.com/)** - Simplifies containerization
- **[Telegram](https://telegram.org/)** - Build on a secure platform

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 🤝 Contribution Guide

Contributions are welcome! Feel free to submit Pull Requests.

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Contact & Support

- **Issue Feedback:** [GitHub Issues](https://github.com/ispace-top/GramDrive/issues)
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
