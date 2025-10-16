# Render PostgreSQL 配置指南

## 📍 你的当前状态

- ✅ 已完成：Database 和 API
- ⏳ 待完成：Redis、Celery（阶段 6-7）

---

## 🎯 如何获取 Render PostgreSQL 连接 URL

### 步骤 1：登录 Render Dashboard

1. 访问 https://dashboard.render.com/
2. 找到你创建的 PostgreSQL 服务

### 步骤 2：获取外部连接 URL

在你的 PostgreSQL 服务页面：

1. 点击 **"Connect"** 或 **"Info"** 标签
2. 找到 **"External Database URL"** 或 **"Connection String"**
3. 复制完整的 URL

URL 格式类似：

```
postgresql://webprobe_user:很长的密码字符串@dpg-xxxxx-a.oregon-postgres.render.com/webprobe_db
```

### 步骤 3：配置 `.env` 文件

**方法 1 - 复制模板并修改：**

```bash
cp .env.stage5 .env
nano .env  # 或使用你喜欢的编辑器
```

**方法 2 - 直接创建：**

```bash
cat > .env << 'EOF'
# Database (Render PostgreSQL)
DATABASE_URL=你从Render复制的完整URL

# Application
APP_NAME=WebProbe
DEBUG=true
LOG_LEVEL=INFO

# Scraper
REQUEST_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=WebProbe/1.0

# Cache
CACHE_TTL=300
EOF
```

---

## 📝 `.env` 文件示例（阶段 5）

```bash
# ===== Render PostgreSQL =====
DATABASE_URL=postgresql://webprobe_user:abc123xyz@dpg-xxxxx-a.oregon-postgres.render.com/webprobe_db

# ===== Application =====
APP_NAME=WebProbe
DEBUG=true
LOG_LEVEL=INFO

# ===== Scraper =====
REQUEST_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=WebProbe/1.0

# ===== Cache =====
CACHE_TTL=300
```

**重要提示：**

- ✅ 只需要填写 `DATABASE_URL`
- ✅ 其他配置使用默认值即可
- ❌ 不需要填写 Redis 和 Celery（现在还没用到）

---

## 🚀 验证配置

### 1. 测试数据库连接

```bash
python -c "from app.config import settings; print('✅ 配置加载成功'); print(f'数据库: {settings.DATABASE_URL[:30]}...')"
```

### 2. 初始化数据库

```bash
python scripts/init_db.py
```

应该看到：

```
Creating database tables...
✅ Database tables created successfully!
```

### 3. 启动 API

```bash
uvicorn app.main:app --reload
```

### 4. 测试 API

```bash
# 新终端窗口
curl http://localhost:8000/api/v1/health
```

应该返回：

```json
{
  "status": "healthy",
  "service": "WebProbe",
  "database": "connected"
}
```

---

## 🔒 安全提示

### 生产环境配置

如果要部署到生产环境，需要修改：

```bash
# 生产环境 .env
DATABASE_URL=你的Render数据库URL
APP_NAME=WebProbe
DEBUG=false              # ⚠️ 改为 false
LOG_LEVEL=WARNING        # ⚠️ 减少日志
REQUEST_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=WebProbe/1.0
CACHE_TTL=300
```

### 保护敏感信息

```bash
# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 检查
git status  # .env 不应该出现在待提交列表中
```

---

## 📊 当前阶段需要的环境变量

| 变量名            | 是否必需 | 说明                       | 示例                             |
| ----------------- | -------- | -------------------------- | -------------------------------- |
| `DATABASE_URL`    | ✅ 必需  | Render PostgreSQL 连接 URL | `postgresql://user:pass@host/db` |
| `APP_NAME`        | ⚪ 可选  | 应用名称                   | `WebProbe`                       |
| `DEBUG`           | ⚪ 可选  | 调试模式                   | `true`                           |
| `LOG_LEVEL`       | ⚪ 可选  | 日志级别                   | `INFO`                           |
| `REQUEST_TIMEOUT` | ⚪ 可选  | 请求超时（秒）             | `30`                             |
| `MAX_RETRIES`     | ⚪ 可选  | 最大重试次数               | `3`                              |
| `USER_AGENT`      | ⚪ 可选  | User-Agent 头              | `WebProbe/1.0`                   |
| `CACHE_TTL`       | ⚪ 可选  | 缓存过期时间（秒）         | `300`                            |

**后续阶段才需要：**
| 变量名 | 何时需要 | 说明 |
|--------|---------|------|
| `REDIS_URL` | 阶段 7 | Redis 连接 URL |
| `CELERY_BROKER_URL` | 阶段 6 | Celery 消息代理 URL |
| `CELERY_RESULT_BACKEND` | 阶段 6 | Celery 结果存储 URL |

---

## 🐛 常见问题

### 1. 无法连接 Render 数据库

**错误：**

```
could not connect to server: Connection refused
```

**解决：**

- 检查 Render 数据库是否已启动（状态为 "Available"）
- 确认使用的是 **External Database URL**（不是 Internal）
- 检查网络连接
- 查看 Render Dashboard 的数据库日志

### 2. 认证失败

**错误：**

```
FATAL: password authentication failed
```

**解决：**

- 重新复制 Render 提供的完整 URL（包含密码）
- 确保 URL 中的特殊字符没有被转义
- 可能需要重置数据库密码

### 3. SSL 连接问题

**错误：**

```
SSL connection has been closed unexpectedly
```

**解决：**
在 `DATABASE_URL` 后添加 SSL 参数：

```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

---

## ✅ 配置完成后

完成配置后，你可以：

1. **运行验证测试**

   ```bash
   python scripts/init_db.py
   uvicorn app.main:app --reload
   ```

2. **访问 API 文档**

   - http://localhost:8000/docs

3. **创建测试任务**

   ```bash
   curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
   ```

4. **进入下一阶段**
   - 完成阶段 5 验证后，可以继续阶段 6（Celery 集成）
   - 届时再配置 Redis 相关环境变量

---

**祝配置顺利！如有问题随时问我。** 🚀
