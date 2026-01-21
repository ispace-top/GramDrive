# 🔧 紧急修复：无限重定向和镜像命名问题

## ✅ 已修复的两个问题

### 问题 1: Docker 镜像命名错误 ✅

**问题描述**: 构建的镜像名为 `tgstate-python-gramdrive`，应该是 `gramdrive`

**修复**: 在 `docker-compose.yml` 中添加 `image` 字段

```yaml
services:
  gramdrive:
    image: gramdrive:latest  # ✅ 显式指定镜像名
    build:
      context: .
      dockerfile: Dockerfile
```

---

### 问题 2: 无限重定向导致 Internal Server Error ✅

**问题描述**:
- 访问 `/` 时不断 `307 Temporary Redirect`
- 最终显示 `Internal Server Error`
- 日志显示大量重定向请求

**根本原因**:
`.env.example` 中的占位符值（如 `your_secret_password`、`your_telegram_bot_token`）被认为是"有效配置"，导致：

1. `PASS_WORD=your_secret_password` → 被认为已设置密码
2. 中间件判断"已设置密码" → 要求登录
3. 但用户没有真实密码 → 无法登录
4. 陷入重定向循环

**修复方案**:

在 `app/core/config.py` 中添加占位符过滤逻辑：

```python
def get_app_settings() -> dict:
    # 定义占位符列表
    TOKEN_PLACEHOLDERS = {
        "your_telegram_bot_token",
        "your_bot_token",
        ...
    }
    PASSWORD_PLACEHOLDERS = {
        "your_secret_password",
        "your_password",
        ...
    }

    def filter_placeholder(value, placeholders):
        """过滤占位符，如果是占位符则返回 None"""
        if not value:
            return None
        value_str = str(value).strip()
        if not value_str or value_str.lower() in placeholders:
            return None
        return value_str

    return {
        "BOT_TOKEN": filter_placeholder(..., TOKEN_PLACEHOLDERS),
        "PASS_WORD": filter_placeholder(..., PASSWORD_PLACEHOLDERS),
        ...
    }
```

同时更新 `get_active_password()` 函数，确保占位符密码被视为"未设置"。

---

## 🚀 应用修复

### 步骤 1: 停止并清理旧容器

```bash
# 停止容器
docker compose down

# 删除旧镜像（可选，如果想清理的话）
docker rmi tgstate-python-gramdrive 2>/dev/null || true
```

### 步骤 2: 重新构建并启动

```bash
docker compose up -d --build
```

### 步骤 3: 验证修复

```bash
# 查看日志
docker compose logs -f gramdrive
```

**期望输出**:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**不应该看到**:
- ❌ `ERROR: 启动机器人失败: The token 'your_telegram_bot_token' was rejected`
- ❌ 大量 `307 Temporary Redirect` 日志

**应该看到**:
- ✅ `WARNING: BOT_TOKEN 未配置，机器人功能将不可用`（这是正常的）

### 步骤 4: 访问 Web 界面

打开浏览器：**http://localhost:8000**

**期望行为**:
1. 首次访问 → 重定向到 `/welcome` 引导页
2. 引导页显示"欢迎使用 Gram Drive"
3. 可以进入设置页面配置 Token

**不应该出现**:
- ❌ 无限重定向
- ❌ Internal Server Error
- ❌ 白屏/无响应

---

## 🎯 配置流程（修复后）

### 方式 1: Web 界面配置（推荐）⭐

1. **访问引导页**
   http://localhost:8000 → 自动重定向到 `/welcome`

2. **进入设置**
   点击"进入设置"或直接访问 http://localhost:8000/settings

3. **配置必要信息**
   - **Bot Token**: 从 [@BotFather](https://t.me/BotFather) 获取
   - **Channel Name**: 你的频道 ID（如 `@your_channel` 或 `-1001234567890`）
   - **Password**: 设置访问密码（可选但推荐）

4. **保存并应用**
   点击"保存并应用"按钮 → Bot 自动启动

5. **开始使用**
   刷新页面 → 文件上传功能可用

### 方式 2: 编辑 .env 文件

如果你仍想使用 `.env` 文件：

```bash
# 编辑 .env
notepad .env  # Windows
nano .env     # Linux/macOS
```

**重要**: 必须使用真实值，不能使用占位符！

```env
# ✅ 正确示例
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_NAME=@myfilestorage
PASS_WORD=MySecurePassword123

# ❌ 错误示例（会被过滤掉）
BOT_TOKEN=your_telegram_bot_token
CHANNEL_NAME=@your_channel
PASS_WORD=your_secret_password
```

然后重启：
```bash
docker compose restart
```

---

## 📊 过滤的占位符列表

修复后，以下占位符值会被自动过滤（视为未配置）：

### BOT_TOKEN
- `your_telegram_bot_token`
- `your_bot_token`
- `bot_token`
- `token`

### CHANNEL_NAME
- `@your_telegram_channel_or_your_id`
- `@your_channel`
- `your_channel`
- `channel_name`

### PASS_WORD
- `your_secret_password`
- `your_password`
- `password`
- `change_me`
- `changeme`

### PICGO_API_KEY
- `your_picgo_api_key`
- `your_api_key`
- `api_key`

---

## 🧪 验证测试

### 测试 1: 占位符过滤

```bash
# 确保 .env 中有占位符
grep "your_secret_password" .env

# 启动容器
docker compose up -d

# 访问主页（应该重定向到 /welcome，不是死循环）
curl -I http://localhost:8000

# 期望结果: HTTP/1.1 307 Temporary Redirect → Location: /welcome
```

### 测试 2: 引导页访问

```bash
# 访问引导页
curl http://localhost:8000/welcome

# 期望结果: 返回 HTML（状态码 200）
```

### 测试 3: 设置页面

```bash
# 访问设置页
curl http://localhost:8000/settings

# 期望结果: 返回 HTML（状态码 200）
```

### 测试 4: 镜像名称

```bash
# 查看镜像
docker images | grep gramdrive

# 期望输出:
# gramdrive    latest    <image-id>    <time>    <size>
```

---

## 🎉 修复完成！

现在你可以：

1. ✅ **使用 `.env.example` 直接启动**（占位符会被自动过滤）
2. ✅ **通过 Web 界面配置所有设置**（推荐）
3. ✅ **正确的镜像命名** (`gramdrive:latest`)
4. ✅ **无限重定向问题已解决**
5. ✅ **友好的引导流程**

### 快速启动命令

```bash
# 完整清理并重新部署
docker compose down
docker compose up -d --build

# 访问服务
open http://localhost:8000  # macOS
start http://localhost:8000  # Windows
xdg-open http://localhost:8000  # Linux
```

---

## 📝 修改的文件

1. `docker-compose.yml` - 添加 `image: gramdrive:latest`
2. `app/core/config.py` - 添加占位符过滤逻辑

**未修改的文件**（已在之前修复）:
- `app/api/files.py` - FastAPI 废弃警告 + 批量删除
- `app/bot_handler.py` - Bot 创建日志级别

---

享受你的 Gram Drive 吧！🚀
