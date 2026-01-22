# Nginx 反向代理配置指南

## 问题说明

当通过 HTTPS 反向代理访问 Gram Drive 时，可能会遇到"Mixed Content"错误：
```
Mixed Content: The page at 'https://tg.itjl.top:91/' was loaded over HTTPS,
but requested an insecure script 'http://tg.itjl.top:91/static/js/main.js?v=4.1'.
This request has been blocked; the content must be served over HTTPS.
```

## 解决方案

### 1. 标准端口配置（推荐 - 443端口）

```nginx
server {
    listen 443 ssl http2;
    server_name tg.itjl.top;

    # SSL 证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 日志
    access_log /var/log/nginx/gramdrive_access.log;
    error_log /var/log/nginx/gramdrive_error.log;

    location / {
        proxy_pass http://localhost:8000;

        # 关键配置：这些 header 让应用知道原始请求的协议
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;       # ← 最关键
        proxy_set_header X-Forwarded-Host $server_name;   # ← 也很重要

        # 支持 WebSocket（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# HTTP 自动跳转到 HTTPS
server {
    listen 80;
    server_name tg.itjl.top;
    return 301 https://$server_name$request_uri;
}
```

### 2. 非标准端口配置（如 :91）

```nginx
server {
    listen 91 ssl http2;
    server_name tg.itjl.top;

    # SSL 证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 日志
    access_log /var/log/nginx/gramdrive_access.log;
    error_log /var/log/nginx/gramdrive_error.log;

    location / {
        proxy_pass http://localhost:8000;

        # 关键配置
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;         # ← 强制指定 https
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Port 91;             # ← 指定端口

        # 支持 WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 3. Synology NAS 反向代理配置

如果你使用 Synology NAS 的内置反向代理：

1. 打开 **控制面板** > **登录门户** > **高级** > **反向代理服务器**
2. 点击 **新增**
3. 填写配置：
   - **来源**：
     - 协议：HTTPS
     - 主机名：tg.itjl.top
     - 端口：91（或你的自定义端口）
     - 启用 HSTS：✓
   - **目标**：
     - 协议：HTTP
     - 主机名：localhost
     - 端口：8000（你的 Docker 容器端口）

4. 点击 **自定义标头** > **新增**，添加以下标头：
   ```
   X-Forwarded-Proto: https
   X-Forwarded-Host: tg.itjl.top
   X-Real-IP: $remote_addr
   X-Forwarded-For: $proxy_add_x_forwarded_for
   ```

5. 在 **WebSocket** 标签中启用 WebSocket

## 验证配置

### 1. 测试 Nginx 配置

```bash
# 测试配置文件语法
sudo nginx -t

# 如果测试通过，重新加载配置
sudo nginx -s reload
```

### 2. 检查 Headers

使用浏览器开发者工具（F12），在 Network 标签中检查 `main.js` 的请求：
- ✅ URL 应该是 `https://tg.itjl.top:91/static/js/main.js`（HTTPS）
- ❌ 不应该是 `http://tg.itjl.top:91/static/js/main.js`（HTTP）

或使用 curl 命令测试：
```bash
curl -I https://tg.itjl.top:91/
```

检查响应头中是否有：
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 部署步骤

### 完整的重新部署流程

```bash
# 1. SSH 登录到你的 NAS
ssh user@nas-ip

# 2. 进入项目目录
cd /volume1/docker/tgstate-python  # 根据你的实际路径调整

# 3. 拉取最新代码（包含修复）
git pull origin main

# 4. 停止并删除旧容器
docker-compose down

# 5. 删除旧镜像（强制重建）
docker rmi gramdrive:latest

# 6. 清除 Docker 构建缓存
docker builder prune -f

# 7. 重新构建（不使用缓存）
docker-compose build --no-cache

# 8. 启动容器
docker-compose up -d

# 9. 查看日志，确认启动成功
docker-compose logs -f
```

### 验证修复

1. 打开浏览器，按 `F12` 打开开发者工具
2. 访问 `https://tg.itjl.top:91/`
3. 在 Console 标签中，不应该再有 "Mixed Content" 错误
4. 在 Network 标签中，检查 `main.js` 的 URL 是 HTTPS 的
5. 测试分类 Tab 是否可以正常点击切换

## 常见问题

### Q: 为什么需要 `X-Forwarded-Proto` header？

A: 当请求通过反向代理到达应用时，应用看到的是 HTTP 请求（因为 Nginx → Docker 之间是 HTTP）。`X-Forwarded-Proto` 告诉应用原始请求实际上是 HTTPS，这样应用在生成 URL 时就会使用 HTTPS。

### Q: Synology NAS 的内置反向代理是否足够？

A: 是的，但需要确保在"自定义标头"中添加 `X-Forwarded-Proto: https`。如果没有这个选项，建议使用 Docker 部署 Nginx。

### Q: 是否需要修改 Docker Compose 配置？

A: 不需要。修复已经在应用代码中完成（通过 `ProxyFixMiddleware`），只需要确保反向代理正确设置 headers。

### Q: 修复后仍有问题怎么办？

1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 使用无痕模式测试
3. 检查 Docker 日志：`docker logs gramdrive`
4. 检查 Nginx 日志：`tail -f /var/log/nginx/gramdrive_error.log`

## 参考资料

- [FastAPI Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
- [Starlette ProxyFixMiddleware](https://www.starlette.io/middleware/#proxyfixmiddleware)
- [MDN: Mixed Content](https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content)
