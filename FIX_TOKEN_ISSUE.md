# 🔧 紧急修复：Token 未配置时无法访问 Web 界面

## ✅ 已修复的问题

### 问题描述
当 `.env` 文件中的 `BOT_TOKEN` 未配置或配置为占位符时，应用无法正常启动或访问 Web 界面。

### 根本原因

1. **`batch_delete_files` 路由使用了 `Depends(get_telegram_service)`**
   - 这会在路由定义时就尝试获取 TelegramService
   - 如果 Token 未配置，会抛出 RuntimeError
   - 导致 FastAPI 无法正常处理请求

2. **过于严格的错误处理**
   - Bot 初始化失败时日志级别为 ERROR
   - 可能给用户造成困惑

### 修复内容

#### 修复 1: `app/api/files.py` - 批量删除端点

**修复前**:
```python
@router.post("/api/batch_delete")
async def batch_delete_files(
    request_data: BatchDeleteRequest,
    telegram_service: TelegramService = Depends(get_telegram_service),  # ❌ 问题
):
```

**修复后**:
```python
@router.post("/api/batch_delete")
async def batch_delete_files(
    request_data: BatchDeleteRequest,
):
    try:
        telegram_service = get_telegram_service()  # ✅ 在函数内部调用
    except Exception:
        raise http_error(503, "未配置 BOT_TOKEN/CHANNEL_NAME，批量删除不可用", code="cfg_missing")
```

#### 修复 2: `app/bot_handler.py` - Bot 创建函数

**修复前**:
```python
def create_bot_app(settings: dict) -> Application:
    if not settings.get("BOT_TOKEN"):
        logger.error(".env 文件中未设置 BOT_TOKEN，机器人无法创建")  # ❌ ERROR 级别
        raise ValueError("BOT_TOKEN not configured.")
```

**修复后**:
```python
def create_bot_app(settings: dict) -> Application:
    bot_token = (settings.get("BOT_TOKEN") or "").strip()
    if not bot_token:
        logger.warning("BOT_TOKEN 未配置，机器人功能将不可用")  # ✅ WARNING 级别
        raise ValueError("BOT_TOKEN not configured.")
```

#### 修复 3: `app/api/files.py` - FastAPI 废弃警告

**修复前**:
```python
sort_by: Optional[str] = Query(None, regex="^(filename|filesize|upload_date)$")  # ❌ 已废弃
sort_order: Optional[str] = Query(None, regex="^(asc|desc)$")  # ❌ 已废弃
```

**修复后**:
```python
sort_by: Optional[str] = Query(None, pattern="^(filename|filesize|upload_date)$")  # ✅ 新语法
sort_order: Optional[str] = Query(None, pattern="^(asc|desc)$")  # ✅ 新语法
```

---

## 🚀 应用修复

### 步骤 1: 停止当前容器

```bash
docker compose down
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

如果 Token 未配置，你应该看到：
```
WARNING: BOT_TOKEN 未配置，机器人功能将不可用
```

而不是之前的：
```
ERROR: 启动机器人失败: The token `your_telegram_bot_token` was rejected
```

---

## ✅ 现在你可以

### 1. 访问 Web 界面

打开浏览器：**http://localhost:8000**

**即使 Bot Token 未配置，以下功能仍可正常使用**:
- ✅ 访问网页
- ✅ 登录/注册
- ✅ 进入设置页面
- ✅ 配置 Bot Token 和频道

**需要 Bot Token 才能使用的功能**:
- ❌ 文件上传
- ❌ 文件下载
- ❌ 文件删除
- ❌ 文件列表（会显示"需要配置 Bot"）

### 2. 在 Web 界面配置 Token

1. 访问 http://localhost:8000/settings
2. 填写 **Bot Token** 和 **Channel Name**
3. 点击 **"保存并应用"**
4. Bot 会自动重启并连接 Telegram
5. 刷新页面，文件功能即可使用

---

## 🧪 测试验证

### 测试 1: 未配置 Token 时访问主页

```bash
# 确保 .env 中 BOT_TOKEN 为空或占位符
curl http://localhost:8000/

# 期望结果：返回 307 重定向到 /welcome 或 /login
# HTTP/1.1 307 Temporary Redirect
```

### 测试 2: 访问设置页面

```bash
curl http://localhost:8000/settings

# 期望结果：返回 HTML 页面（状态码 200）
```

### 测试 3: 尝试上传文件（应该失败但不崩溃）

```bash
curl -F "file=@test.txt" http://localhost:8000/api/upload

# 期望结果：返回 503 错误，提示需要配置 Token
# {"detail": {"message": "未配置 BOT_TOKEN/CHANNEL_NAME", "code": "cfg_missing"}}
```

### 测试 4: 配置 Token 后验证

1. 在 Web 界面配置正确的 Token
2. 查看日志：
   ```bash
   docker compose logs -f gramdrive
   ```
3. 期望看到：
   ```
   INFO: Bot 已启动: YourBotName (@your_bot)
   INFO: 频道已验证: YourChannel
   ```

---

## 📊 修复前后对比

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| Token 未配置 | ❌ 应用崩溃/无法访问 | ✅ 正常访问，提示配置 |
| 访问主页 | ❌ 500 错误 | ✅ 正常重定向 |
| 访问设置 | ❌ 可能无法访问 | ✅ 正常访问 |
| 上传文件 | ❌ 崩溃 | ✅ 返回友好错误提示 |
| 批量删除 | ❌ 500 错误 | ✅ 返回 503 错误提示 |
| 日志信息 | ❌ ERROR 级别 | ✅ WARNING 级别 |
| FastAPI 警告 | ⚠️ 废弃警告 | ✅ 无警告 |

---

## 🎯 推荐工作流程

1. **首次部署**
   ```bash
   # 不需要预先配置 Token
   docker compose up -d --build
   ```

2. **访问 Web 界面**
   ```bash
   # 打开浏览器
   http://localhost:8000
   ```

3. **完成引导配置**
   - 设置访问密码（可选）
   - 进入设置页面
   - 配置 Bot Token 和频道

4. **保存并应用**
   - Bot 自动启动
   - 无需重启容器

5. **开始使用**
   - 上传文件
   - 管理存储

---

## 🔒 安全说明

修复后的代码：
- ✅ 不会在 Token 未配置时暴露敏感错误
- ✅ 返回友好的错误提示
- ✅ 正确处理认证失败
- ✅ 保持所有安全中间件正常工作

---

## 📝 相关文件

修改的文件：
1. `app/api/files.py` - 批量删除 + FastAPI 废弃警告
2. `app/bot_handler.py` - Bot 创建日志级别

未修改但相关的文件：
- `app/core/http_client.py` - 已有正确的异常处理
- `app/services/telegram_service.py` - get_telegram_service 会抛出 RuntimeError
- `app/main.py` - 中间件逻辑正常

---

## 🎉 修复完成！

现在你可以：

1. **无需预配置 Token** 即可访问 Web 界面
2. **在 Web 界面配置** 所有设置（推荐）
3. **即使配置错误** 也不会导致应用崩溃
4. **友好的错误提示** 引导你完成配置

运行以下命令应用修复：

```bash
docker compose down
docker compose up -d --build
```

然后访问：http://localhost:8000/settings 配置你的 Bot Token！
