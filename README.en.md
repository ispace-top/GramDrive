# Gram Drive: Your Personal Telegram Cloud Storage

[![Build Status](https://github.com/ispace-top/tgstate-python/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ispace-top/tgstate-python/actions/workflows/docker-image.yml)
[![Python Version](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/wapedkj/gramdrive?logo=docker)](https://hub.docker.com/r/wapedkj/gramdrive)

[中文版本](README.md)

**Transform your Telegram account into a private, feature-rich, and everlasting cloud storage and media center.**

Gram Drive leverages Telegram's unlimited storage, providing a sleek web interface to manage your files, create shareable links, and even serve as a powerful image host for services like PicGo. All your data is securely stored in a private channel or group of your choice.

---

<!-- We recommend adding a screenshot or GIF of the web interface here! -->
<!-- ![Gram Drive Screenshot](https://your-image-host.com/gramdrive_screenshot.png) -->

## ✨ Key Features

-   **Limitless Storage**: Your storage capacity is only limited by Telegram itself.
-   **Modern Web Interface**: Clean, responsive, and intuitive UI with both light and dark modes.
-   **File Management**: Upload, download, delete, and search your files with ease. Supports batch operations.
-   **Drag & Drop Uploads**: Simply drag files into the browser for a seamless upload experience. Large files are automatically chunked.
-   **Short URL Sharing**: Generate clean, short links (e.g., `/d/AbC123`) for easy sharing.
-   **Image Hosting Mode**: A dedicated gallery view for your images. Copy links in URL, Markdown, or HTML formats, fully compatible with PicGo.
-   **Statistics Dashboard**: A comprehensive dashboard to visualize your storage usage, file type distribution, download counts, and more.
-   **Downloads Manager**: Configure auto-downloading of files from your channel to local server storage, and manage these local files directly from the UI.
-   **Advanced File Serving**：
    -   **Streaming Support**: Full `Range` request support for streaming audio and video files. Seek and scrub through your media without waiting.
    -   **Smart Content-Disposition**: Automatically previews viewable files (images, PDFs, videos) in-browser and triggers downloads for others.
    -   **Force Download**: Option to force download any file by adding `?download=1` to the URL.
-   **Secure & Private**:
    -   Your files are stored in your own private channel/group.
    -   The web interface is protected by a password of your choice.
    -   Supports API Key authentication for programmatic uploads (e.g., PicGo).
-   **Real-time Updates**: The file list updates in real-time as new files are uploaded or deleted, thanks to Server-Sent Events (SSE).
-   **Easy Deployment**: Deploy instantly with Docker or run directly from source.

## 🛠️ Technology Stack

| Component         | Technology            |
| :---------------- | :-------------------- |
| **Backend Framework** | FastAPI               |
| **Telegram Bot Lib**  | `python-telegram-bot` |
| **Async HTTP Client** | `httpx`               |
| **Database**      | SQLite                |
| **Web Server**    | Uvicorn               |
| **Real-time Events**  | `sse-starlette`       |
| **Configuration** | `pydantic-settings`   |
| **Linting & Formatting** | Ruff                  |
| **Containerization** | Docker                |

## 🚀 Getting Started

You can deploy Gram Drive using Docker (recommended for production) or run it directly from the source code (for development).

### 1. Docker Deployment (Recommended)

This is the easiest and most reliable way to get started.

```bash
# 1. Create a persistent volume for your data (database, etc.)
docker volume create gramdrive_data

# 2. Pull the latest image and run the container
# Replace 8000 with any port you prefer on your host machine
docker run -d \
  --name gramdrive \
  --restart unless-stopped \
  -p 8000:8000 \
  -v gramdrive_data:/app/data \
  wapedkj/gramdrive:latest
```

**Configuring `DOWNLOAD_DIR` for Automatic Downloads**

If you enable the automatic download feature in the "Downloads Manager" and want the downloaded files to be persistently stored on your host machine, you need to map the container's download path `/app/downloads` to a directory on your host. For example:

```bash
docker run -d \
  --name gramdrive \
  --restart unless-stopped \
  -p 8000:8000 \
  -v gramdrive_data:/app/data \
  -v /path/on/your/host:/app/downloads \# Add this line: maps container download dir to host
  wapedkj/gramdrive:latest
```

*   Please replace `/path/on/your/host` with the absolute path on your host machine where you want to store downloaded files.
*   **Important**: Ensure the `/path/on/your/host` directory exists and Docker has write permissions to it.


After running the command, access the web interface at `http://<your_server_ip>:8000`.

### 2. Local Development (From Source)

This method is suitable for developers who want to modify the code.

```bash
# 1. Clone the repository
git clone https://github.com/ispace-top/tgstate-python.git
cd tgstate-python

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment
cp .env.example .env
# Now, edit the .env file with your settings (see configuration below)

# 5. Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The application will be available at `http://localhost:8000`.

## ⚙️ Initial Configuration

After the first launch, you'll be prompted to set an admin password. Once logged in, navigate to **System Settings** to complete the setup.

#### Step 1: Get `BOT_TOKEN` from BotFather

1.  Open Telegram and search for the official **[@BotFather](https://t.me/BotFather)**.
2.  Start a chat and send the `/newbot` command.
3.  Follow the prompts to set a name and a username for your bot (the username must end in `bot`).
4.  BotFather will send you a message containing the token. Copy the string under `Use this token to access the HTTP API:`. This is your **`BOT_TOKEN`**.

#### Step 2: Get `CHANNEL_NAME` (Chat ID)

1.  Create a new **private** channel or group in Telegram.
2.  Add the bot you just created as an **administrator** in the channel/group.
3.  Send any message (e.g., "hello") to your channel/group.
4.  Forward that message to the bot **[@userinfobot](https://t.me/userinfobot)**.
5.  It will reply with details, including the `From Chat` ID. Copy the ID, which is usually a number starting with `-100...`. This is your **`CHANNEL_NAME`**.

Now, enter these values in the System Settings page in the web UI.

## 🔧 Configuration Variables

All settings can be configured via environment variables (in a `.env` file or Docker environment) or through the web UI after the first launch.

| Variable           | Description                                                        |
| :----------------- | :----------------------------------------------------------------- |
| `BOT_TOKEN`        | **Required.** Your Telegram bot token.                             |
| `CHANNEL_NAME`     | **Required.** The ID of your private channel/group.                |
| `PASS_WORD`        | The admin password for the web interface. If empty, no authentication is required. |
| `BASE_URL`         | The public-facing URL of your instance (e.g., `https://tg.example.com`). Optional, but recommended for accuracy when sharing links from the bot. |
| `PICGO_API_KEY`    | The API key for PicGo uploads. Set a secure, random string.        |

## 🙏 Acknowledgments & Fork Information

This project is a fork of and has been significantly enhanced from the original **[ispace-top/tgstate-python](https://github.com/ispace-top/tgstate-python)** repository.

Our heartfelt thanks go to the original author for creating an excellent foundation. This fork aims to continue the development with new features, bug fixes, and a slightly different architectural direction.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.