# ⚙️ 环境变量配置指南

## 🔴 重要提示

**在首次启动前，必须配置正确的环境变量！**

容器已构建成功，但需要配置真实的 Telegram Bot Token 才能正常运行。

---

## 📝 配置步骤

### 步骤 1: 停止当前容器

```bash
docker compose down
```

### 步骤 2: 编辑 .env 文件

```bash
# Windows
notepad .env

# Linux/macOS
nano .env
# 或
vim .env
```

### 步骤 3: 填写真实配置

#### 必填项：

1. **BOT_TOKEN** - 从 [@BotFather](https://t.me/BotFather) 获取
   ```env
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

2. **CHANNEL_NAME** - 你的 Telegram 频道或用户 ID
   ```env
   # 公开频道
   CHANNEL_NAME=@your_channel_name

   # 或私有频道 ID
   CHANNEL_NAME=-1001234567890

   # 或你的用户 ID
   CHANNEL_NAME=123456789
   ```

#### 可选项：

3. **PASS_WORD** - Web 界面访问密码（留空则无需密码）
   ```env
   PASS_WORD=your_secure_password
   ```

4. **PICGO_API_KEY** - PicGo 上传接口密钥（留空则无需密钥）
   ```env
   PICGO_API_KEY=your_picgo_api_key
   ```

5. **BASE_URL** - 公开访问地址（用于生成分享链接）
   ```env
   # 本地访问
   BASE_URL=http://localhost:8000

   # 公网访问
   BASE_URL=https://your-domain.com
   ```

---

## 🤖 如何获取 Bot Token

### 1. 打开 Telegram，搜索 [@BotFather](https://t.me/BotFather)

### 2. 发送 `/newbot` 创建新 Bot

```
/newbot
```

### 3. 按提示设置 Bot 名称和用户名

```
名称: My File Storage Bot
用户名: myfilestorage_bot  (必须以 _bot 结尾)
```

### 4. 复制 Token

BotFather 会返回类似这样的消息：
```
Done! Congratulations on your new bot.
Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

将这串 Token 复制到 `.env` 文件的 `BOT_TOKEN=` 后面。

---

## 📢 如何获取 Channel ID

### 方法 1: 公开频道（推荐）

1. 创建 Telegram 频道
2. 将频道设置为公开
3. 设置频道用户名（如 `myfilestorage`）
4. 在 `.env` 中填写：
   ```env
   CHANNEL_NAME=@myfilestorage
   ```

### 方法 2: 私有频道

1. 创建私有频道
2. 将你的 Bot 添加为频道管理员
3. 使用机器人获取频道 ID：
   - 搜索 [@userinfobot](https://t.me/userinfobot)
   - 转发频道中的任意消息给它
   - 它会返回频道 ID（如 `-1001234567890`）
4. 在 `.env` 中填写：
   ```env
   CHANNEL_NAME=-1001234567890
   ```

### 方法 3: 使用个人账号（私聊 Bot）

1. 使用 [@userinfobot](https://t.me/userinfobot) 获取你的用户 ID
2. 在 `.env` 中填写：
   ```env
   CHANNEL_NAME=123456789
   ```

---

## ✅ 完整配置示例

```env
# 必填项
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_NAME=@myfilestorage

# 可选项
PASS_WORD=my_secure_password_2024
PICGO_API_KEY=
BASE_URL=http://localhost:8000
```

---

## 🚀 重新启动服务

配置完成后，重新启动容器：

```bash
# 重新构建并启动
docker compose up -d --build

# 查看启动日志
docker compose logs -f
```

---

## ✅ 验证配置

### 1. 检查日志中是否有错误

```bash
docker compose logs -f gramdrive
```

**成功的日志应该包含：**
```
INFO app.core.http_client: Bot 已启动: YourBotName (@your_bot)
INFO app.core.http_client: 频道已验证: YourChannel
```

**如果看到错误：**
```
ERROR app.core.http_client: 启动机器人失败: The token `your_telegram_bot_token` was rejected
```
说明 Bot Token 配置错误。

### 2. 访问 Web 界面

打开浏览器访问：http://localhost:8000

如果配置了密码，会要求输入密码。

### 3. 测试上传文件

在 Web 界面上传一个小文件，检查：
- 文件是否出现在文件列表
- Telegram 频道/聊天中是否收到文件
- 下载链接是否有效

---

## 🐛 常见问题

### 问题 1: Token 被拒绝

```
ERROR: The token `your_telegram_bot_token` was rejected
```

**原因**: 使用了 `.env.example` 中的占位符

**解决方案**: 从 BotFather 获取真实 Token

---

### 问题 2: 频道 ID 格式错误

```
ERROR: Chat not found
```

**原因**:
- 频道 ID 格式错误
- Bot 未被添加为频道管理员（私有频道）
- 频道不存在

**解决方案**:
1. 确认频道 ID 格式正确（公开频道以 `@` 开头，私有频道为负数）
2. 确保 Bot 已被添加为频道管理员
3. 检查频道是否存在

---

### 问题 3: 环境变量未生效

**症状**: 修改 `.env` 后重启容器，配置未更新

**解决方案**:
```bash
# 完全停止容器
docker compose down

# 重新启动（会重新读取 .env）
docker compose up -d
```

---

### 问题 4: 无法在 Web 界面配置

**重要**:
- `.env` 文件中的配置优先级 **低于** 数据库中的配置
- 首次启动时，`.env` 的值会被写入数据库
- 之后可以在 Web 界面（设置页面）修改，无需重启容器

**建议流程**:
1. 首次启动前，在 `.env` 配置最基本的 `BOT_TOKEN` 和 `CHANNEL_NAME`
2. 启动容器后，在 Web 界面的 "设置" 页面修改其他配置
3. 点击 "保存并应用" 立即生效，无需重启

---

## 📚 相关链接

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [BotFather 使用指南](https://core.telegram.org/bots#botfather)
- [获取频道 ID 工具](https://t.me/userinfobot)

---

## 🔒 安全建议

1. **不要泄露 Bot Token**
   - 不要将 `.env` 文件提交到 Git
   - 不要在公开场合分享 Token

2. **定期更换密码**
   - 定期更换 Web 访问密码
   - 定期更换 PicGo API Key

3. **使用私有频道**
   - 推荐使用私有频道存储文件
   - 设置 Bot 为唯一管理员

4. **备份数据**
   - 定期备份 `./data` 目录
   - 记录所有配置信息

---

配置完成后，你的 Gram Drive 应该可以正常运行了！ 🎉
