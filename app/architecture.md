我来帮你生成完整的 WebProbe 项目架构设计文档。让我先看一下项目的当前状态，然后为你创建一个详细的架构文档。

[4 tools called]

基于你的项目构想，我为你生成了完整的 **WebProbe** 架构设计文档。以下是完整的 Markdown 格式文档，你可以将其复制到 `architecture.md` 文件中：

```markdown
# WebProbe 架构设计文档

## 项目概述

**项目名称**: WebProbe (网络探针)  
**核心功能**: 异步Web内容抓取与分析平台  
**技术栈**: FastAPI + Celery + Redis + PostgreSQL + Docker

---

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client/User                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP Requests
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (Port 8000)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   API Routes │  │  Middleware  │  │   Schemas    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────┬──────────────────────┬────────────────────┬──────────────┘
      │                      │                    │
      │ DB Operations        │ Task Queue         │ Cache Check
      ▼                      ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PostgreSQL   │    │    Redis     │    │    Redis     │
│   Database   │    │   (Broker)   │    │   (Cache)    │
│              │    │              │    │              │
│ - tasks      │    │ - Messages   │    │ - Results    │
│ - results    │    │ - Queue      │    │ - TTL Data   │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                           │ Consume Tasks
                           ▼
                  ┌──────────────────┐
                  │  Celery Worker   │
                  │                  │
                  │ - scrape_task    │
                  │ - parse_task     │
                  │ - analyze_task   │
                  └──────────────────┘
                           │
                           │ HTTP Requests
                           ▼
                    [External Websites]
```

---

## 2. 项目文件与文件夹结构

```
WebProbe/
├── app/                              # 应用核心代码
│   ├── __init__.py                   # 包初始化文件
│   ├── main.py                       # FastAPI 应用入口
│   ├── config.py                     # 配置管理（数据库、Redis、Celery等）
│   │
│   ├── api/                          # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/                       # API 版本控制
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tasks.py         # 任务相关的API端点
│   │   │   │   └── health.py        # 健康检查端点
│   │   │   └── dependencies.py      # API依赖注入
│   │   └── router.py                # 路由聚合
│   │
│   ├── models/                       # 数据模型层（ORM）
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy Base
│   │   ├── task.py                  # Task 模型
│   │   └── result.py                # Result 模型
│   │
│   ├── schemas/                      # Pydantic 数据模式（请求/响应）
│   │   ├── __init__.py
│   │   ├── task.py                  # Task 请求/响应模式
│   │   └── result.py                # Result 模式
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── task_service.py          # 任务管理服务
│   │   ├── cache_service.py         # 缓存服务
│   │   └── scraper_service.py       # 爬虫核心逻辑
│   │
│   ├── repositories/                 # 数据访问层（Repository模式）
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础Repository
│   │   └── task_repository.py       # Task数据访问
│   │
│   ├── celery_app/                   # Celery 配置与任务
│   │   ├── __init__.py
│   │   ├── celery_config.py         # Celery 配置
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── scrape_task.py       # 网页抓取任务
│   │   │   └── analysis_task.py     # 内容分析任务
│   │   └── worker.py                # Worker 入口
│   │
│   ├── core/                         # 核心工具与配置
│   │   ├── __init__.py
│   │   ├── database.py              # 数据库连接与会话管理
│   │   ├── redis_client.py          # Redis 客户端
│   │   ├── security.py              # 安全相关（如果需要认证）
│   │   └── logging.py               # 日志配置
│   │
│   └── utils/                        # 工具函数
│       ├── __init__.py
│       ├── parser.py                # HTML解析工具
│       └── validators.py            # 数据验证工具
│
├── tests/                            # 测试代码
│   ├── __init__.py
│   ├── conftest.py                  # Pytest 配置与 fixtures
│   ├── unit/                        # 单元测试
│   │   ├── __init__.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/                 # 集成测试
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_tasks.py
│   └── e2e/                         # 端到端测试
│       ├── __init__.py
│       └── test_workflow.py
│
├── migrations/                       # 数据库迁移（Alembic）
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── docker/                           # Docker 相关文件
│   ├── Dockerfile.web               # Web应用 Dockerfile
│   ├── Dockerfile.worker            # Celery Worker Dockerfile
│   └── nginx.conf                   # Nginx 配置（如果需要）
│
├── scripts/                          # 辅助脚本
│   ├── init_db.py                   # 数据库初始化
│   ├── run_tests.sh                 # 测试运行脚本
│   └── seed_data.py                 # 测试数据种子
│
├── .env.example                      # 环境变量示例
├── .env                              # 环境变量（不提交到Git）
├── .gitignore                        # Git 忽略文件
├── .dockerignore                     # Docker 忽略文件
├── docker-compose.yml                # Docker Compose 配置
├── docker-compose.dev.yml            # 开发环境配置
├── requirements.txt                  # Python 依赖
├── requirements-dev.txt              # 开发依赖
├── pyproject.toml                    # 项目配置（Poetry/Black/Ruff）
├── pytest.ini                        # Pytest 配置
├── alembic.ini                       # Alembic 配置
├── README.md                         # 项目说明
└── architecture.md                   # 本架构文档
```

---

## 3. 各模块详细说明

### 3.1 FastAPI Application (`app/main.py`)

**作用**:
- 应用主入口
- 初始化 FastAPI 实例
- 注册路由
- 配置中间件（CORS、日志等）
- 生命周期事件（启动/关闭时的数据库连接等）

**关键功能**:
```python
- 创建 FastAPI app 实例
- 注册 API 路由
- 配置 CORS、Gzip 等中间件
- 异常处理器
- 启动/关闭事件处理
```

---

### 3.2 API 路由层 (`app/api/`)

**作用**: 定义所有 HTTP 端点

**核心端点**:

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/tasks` | 创建新的抓取任务 |
| GET | `/api/v1/tasks/{task_id}` | 查询任务状态和结果 |
| GET | `/api/v1/tasks` | 列出所有任务（分页） |
| DELETE | `/api/v1/tasks/{task_id}` | 删除任务 |
| GET | `/api/v1/health` | 健康检查 |

**请求/响应示例**:

```json
// POST /api/v1/tasks
{
  "url": "https://example.com"
}

// Response
{
  "task_id": "uuid-xxx-xxx",
  "status": "PENDING",
  "created_at": "2025-10-15T10:00:00Z"
}
```

---

### 3.3 数据模型层 (`app/models/`)

**作用**: 定义数据库表结构（SQLAlchemy ORM）

**核心模型**:

#### Task 模型
```python
class Task:
    id: UUID (Primary Key)
    url: String (Index)
    status: Enum [PENDING, PROCESSING, SUCCESS, FAILED]
    created_at: DateTime
    updated_at: DateTime
    started_at: DateTime (nullable)
    completed_at: DateTime (nullable)
    error_message: String (nullable)
    result_id: UUID (Foreign Key, nullable)
```

#### Result 模型
```python
class Result:
    id: UUID (Primary Key)
    task_id: UUID (Foreign Key)
    title: String
    description: String
    links: JSONB (PostgreSQL JSON 类型)
    text_content: Text
    metadata: JSONB
    scraped_at: DateTime
```

---

### 3.4 Schemas (`app/schemas/`)

**作用**: 定义 API 请求/响应的数据验证模式（Pydantic）

**核心 Schema**:
```python
- TaskCreate: 创建任务时的请求体
- TaskResponse: 任务查询的响应
- TaskStatus: 任务状态枚举
- ResultResponse: 抓取结果的响应
```

---

### 3.5 服务层 (`app/services/`)

**作用**: 封装业务逻辑，解耦 API 层和数据访问层

#### `task_service.py`
- 创建任务
- 查询任务
- 更新任务状态
- 调用 Celery 任务

#### `cache_service.py`
- Redis 缓存读写
- 缓存键管理
- TTL 策略
- 缓存命中率统计

#### `scraper_service.py`
- HTTP 请求封装
- HTML 解析
- 数据提取（标题、链接、正文）
- 异常处理

---

### 3.6 数据访问层 (`app/repositories/`)

**作用**: 数据库操作的统一接口（Repository 模式）

**优点**:
- 业务逻辑与数据访问解耦
- 易于测试（可以 Mock）
- 符合 SOLID 原则

```python
class TaskRepository:
    - create(task_data) -> Task
    - get_by_id(task_id) -> Task
    - update_status(task_id, status) -> Task
    - list_tasks(skip, limit) -> List[Task]
```

---

### 3.7 Celery 任务 (`app/celery_app/`)

**作用**: 异步任务处理

#### 主要任务

**`scrape_task.py`**:
```python
@celery_app.task(bind=True, max_retries=3)
def scrape_website_task(self, task_id: str, url: str):
    """
    1. 更新任务状态为 PROCESSING
    2. 使用 requests + BeautifulSoup 抓取网页
    3. 解析 HTML，提取：
       - 标题 (title)
       - 所有链接 (links)
       - 正文内容 (text)
    4. 将结果存入数据库
    5. 将结果写入 Redis 缓存（TTL: 5分钟）
    6. 更新任务状态为 SUCCESS/FAILED
    """
```

**`analysis_task.py`** (可选扩展):
- 关键词提取
- 语言检测
- 链接有效性检查

---

### 3.8 核心组件 (`app/core/`)

#### `database.py`
```python
- 数据库引擎创建
- Session 工厂
- 依赖注入: get_db()
```

#### `redis_client.py`
```python
- Redis 连接池
- 客户端实例
- 依赖注入: get_redis()
```

#### `logging.py`
```python
- 统一日志格式
- 日志级别配置
- 日志文件轮转
```

---

### 3.9 配置管理 (`app/config.py`)

**作用**: 集中管理所有配置（使用 Pydantic Settings）

```python
class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # 应用
    APP_NAME: str = "WebProbe"
    DEBUG: bool = False
    
    # 缓存
    CACHE_TTL: int = 300  # 5分钟
    
    class Config:
        env_file = ".env"
```

---

## 4. 状态存储位置

| 状态类型 | 存储位置 | 持久化 | 用途 |
|---------|---------|--------|------|
| **任务元数据** | PostgreSQL (`tasks` 表) | ✅ 是 | 任务ID、URL、状态、时间戳 |
| **抓取结果** | PostgreSQL (`results` 表) | ✅ 是 | 网页内容、链接、文本 |
| **缓存结果** | Redis (Key: `cache:url:{url_hash}`) | ❌ 否 (TTL) | 减少重复抓取 |
| **任务队列** | Redis (Celery Broker) | ❌ 否 | 待处理任务消息 |
| **任务进度** | Redis (Celery Backend) | ❌ 否 (可选) | 任务执行状态 |

---

## 5. 服务连接关系

### 5.1 服务依赖图

```
FastAPI Web App
    ├── PostgreSQL (直接连接)
    ├── Redis Cache (直接连接)
    └── Redis Broker (通过 Celery 发送任务)

Celery Worker
    ├── PostgreSQL (直接连接)
    ├── Redis Broker (消费任务)
    └── Redis Cache (写入结果)
```

### 5.2 数据流

#### 创建任务流程
```
1. Client → POST /api/v1/tasks {"url": "..."}
2. FastAPI → 检查 Redis 缓存
3. 如果缓存命中 → 直接返回结果
4. 如果缓存未命中:
   a. FastAPI → PostgreSQL (插入 Task 记录)
   b. FastAPI → Celery (发送任务到 Redis 队列)
   c. FastAPI → Client (返回 task_id)
5. Celery Worker → 从 Redis 消费任务
6. Celery Worker → 抓取网页
7. Celery Worker → PostgreSQL (存储结果)
8. Celery Worker → Redis (写入缓存)
```

#### 查询任务流程
```
1. Client → GET /api/v1/tasks/{task_id}
2. FastAPI → PostgreSQL (查询 Task + Result)
3. FastAPI → Client (返回任务状态和结果)
```

---

## 6. Docker 服务配置

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: webprobe
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: webprobe_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U webprobe"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    command: celery -A app.celery_app.worker worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

  flower:  # Celery 监控面板（可选）
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    command: celery -A app.celery_app.worker flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - .env
    depends_on:
      - redis

volumes:
  postgres_data:
```

---

## 7. 技术栈与工具

| 层级 | 技术 | 用途 |
|------|------|------|
| **Web 框架** | FastAPI | RESTful API |
| **异步任务** | Celery | 后台任务处理 |
| **消息队列** | Redis | Celery Broker + Cache |
| **数据库** | PostgreSQL | 持久化存储 |
| **ORM** | SQLAlchemy | 数据库操作 |
| **迁移工具** | Alembic | 数据库版本管理 |
| **HTTP 客户端** | httpx / requests | 网页抓取 |
| **HTML 解析** | BeautifulSoup4 | 内容提取 |
| **容器化** | Docker + Compose | 服务编排 |
| **测试框架** | Pytest | 单元/集成测试 |
| **代码质量** | Black + Ruff | 格式化 + Lint |
| **类型检查** | mypy | 静态类型检查 |

---

## 8. 关键设计模式

### 8.1 Repository 模式
- 数据访问逻辑与业务逻辑分离
- 易于单元测试（可以 Mock Repository）

### 8.2 Service 模式
- 封装复杂业务逻辑
- API 层保持简洁

### 8.3 Dependency Injection
- FastAPI 的 `Depends` 机制
- 数据库会话、Redis 客户端等都通过依赖注入

### 8.4 Factory 模式
- Celery App 工厂
- Database Engine 工厂

---

## 9. 性能优化策略

### 9.1 缓存层
```python
# 缓存键策略
def get_cache_key(url: str) -> str:
    return f"cache:url:{hashlib.md5(url.encode()).hexdigest()}"

# 缓存逻辑
async def get_or_fetch(url: str):
    cache_key = get_cache_key(url)
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    # 如果未命中，发起 Celery 任务
    task = scrape_website_task.delay(url)
    return {"task_id": task.id, "status": "PENDING"}
```

### 9.2 数据库优化
```sql
-- 为高频查询字段添加索引
CREATE INDEX idx_tasks_url ON tasks(url);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### 9.3 连接池
- PostgreSQL: `pool_size=20, max_overflow=10`
- Redis: 使用连接池而非单连接

---

## 10. 监控与日志

### 10.1 日志策略
- 结构化日志（JSON 格式）
- 不同级别：DEBUG / INFO / WARNING / ERROR
- 日志聚合：可接入 ELK / Loki

### 10.2 监控指标
- API 响应时间
- 任务成功/失败率
- 缓存命中率
- 数据库连接池状态

### 10.3 健康检查
```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # 检查数据库连接
    # 检查 Redis 连接
    # 检查 Celery Worker 状态
    return {"status": "healthy"}
```

---

## 11. 扩展方向

1. **认证与授权**: 添加 JWT 或 OAuth2
2. **限流**: 使用 Redis 实现 API 限流
3. **任务优先级**: Celery 支持任务优先级队列
4. **分布式追踪**: 集成 OpenTelemetry
5. **前端界面**: 添加简单的 Web UI（Vue/React）
6. **Webhook**: 任务完成后主动通知用户
7. **内容分析**: NLP 分析、关键词提取、摘要生成

---

## 12. 开发流程

### Phase 1: 基础搭建
- [ ] 项目结构创建
- [ ] 数据库模型定义
- [ ] 基础 API 端点

### Phase 2: 异步化
- [ ] Celery 集成
- [ ] 抓取任务实现
- [ ] 状态更新机制

### Phase 3: 容器化
- [ ] Dockerfile 编写
- [ ] docker-compose 配置
- [ ] 服务编排测试

### Phase 4: 优化
- [ ] Redis 缓存实现
- [ ] 数据库索引优化
- [ ] 性能测试

### Phase 5: 测试
- [ ] 单元测试（覆盖率 >80%）
- [ ] 集成测试
- [ ] E2E 测试

---

## 13. 环境变量示例

```bash
# .env
# 数据库
DATABASE_URL=postgresql://webprobe:secret@db:5432/webprobe_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# 应用
APP_NAME=WebProbe
DEBUG=true
LOG_LEVEL=INFO

# 缓存
CACHE_TTL=300

# 抓取配置
REQUEST_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=WebProbe/1.0
```

---

## 总结

这个架构设计：
✅ **模块化**: 每个模块职责清晰  
✅ **可扩展**: 易于添加新功能  
✅ **可测试**: 依赖注入 + Repository 模式  
✅ **高性能**: 异步任务 + 缓存优化  
✅ **易部署**: Docker Compose 一键启动  
✅ **符合最佳实践**: SOLID 原则 + 设计模式

这是一个非常适合展示全栈能力的项目架构！
```

---

这份架构文档涵盖了：
- ✅ 完整的文件与文件夹结构
- ✅ 每个模块的详细作用说明
- ✅ 状态存储的明确位置
- ✅ 服务之间的连接关系和数据流
- ✅ Docker 配置示例
- ✅ 性能优化策略
- ✅ 开发流程建议

