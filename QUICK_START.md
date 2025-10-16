# 🚀 快速开始验证

## ✅ 已完成配置

1. ✅ `.env` 文件已创建，包含 Render PostgreSQL 连接
2. ✅ `app/config.py` 已修改，Redis/Celery 为可选
3. ✅ 数据库和 API 代码已就绪

---

## 📝 验证步骤（在你的终端中执行）

### 方式 1：使用验证脚本（推荐）

```bash
./verify_setup.sh
```

如果一切正常，会显示：

```
✅ 所有前置检查已通过！
```

然后启动服务器：

```bash
uvicorn app.main:app --reload
```

---

### 方式 2：手动验证

#### 步骤 1：测试配置

```bash
python -c "from app.config import settings; print('✅ 配置OK')"
```

#### 步骤 2：初始化数据库

```bash
python scripts/init_db.py
```

应该看到：

```
Creating database tables...
✅ Database tables created successfully!
```

#### 步骤 3：启动应用

```bash
uvicorn app.main:app --reload
```

应该看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 步骤 4：测试 API（新终端窗口）

**测试 1 - 根端点：**

```bash
curl http://localhost:8000/
```

预期响应：

```json
{
  "message": "Welcome to WebProbe API",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

**测试 2 - 健康检查：**

```bash
curl http://localhost:8000/api/v1/health
```

预期响应：

```json
{
  "status": "healthy",
  "service": "WebProbe",
  "database": "connected"
}
```

**测试 3 - 创建任务：**

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

预期响应：

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "url": "https://example.com",
  "status": "PENDING",
  "created_at": "2025-10-16T...",
  ...
}
```

**测试 4 - 查询任务：**

```bash
curl http://localhost:8000/api/v1/tasks
```

**测试 5 - 访问 API 文档：**

在浏览器中打开：

```
http://localhost:8000/docs
```

---

## 🎯 验证清单

完成以下项目表示阶段 5 验证成功：

- [ ] ✅ `.env` 文件存在且包含正确的 DATABASE_URL
- [ ] ✅ 配置可以正常加载（无报错）
- [ ] ✅ 数据库表创建成功
- [ ] ✅ FastAPI 应用成功启动
- [ ] ✅ 根端点 `/` 可访问
- [ ] ✅ 健康检查 `/api/v1/health` 返回 healthy
- [ ] ✅ 可以创建任务（POST `/api/v1/tasks`）
- [ ] ✅ 可以查询任务（GET `/api/v1/tasks`）
- [ ] ✅ Swagger UI 文档可访问（`/docs`）

---

## 🐛 常见问题

### 问题 1：数据库连接失败

**错误：**

```
could not connect to server
```

**解决：**

1. 检查 Render Dashboard，确认数据库状态为 "Available"
2. 确认使用的是 External Database URL
3. 检查网络连接
4. 尝试在 URL 后添加 `?sslmode=require`

### 问题 2：端口被占用

**错误：**

```
Address already in use
```

**解决：**

```bash
# 查找占用进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 问题 3：模块导入错误

**错误：**

```
ModuleNotFoundError: No module named 'app'
```

**解决：**

```bash
# 确认在项目根目录
pwd
# 应该显示：/Users/wangsiting/WebProb_intern/-WebProbe-1

# 确认虚拟环境已激活
which python

# 重新安装依赖
pip install -r requirements.txt
```

---

## 🎉 验证成功后

恭喜完成阶段 5！你现在可以：

1. **体验 API 功能**

   - 在 Swagger UI 中测试各种端点
   - 创建多个测试任务
   - 查看数据库中的数据

2. **进入下一阶段**

   - 查看 `tasks.md` 中的阶段 6：Celery 集成
   - 到时需要配置 Redis 和 Celery

3. **提交代码**
   ```bash
   git add .
   git commit -m "完成阶段5: FastAPI 基础 API 实现"
   git push
   ```

---

## 📚 相关文档

- `RENDER_SETUP.md` - Render PostgreSQL 详细配置
- `VERIFICATION_GUIDE.md` - 完整验证指南
- `tasks.md` - 完整 MVP 任务列表
- `architecture.md` - 项目架构设计

---

**现在就开始验证吧！** 🚀

```bash
# 一键验证
./verify_setup.sh

# 启动应用
uvicorn app.main:app --reload
```
