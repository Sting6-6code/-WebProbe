# WebProbe 阶段 1-5 复盘文档



---

## 📚 目录

1. [整体架构概览](#整体架构概览)
2. [阶段 1：项目基础设置](#阶段-1项目基础设置)
3. [阶段 2：数据库层](#阶段-2数据库层)
4. [阶段 3：Pydantic Schemas](#阶段-3pydantic-schemas)
5. [阶段 4：Repository 层](#阶段-4repository-层)
6. [阶段 5：基础 API](#阶段-5基础-api)
7. [设计套路总结](#设计套路总结)
8. [关键技术决策](#关键技术决策)
9. [面试准备](#面试准备)

---

## 🎯 整体架构概览

### 我们在构建什么？

一个**异步 Web 内容抓取平台**，用户可以：

1. 提交一个 URL
2. 系统异步抓取网页内容
3. 用户查询抓取结果

### 为什么选择这个架构？

```
用户请求 → FastAPI → Repository → Database
                ↓
            Celery Worker → 抓取网页 → 保存结果
```

**设计理念**：

- ✅ **分层架构**：职责分离，便于维护
- ✅ **异步处理**：不阻塞 API 响应
- ✅ **可扩展性**：每层独立，易于扩展
- ✅ **可测试性**：每层可单独测试

---

## 🚀 阶段 1：项目基础设置

### 🎯 目标

建立项目的"骨架"，确保所有协作者能在同一环境下工作。

### 📦 完成的任务

#### Task 1-2: 依赖管理和版本控制

**创建了什么**：

```
requirements.txt   # Python 依赖
.gitignore         # Git 忽略规则
```

**为什么需要**：

- `requirements.txt`：确保团队使用相同的库版本（避免"在我电脑上能跑"问题）
- `.gitignore`：防止提交敏感信息（`.env`）和无用文件（`__pycache__`）

**套路**：

```
1. 先确定技术栈
2. 固定版本号（fastapi==0.104.1，而不是 fastapi）
3. 明确忽略规则
```

#### Task 3: 环境变量管理

**创建了什么**：

```bash
.env.example   # 配置模板（可提交）
.env           # 实际配置（不提交，在 .gitignore 中）
```

**为什么这么做**：

- ✅ **安全**：数据库密码不会泄露到 Git
- ✅ **灵活**：开发/生产环境使用不同配置
- ✅ **协作**：新人知道需要配置什么

**套路**：

```
1. .env.example 提供模板
2. .env 存储实际值
3. .gitignore 忽略 .env
4. README 说明如何配置
```

#### Task 4: 目录结构

**创建了什么**：

```
app/
├── api/              # API 路由
├── models/           # 数据库模型
├── schemas/          # 数据验证
├── services/         # 业务逻辑
├── repositories/     # 数据访问
├── core/             # 核心配置
└── utils/            # 工具函数
```

**为什么这么设计**：

- 📁 **分层架构**：每层职责单一
- 📁 **可预测**：其他开发者知道在哪找代码
- 📁 **可扩展**：新功能放在对应目录

**套路（重要！）**：

```
按职责分层：
1. api/        - 处理 HTTP 请求和响应
2. models/     - 定义数据库表结构
3. schemas/    - 定义数据验证规则
4. repositories/ - 封装数据库操作
5. services/   - 实现业务逻辑
6. core/       - 配置和工具
```

#### Task 5: 配置管理

**创建了什么**：

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "WebProbe"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

**为什么用 Pydantic Settings**：

1. ✅ **类型验证**：自动检查配置类型
2. ✅ **默认值**：可选配置有默认值
3. ✅ **自动加载**：从 `.env` 自动读取
4. ✅ **IDE 友好**：有代码提示

**套路**：

```python
# 必需配置：没有默认值
DATABASE_URL: str

# 可选配置：有默认值
DEBUG: bool = False
```

### 🧠 设计思维

#### 问：为什么要先设置这些"无聊"的东西？

**答**：就像建房子要先打地基！

```
❌ 错误做法：直接写代码
   → 环境不一致
   → 配置混乱
   → 协作困难

✅ 正确做法：先建基础设施
   → 统一环境
   → 清晰配置
   → 易于协作
```

#### 问：为什么要分这么多目录？

**答**：**单一职责原则**（SOLID 的 S）

```python
# ❌ 所有代码放一个文件
main.py  # 3000 行代码，难以维护

# ✅ 按职责分离
api/endpoints/tasks.py      # 处理 HTTP 请求
repositories/task_repo.py   # 数据库操作
services/scraper.py         # 业务逻辑
```

---

## 🗄️ 阶段 2：数据库层

### 🎯 目标

设计数据模型，建立与数据库的连接。

### 📊 数据模型设计

#### Task 6-8: 创建模型

**设计了什么**：

```
Task 表          Result 表
┌─────────┐     ┌──────────┐
│ id      │────→│ task_id  │
│ url     │     │ title    │
│ status  │     │ content  │
│ ...     │     │ ...      │
└─────────┘     └──────────┘
   1 对 1 关系
```

**为什么分两张表**：

1. **Task（任务）**：记录"要做什么"
   - URL、状态、时间
2. **Result（结果）**：记录"做完了什么"
   - 标题、内容、链接

**好处**：

- ✅ **解耦**：任务和结果独立管理
- ✅ **扩展**：未来可以一个任务多个结果
- ✅ **查询**：可以只查任务状态，不加载大数据

#### 代码设计套路

##### 1️⃣ **Mixin 模式**（代码复用）

```python
# app/models/base.py
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class UUIDMixin:
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
```

**为什么用 Mixin**：

- ✅ **DRY 原则**：Don't Repeat Yourself
- ✅ **一致性**：所有表都有相同的时间戳字段
- ✅ **维护**：修改一处，所有表生效

**对比**：

```python
# ❌ 不用 Mixin（重复代码）
class Task(Base):
    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime, ...)  # 重复
    updated_at = Column(DateTime, ...)  # 重复

class Result(Base):
    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime, ...)  # 又重复
    updated_at = Column(DateTime, ...)  # 又重复

# ✅ 用 Mixin（复用代码）
class Task(Base, UUIDMixin, TimestampMixin):
    url = Column(String)
    # id, created_at, updated_at 自动继承

class Result(Base, UUIDMixin, TimestampMixin):
    title = Column(String)
    # id, created_at, updated_at 自动继承
```

##### 2️⃣ **枚举类型**（类型安全）

```python
class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
```

**为什么用枚举**：

```python
# ❌ 用字符串（容易出错）
task.status = "PENDING"   # OK
task.status = "PENDNG"    # 拼写错误，运行时才发现

# ✅ 用枚举（编译时检查）
task.status = TaskStatus.PENDING   # OK
task.status = TaskStatus.PENDNG    # IDE 直接报错
```

##### 3️⃣ **索引设计**（性能优化）

```python
class Task(Base):
    url = Column(String, index=True)      # 经常按 URL 查询
    status = Column(Enum, index=True)     # 经常按状态过滤
```

**为什么加索引**：

```
无索引：扫描 100 万行 → 慢 🐌
有索引：直接定位      → 快 🚀
```

**套路**：

```
给以下列加索引：
1. WHERE 子句中的列（status）
2. JOIN 条件列（task_id）
3. ORDER BY 列（created_at）
```

#### Task 10: 数据库连接

**创建了什么**：

```python
# app/core/database.py
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**为什么这么设计**：

1. **连接池**：复用连接，避免频繁创建

   ```python
   pool_size=10,        # 保持 10 个连接
   max_overflow=20      # 最多额外创建 20 个
   ```

2. **依赖注入**：FastAPI 自动管理生命周期
   ```python
   @app.get("/tasks")
   def list_tasks(db: Session = Depends(get_db)):
       # FastAPI 自动调用 get_db()
       # 请求结束后自动关闭连接
   ```

### 🧠 设计思维

#### 问：为什么用 UUID 而不是自增 ID？

```python
# 选项 1: 自增 ID
id = Column(Integer, primary_key=True, autoincrement=True)

# 选项 2: UUID
id = Column(UUID, primary_key=True, default=uuid.uuid4)
```

**UUID 的优势**：

- ✅ **分布式友好**：不同服务器生成不会冲突
- ✅ **安全性**：难以猜测下一个 ID
- ✅ **合并数据**：不会出现 ID 冲突

**自增 ID 的优势**：

- ✅ **紧凑**：只占 4 字节（UUID 占 16 字节）
- ✅ **有序**：插入性能更好
- ✅ **可读**：`/tasks/1` 比 `/tasks/uuid` 易读

**结论**：微服务架构选 UUID，单体应用可选自增 ID

#### 问：为什么 Result 和 Task 是 1:1 关系？

**当前设计**：一个任务只有一个结果

**未来扩展**：

```python
# 如果需要支持"定时重复抓取"
# 只需改为 1:N 关系
class Result(Base):
    task_id = Column(UUID, ForeignKey("tasks.id"))  # 去掉 unique=True
```

**套路**：先简单设计，需要时再扩展

---

## 📋 阶段 3：Pydantic Schemas

### 🎯 目标

定义 API 的输入输出格式，实现数据验证。

### 🔍 为什么需要 Schemas？

```
用户输入 → Schema 验证 → Model 存储 → Schema 序列化 → 返回给用户
    ↓            ↓            ↓            ↓
  JSON     类型检查      数据库        JSON
```

**三层数据模型**：

1. **Request（输入）**：TaskCreate
2. **Database（存储）**：Task Model
3. **Response（输出）**：TaskResponse

### 📝 代码设计

#### Task 12: Task Schemas

```python
# 输入 Schema（用户提交）
class TaskCreate(BaseModel):
    url: HttpUrl  # 自动验证 URL 格式

    class Config:
        json_schema_extra = {
            "example": {"url": "https://example.com"}
        }

# 输出 Schema（返回给用户）
class TaskResponse(BaseModel):
    id: UUID
    url: str
    status: TaskStatus
    created_at: datetime
    # ...

    class Config:
        from_attributes = True  # 可以从 ORM 对象创建
```

**为什么分 Create 和 Response**：

```python
# ❌ 用同一个 Schema
class Task(BaseModel):
    id: UUID              # 创建时用户不能指定 ID！
    url: HttpUrl
    created_at: datetime  # 创建时用户不能指定时间！

# ✅ 分开定义
class TaskCreate(BaseModel):
    url: HttpUrl          # 只需要 URL

class TaskResponse(BaseModel):
    id: UUID              # 系统生成
    url: str
    created_at: datetime  # 系统生成
```

#### Task 14: 列表响应

```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

**为什么需要分页信息**：

```json
{
  "tasks": [...],
  "total": 100,      // 总共 100 条
  "page": 1,         // 当前第 1 页
  "page_size": 10    // 每页 10 条
}
```

前端可以实现：

```
← 上一页  1 2 3 4 5  下一页 →
```

### 🧠 设计思维

#### 问：为什么不直接用 Model？

```python
# ❌ 直接返回 Model
@app.get("/tasks/{id}")
def get_task(id: UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    return task  # 可能暴露敏感字段！

# ✅ 使用 Schema
@app.get("/tasks/{id}", response_model=TaskResponse)
def get_task(id: UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    return task  # TaskResponse 只返回允许的字段
```

**好处**：

1. ✅ **安全**：控制返回的字段
2. ✅ **解耦**：数据库改动不影响 API
3. ✅ **验证**：自动类型检查

#### 问：HttpUrl 和 str 有什么区别？

```python
class TaskCreate(BaseModel):
    url: HttpUrl  # Pydantic 特殊类型

# 自动验证：
TaskCreate(url="https://example.com")  # ✅ 通过
TaskCreate(url="not a url")            # ❌ 报错
TaskCreate(url="ftp://example.com")    # ❌ 报错（必须 http/https）
```

**套路**：使用 Pydantic 的特殊类型

- `HttpUrl`：HTTP URL
- `EmailStr`：邮箱
- `constr(min_length=1)`：非空字符串
- `conint(gt=0)`：正整数

---

## 🏗️ 阶段 4：Repository 层

### 🎯 目标

封装所有数据库操作，让业务逻辑不直接接触数据库。

### 🎨 Repository 模式

#### 什么是 Repository？

```
Controller → Repository → Database
              ↑
          封装数据访问
```

**类比**：

- Repository 就像图书馆管理员
- 你（Controller）想要书，不需要知道书在哪个书架
- 告诉管理员（Repository）书名，他帮你找

#### Task 15: 基础 Repository

```python
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(...).first()

    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        return db_obj
```

**为什么用泛型**：

```python
# 一个 BaseRepository 可以用于所有模型
task_repo = BaseRepository[Task](Task, db)
result_repo = BaseRepository[Result](Result, db)

# 有类型提示
task = task_repo.get_by_id(id)  # IDE 知道返回 Task
```

#### Task 16: TaskRepository

```python
class TaskRepository(BaseRepository[Task]):
    def get_by_url(self, url: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.url == url).first()

    def get_by_status(self, status: TaskStatus) -> List[Task]:
        return self.db.query(Task).filter(Task.status == status).all()
```

**为什么继承 BaseRepository**：

```python
# TaskRepository 自动拥有：
- get_by_id()
- get_all()
- create()
- update()
- delete()

# 只需添加特定方法：
- get_by_url()
- get_by_status()
```

### 🧠 设计思维

#### 问：为什么不在 Controller 直接写 SQL？

```python
# ❌ 在 Controller 写数据库逻辑
@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.status == "PENDING").all()
    return tasks

# ✅ 使用 Repository
@app.get("/tasks")
def list_tasks(task_repo: TaskRepository = Depends(get_task_repo)):
    tasks = task_repo.get_by_status(TaskStatus.PENDING)
    return tasks
```

**好处**：

1. ✅ **可测试**：可以 mock Repository
2. ✅ **可复用**：`get_by_status()` 可以在多处使用
3. ✅ **可维护**：数据库逻辑集中管理

#### 问：Repository 和 Service 的区别？

```
Repository：数据访问（How to get data）
  - 只负责 CRUD
  - 不包含业务逻辑

Service：业务逻辑（What to do with data）
  - 调用 Repository
  - 包含业务规则
```

**例子**：

```python
# Repository：简单的数据访问
class TaskRepository:
    def get_by_id(self, id: UUID) -> Task:
        return self.db.query(Task).filter(...).first()

# Service：复杂的业务逻辑
class TaskService:
    def create_and_trigger_scraping(self, url: str) -> Task:
        # 1. 检查是否已存在
        existing = self.task_repo.get_by_url(url)
        if existing:
            return existing

        # 2. 创建任务
        task = self.task_repo.create({"url": url})

        # 3. 触发异步抓取
        scrape_task.delay(task.id)

        return task
```

---

## 🌐 阶段 5：基础 API

### 🎯 目标

创建 RESTful API 端点，让用户可以通过 HTTP 访问系统。

### 🚦 API 设计

#### RESTful 规范

```
POST   /api/v1/tasks          创建任务
GET    /api/v1/tasks          获取任务列表
GET    /api/v1/tasks/{id}     获取单个任务
PUT    /api/v1/tasks/{id}     更新任务
DELETE /api/v1/tasks/{id}     删除任务
```

**为什么这么设计**：

- ✅ **语义化**：通过 HTTP 方法表示操作
- ✅ **统一**：业界标准，易于理解
- ✅ **版本化**：`/api/v1/` 便于未来升级

#### Task 19: 健康检查

```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="unhealthy")
```

**为什么需要健康检查**：

1. ✅ **监控**：Kubernetes 定期检查
2. ✅ **调试**：快速判断服务状态
3. ✅ **负载均衡**：不健康的实例不接受流量

#### Task 20-21: CRUD 端点

##### 创建任务

```python
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_in: TaskCreate,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    task_data = {"url": str(task_in.url), "status": "PENDING"}
    task = task_repo.create(task_data)
    return task
```

**设计细节**：

1. `response_model=TaskResponse`：自动验证和序列化
2. `status_code=201`：创建成功返回 201
3. `Depends(get_task_repository)`：依赖注入

##### 查询任务

```python
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    task = task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

**错误处理**：

```python
# 404：资源不存在
if not task:
    raise HTTPException(status_code=404)

# 400：请求参数错误（Pydantic 自动处理）
# 500：服务器错误（FastAPI 自动捕获）
```

##### 列表查询（带分页）

```python
@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    skip: int = 0,
    limit: int = 10,
    status_filter: Optional[TaskStatus] = None,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    if status_filter:
        tasks = task_repo.get_by_status(status_filter, skip, limit)
        total = task_repo.count_by_status(status_filter)
    else:
        tasks = task_repo.get_all(skip, limit)
        total = len(tasks)

    return {
        "tasks": tasks,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }
```

**分页套路**：

```
skip=0, limit=10   → 第 1 页
skip=10, limit=10  → 第 2 页
skip=20, limit=10  → 第 3 页
```

#### Task 22: 路由聚合

```python
# app/api/v1/__init__.py
api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(tasks.router, prefix="", tags=["Tasks"])

# app/main.py
app = FastAPI(title="WebProbe")
app.include_router(api_router, prefix="/api/v1")
```

**为什么分层路由**：

```
app
  └─ /api/v1
       ├─ /health
       └─ /tasks
            ├─ POST /tasks
            ├─ GET /tasks
            └─ GET /tasks/{id}
```

1. ✅ **版本管理**：`/api/v1` → `/api/v2`
2. ✅ **模块化**：每个功能独立路由文件
3. ✅ **自动文档**：tags 分组显示

### 🧠 设计思维

#### 问：为什么用依赖注入？

```python
# ❌ 硬编码依赖
@app.get("/tasks")
def list_tasks():
    db = SessionLocal()  # 每次创建新连接
    repo = TaskRepository(db)
    tasks = repo.get_all()
    db.close()  # 手动关闭
    return tasks

# ✅ 依赖注入
@app.get("/tasks")
def list_tasks(task_repo: TaskRepository = Depends(get_task_repo)):
    tasks = task_repo.get_all()
    return tasks  # 自动关闭连接
```

**好处**：

1. ✅ **自动管理**：FastAPI 自动创建和销毁
2. ✅ **易于测试**：可以注入 mock 对象
3. ✅ **代码简洁**：不需要手动管理资源

#### 问：async def 和 def 的区别？

```python
# 同步函数
@app.get("/tasks")
def list_tasks():
    tasks = task_repo.get_all()  # 阻塞
    return tasks

# 异步函数
@app.get("/tasks")
async def list_tasks():
    tasks = task_repo.get_all()  # 还是阻塞（数据库操作）
    return tasks
```

**真相**：

- 数据库操作（SQLAlchemy）是同步的
- 用 `async def` 只是为了统一风格
- 真正的异步在阶段 6（Celery）

**何时用 async**：

```python
# 真正的异步操作
async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

---

## 🎓 设计套路总结

### 📐 分层架构套路

```
1. Controller (API层)
   ↓ 调用
2. Service (业务逻辑层)
   ↓ 调用
3. Repository (数据访问层)
   ↓ 访问
4. Database (数据库)
```

**每层职责**：

```python
# Controller：处理 HTTP
@app.post("/tasks")
def create_task(task_in: TaskCreate):
    # 验证输入 → 调用 Service → 返回响应
    pass

# Service：业务逻辑
class TaskService:
    def create_task_with_scraping(self, url: str):
        # 检查重复 → 创建任务 → 触发异步
        pass

# Repository：数据访问
class TaskRepository:
    def create(self, data: dict):
        # 插入数据库 → 返回对象
        pass
```

### 🔧 配置管理套路

```
1. 敏感配置（密码）→ .env（不提交）
2. 配置模板 → .env.example（提交）
3. 配置类 → config.py（提交）
4. 使用配置 → from app.config import settings
```

### 📊 数据建模套路

```
1. 确定实体（Task, Result）
2. 确定关系（1:1, 1:N, N:N）
3. 抽取公共字段（Mixin）
4. 添加索引（WHERE/JOIN/ORDER BY 的字段）
5. 使用枚举（固定值的字段）
```

### 🔐 数据验证套路

```
1. 输入验证 → Pydantic Schema (TaskCreate)
2. 数据库验证 → SQLAlchemy Model (Task)
3. 输出验证 → Pydantic Schema (TaskResponse)

三层分离，职责清晰！
```

### 🚀 API 设计套路

```
1. RESTful 规范
   - GET：查询
   - POST：创建
   - PUT：更新
   - DELETE：删除

2. 状态码规范
   - 200：成功
   - 201：创建成功
   - 400：参数错误
   - 404：未找到
   - 500：服务器错误

3. 分页规范
   - skip：偏移量
   - limit：每页数量
   - 返回：total, page, page_size
```

---

## 💡 关键技术决策

### 1. 为什么选择 FastAPI？

```
✅ 性能：与 Node.js、Go 相当
✅ 类型安全：基于 Python 类型提示
✅ 自动文档：Swagger UI 自动生成
✅ 异步支持：原生支持 async/await
✅ 依赖注入：优雅的依赖管理
```

**对比**：
| 框架 | 性能 | 文档 | 学习曲线 | 类型安全 |
|------|------|------|----------|----------|
| Flask | ⭐⭐⭐ | ❌ 需手写 | ⭐⭐⭐⭐⭐ | ❌ |
| Django | ⭐⭐ | ✅ 内置 | ⭐⭐⭐ | ❌ |
| FastAPI | ⭐⭐⭐⭐⭐ | ✅ 自动 | ⭐⭐⭐⭐ | ✅ |

### 2. 为什么用 PostgreSQL？

```
✅ JSONB：灵活存储非结构化数据（links, extra_data）
✅ 可靠：ACID 保证，企业级数据库
✅ 功能：全文搜索、地理位置、数组等
✅ 扩展：支持各种插件
```

**对比 MySQL**：

- PostgreSQL 的 JSONB 比 MySQL 的 JSON 性能更好
- PostgreSQL 更适合复杂查询

### 3. 为什么用 SQLAlchemy ORM？

```
✅ 抽象：不需要写 SQL
✅ 类型安全：IDE 有代码提示
✅ 迁移：支持多种数据库
✅ 关系：自动处理外键和关系
```

**对比原生 SQL**：

```python
# ❌ 原生 SQL
cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
row = cursor.fetchone()
task = Task(id=row[0], url=row[1], ...)  # 手动映射

# ✅ ORM
task = db.query(Task).filter(Task.id == task_id).first()
```

### 4. 为什么用 Pydantic？

```
✅ 自动验证：类型错误自动返回 400
✅ 序列化：自动转换 datetime、UUID 等
✅ 文档：自动生成 JSON Schema
✅ 性能：基于 C 扩展，速度快
```

---

## 📚 面试准备

### 高频问题

#### 1. 介绍一下你的项目架构

**回答模板**：

```
我们采用了分层架构：

1. API 层：FastAPI 处理 HTTP 请求
2. Service 层：实现业务逻辑
3. Repository 层：封装数据访问
4. Model 层：定义数据结构

这种设计的好处是：
- 职责分离，易于维护
- 每层可独立测试
- 易于扩展新功能
```

#### 2. 为什么用 Repository 模式？

**回答模板**：

```
主要有三个原因：

1. 解耦：业务逻辑不直接依赖数据库
   - 可以轻松切换数据库
   - 可以添加缓存层

2. 复用：数据访问逻辑集中管理
   - get_by_status() 可在多处使用
   - 避免重复代码

3. 测试：可以 mock Repository
   - 不需要真实数据库
   - 测试更快更可靠
```

#### 3. 如何设计数据库表？

**回答模板**：

```
我遵循以下步骤：

1. 确定实体：Task 和 Result
2. 确定关系：1:1 关系
3. 抽取公共字段：
   - id, created_at, updated_at（Mixin）
4. 添加索引：
   - url（经常查询）
   - status（经常过滤）
5. 选择数据类型：
   - UUID：分布式友好
   - JSONB：灵活存储
```

#### 4. 如何处理并发？

**回答模板**：

```
我们使用了几种策略：

1. 数据库层：
   - 连接池（pool_size=10）
   - 事务隔离

2. 应用层：
   - 异步处理（Celery）
   - 状态机（PENDING → PROCESSING → SUCCESS）

3. 未来优化：
   - 分布式锁（Redis）
   - 消息队列（Kafka）
```

#### 5. 如何保证 API 质量？

**回答模板**：

```
我们有多层保障：

1. 输入验证：Pydantic 自动验证
2. 类型安全：Python 类型提示
3. 错误处理：统一的异常处理
4. 单元测试：Repository、Service 层
5. 集成测试：API 端到端测试
6. 文档：自动生成 Swagger UI
```

### 关键知识点

#### REST API 设计原则

```
1. 资源导向：/tasks 而不是 /get-tasks
2. HTTP 方法语义化：GET/POST/PUT/DELETE
3. 状态码标准化：2xx/4xx/5xx
4. 版本化：/api/v1/
5. 分页：skip, limit
6. 过滤：query parameters
```

#### 数据库设计原则

```
1. 范式化：消除冗余
2. 索引优化：WHERE/JOIN 字段
3. 外键约束：保证数据一致性
4. 类型选择：根据业务场景
5. 预留扩展：考虑未来需求
```

#### Python 最佳实践

```
1. 类型提示：def func(x: int) -> str
2. 文档字符串："""description"""
3. 异常处理：try/except/finally
4. 上下文管理：with statement
5. 列表推导式：[x for x in ...]
```

---

## 🎯 总结

### 你学到了什么？

#### 技术层面

1. ✅ FastAPI 框架使用
2. ✅ SQLAlchemy ORM
3. ✅ Pydantic 数据验证
4. ✅ PostgreSQL 数据库
5. ✅ RESTful API 设计
6. ✅ 依赖注入模式
7. ✅ Repository 模式

#### 工程层面

1. ✅ 项目结构组织
2. ✅ 配置管理
3. ✅ 环境变量
4. ✅ 分层架构
5. ✅ 代码复用（Mixin）
6. ✅ 错误处理
7. ✅ API 文档

#### 思维层面

1. ✅ 单一职责原则
2. ✅ DRY 原则
3. ✅ 解耦思想
4. ✅ 测试驱动
5. ✅ 渐进式开发
6. ✅ 可扩展设计

### 下一步做什么？

#### 阶段 6：Celery 集成

```
学习内容：
- 异步任务队列
- Redis 消息代理
- 任务状态管理
- 重试机制
```

#### 阶段 7：Redis 缓存

```
学习内容：
- 缓存策略
- TTL 管理
- 缓存失效
- 性能优化
```

#### 阶段 8：Docker 化

```
学习内容：
- 容器化
- Docker Compose
- 服务编排
- 生产部署
```

### 给初学者的建议

1. **先理解架构，再写代码**

   - 知道为什么要这么设计
   - 理解每层的职责

2. **注重代码质量**

   - 类型提示
   - 文档字符串
   - 命名规范

3. **多问为什么**

   - 为什么用 UUID？
   - 为什么分三层？
   - 为什么用 Pydantic？

4. **实践出真知**

   - 动手写代码
   - 运行测试
   - 调试错误

5. **持续学习**
   - 阅读官方文档
   - 看开源项目
   - 写技术博客

