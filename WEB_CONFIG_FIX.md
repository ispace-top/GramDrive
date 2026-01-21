# 🎯 快速修复指南：通过 Web 界面配置

## ✅ 好消息

**容器已成功启动！** 即使 Bot Token 配置错误，Web 界面仍然可以访问。

你可以直接在 Web 界面配置，无需编辑 `.env` 文件。

---

## 🚀 快速修复步骤（推荐）

### 步骤 1: 访问 Web 界面

打开浏览器访问：**http://localhost:8000**

此时服务已经运行，只是 Bot 功能暂时不可用。

---

### 步骤 2: 进入设置页面

1. 点击左侧导航栏的 **"设置"** 或 **"系统设置"**
2. 如果设置了密码，输入密码登录
   - 默认密码是 `.env` 文件中的 `PASS_WORD`
   - 如果未设置或使用了占位符，可能无法登录（见下方解决方案）

---

### 步骤 3: 填写配置

在设置页面填写：

#### 必填项：

1. **Bot Token**
   - 从 [@BotFather](https://t.me/BotFather) 获取
   - 格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **Channel Name**
   - 公开频道：`@your_channel`
   - 私有频道 ID：`-1001234567890`
   - 或你的用户 ID：`123456789`

#### 可选项：

3. **Password** - Web 访问密码
4. **PicGo API Key** - PicGo 上传密钥
5. **Base URL** - 公开访问地址
6. **下载线程数** - 多线程下载加速（1-16，推荐 4-8）

---

### 步骤 4: 保存并应用

点击右上角的 **"保存并应用"** 按钮。

配置会立即生效，Bot 会自动重启连接 Telegram。

---

### 步骤 5: 验证配置

1. **查看容器日志**：
   ```bash
   docker compose logs -f gramdrive
   ```

2. **成功的日志示例**：
   ```
   INFO: Bot 已启动: YourBotName (@your_bot)
   INFO: 频道已验证: YourChannel
   ```

3. **刷新页面**，文件上传功能应该可用了

---

## 🔓 如果无法登录设置页面

### 情况 1: 密码错误或忘记密码

**临时方案：清空密码配置**

```bash
# 停止容器
docker compose down

# 编辑 .env 文件，将 PASS_WORD 留空
# Windows
notepad .env

# Linux/macOS
nano .env
```

在 `.env` 中修改：
```env
PASS_WORD=
```

然后重启：
```bash
docker compose up -d
```

访问 http://localhost:8000/settings 无需密码即可进入设置页面。

---

### 情况 2: 完全无法访问

**方案：直接修改数据库**

```bash
# 进入容器
docker compose exec gramdrive bash

# 使用 Python 修改数据库
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/app/data/tgstate.db')
cursor = conn.cursor()

# 清空密码（可选）
cursor.execute("UPDATE app_settings SET pass_word = NULL WHERE id = 1")

# 设置 Bot Token（替换为你的真实 Token）
cursor.execute("UPDATE app_settings SET bot_token = '123456789:ABCdefGHIjklMNOpqrsTUVwxyz' WHERE id = 1")

# 设置频道名（替换为你的频道）
cursor.execute("UPDATE app_settings SET channel_name = '@your_channel' WHERE id = 1")

conn.commit()
conn.close()
print("✅ 配置已更新！")
EOF

# 退出容器
exit
```

然后重启容器：
```bash
docker compose restart
```

---

## 📋 配置优先级说明

根据项目架构（`CLAUDE.md`），配置加载优先级为：

```
数据库配置 > 环境变量 (.env) > 默认值
```

**这意味着**：

1. **首次启动**：`.env` 文件的值会写入数据库
2. **后续启动**：优先使用数据库中的配置
3. **Web 修改**：在设置页面修改会更新数据库，立即生效

**推荐工作流程**：

1. ✅ 首次部署：在 `.env` 配置基本的 `BOT_TOKEN` 和 `CHANNEL_NAME`
2. ✅ 后续调整：在 Web 界面的 "设置" 页面修改，无需重启容器
3. ✅ 高级配置：直接在 Web 界面配置新功能（如下载线程数）

---

## 🎯 现在你可以

### 方式 1: Web 界面配置（推荐）⭐

1. 访问 http://localhost:8000/settings
2. 填写正确的 Bot Token 和 Channel Name
3. 点击 "保存并应用"
4. 完成！

### 方式 2: 修改 .env 重启

1. 编辑 `.env` 文件
2. 填写正确的配置
3. `docker compose down && docker compose up -d`
4. 完成！

---

## 🔍 当前错误分析

你看到的错误：
```
ERROR: The token `your_telegram_bot_token` was rejected
```

**原因**: 容器读取了 `.env` 中的占位符文本

**影响**:
- ✅ Web 界面正常可访问
- ✅ 设置页面正常可用
- ❌ 文件上传/下载功能暂时不可用（需要配置 Bot）

**解决**: 按上面的方式 1 或方式 2 配置即可

---

## 🎉 总结

好消息是：
- ✅ 容器已成功构建和运行
- ✅ Web 服务正常工作（http://localhost:8000）
- ✅ 只需在设置页面填写正确的 Token 即可
- ✅ 无需重新构建容器

你现在可以：
1. 访问 http://localhost:8000/settings
2. 配置 Bot Token 和 Channel Name
3. 点击 "保存并应用"
4. 开始使用！🚀
