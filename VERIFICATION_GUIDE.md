# WebProbe API 验证指南

## 🎯 目标

验证阶段 5 FastAPI 应用是否成功创建并可访问

---

## 方案一：使用 PostgreSQL (生产环境配置)

### 前提条件

- Docker 已安装并运行
- Python 虚拟环境已激活

### 步骤

#### 1. 启动 PostgreSQL

```bash
./start_postgres.sh
```

或手动执行：

```bash
docker run -d \
  --name webprobe-postgres \
  -e POSTGRES_USER=webprobe \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=webprobe_db \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 2. 确认 .env 文件存在

```bash
cat .env
```

应该看到 `DATABASE_URL=postgresql://webprobe:secret@localhost:5432/webprobe_db`

#### 3. 初始化数据库

```bash
python scripts/init_db.py
```

预期输出：

```
Creating database tables...
✅ Database tables created successfully!
```

#### 4. 启动 FastAPI 应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

预期输出：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 5. 验证 API（打开新终端窗口）

**测试 1: 访问根端点**

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

**测试 2: 健康检查**

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

**测试 3: 创建任务**

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
  "updated_at": "2025-10-16T...",
  ...
}
```

**测试 4: 查询任务**

```bash
# 使用上面返回的 task_id
curl http://localhost:8000/api/v1/tasks/{task_id}
```

**测试 5: 列出所有任务**

```bash
curl http://localhost:8000/api/v1/tasks
```

**测试 6: 访问 API 文档**
在浏览器中打开：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 方案二：快速验证 (使用 SQLite，无需 Docker)

### 适用场景

- Docker 未安装或未运行
- 只想快速测试 API 功能
- 开发环境测试

### 步骤

#### 1. 使用测试配置

```bash
cp .env.test .env
```

#### 2. 初始化数据库

```bash
python scripts/init_db.py
```

#### 3. 启动 FastAPI 应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. 验证 API

按照方案一的步骤 5 进行验证

#### 快捷命令

```bash
# 一键启动测试
./quick_test.sh
```

---

## 📊 验证清单

完成以下检查项即表示阶段 5 验证成功：

- [ ] ✅ FastAPI 应用成功启动，无报错
- [ ] ✅ 访问 `http://localhost:8000/` 返回欢迎信息
- [ ] ✅ 访问 `http://localhost:8000/docs` 显示 Swagger UI
- [ ] ✅ 健康检查端点 `/api/v1/health` 返回 healthy
- [ ] ✅ 可以成功创建任务 (POST `/api/v1/tasks`)
- [ ] ✅ 可以查询单个任务 (GET `/api/v1/tasks/{id}`)
- [ ] ✅ 可以列出所有任务 (GET `/api/v1/tasks`)
- [ ] ✅ API 文档自动生成并可访问

---

## 🐛 常见问题

### 1. 端口被占用

错误: `Address already in use`

解决:

```bash
# 查找占用端口的进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
# 或使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 2. 数据库连接失败

错误: `could not connect to server`

解决:

```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres
# 如果未运行，启动它
docker start webprobe-postgres
# 等待几秒后重试
```

### 3. 模块导入错误

错误: `ModuleNotFoundError`

解决:

```bash
# 确保在项目根目录
pwd
# 确保虚拟环境已激活
which python
# 重新安装依赖
pip install -r requirements.txt
```

### 4. Pydantic ValidationError

错误: `validation error for Settings`

解决:

```bash
# 确保 .env 文件存在
ls -la .env
# 检查 .env 文件内容
cat .env
# 确保所有必需字段都已填写
```

---

## 🎉 验证成功后的下一步

验证成功后，你可以：

1. **查看 API 文档**: http://localhost:8000/docs
2. **使用 Swagger UI 测试 API**: 在文档页面直接测试
3. **进入阶段 6**: Celery 集成 (参考 tasks.md)
4. **提交代码**:
   ```bash
   git add .
   git commit -m "完成阶段5: 基础 API 实现"
   ```

---

## 📝 测试数据示例

### 创建多个测试任务

```bash
# 任务 1
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# 任务 2
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'

# 任务 3
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://python.org"}'
```

### 查询带分页的任务列表

```bash
# 第一页，每页 2 条
curl "http://localhost:8000/api/v1/tasks?skip=0&limit=2"

# 第二页
curl "http://localhost:8000/api/v1/tasks?skip=2&limit=2"
```

### 按状态过滤任务

```bash
# 查询 PENDING 状态的任务
curl "http://localhost:8000/api/v1/tasks?status_filter=PENDING"
```

---

**祝验证顺利！如有问题请查看常见问题部分或检查服务器日志。** 🚀
