# Models 模块设计文档 & 面试指南

> 数据模型层的完整设计说明和面试准备

---

## 📚 目录

1. [整体架构设计](#整体架构设计)
2. [模型详解](#模型详解)
3. [设计模式与最佳实践](#设计模式与最佳实践)
4. [数据库设计](#数据库设计)
5. [面试高频问题](#面试高频问题)
6. [代码示例](#代码示例)

---

## 整体架构设计

### 🎯 设计原则

1. **DRY 原则** (Don't Repeat Yourself) - 通过 Mixin 复用代码
2. **单一职责原则** - 每个文件只负责一个模型
3. **关注点分离** - 基础功能与业务模型分离
4. **类型安全** - 使用 Enum 避免拼写错误
5. **性能优化** - 合理使用索引

### 📁 目录结构

```
app/models/
├── __init__.py      # 模块导出
├── base.py          # 基础类和 Mixin
├── task.py          # Task 模型（任务）
└── result.py        # Result 模型（结果）
```

### 🔗 模型关系图

```
┌─────────────────────────────────────────────┐
│              Base (SQLAlchemy)              │
│         declarative_base()                  │
└─────────────────────────────────────────────┘
                     ▲
                     │ 继承
        ┌────────────┴────────────┐
        │                         │
┌───────┴────────┐       ┌────────┴────────┐
│  UUIDMixin     │       │ TimestampMixin  │
│  - id (UUID)   │       │ - created_at    │
└───────┬────────┘       │ - updated_at    │
        │                └────────┬────────┘
        │                         │
        └───────┬─────────────────┘
                │ 多重继承
        ┌───────┴────────┐
        │                │
   ┌────┴─────┐    ┌─────┴─────┐
   │   Task   │    │  Result   │
   │          │◄───│           │
   │  业务字段  │ 1:1 │  抓取数据  │
   └──────────┘    └───────────┘
      │                  │
      ├─ url             ├─ task_id (FK)
      ├─ status          ├─ title
      ├─ started_at      ├─ description
      ├─ completed_at    ├─ links (JSONB)
      ├─ error_message   ├─ text_content
      └─ result_id       └─ metadata (JSONB)
```

### 🎨 实体关系图 (ERD)

```
┌─────────────────────────┐
│         tasks           │
├─────────────────────────┤
│ id (PK)        UUID     │
│ url            VARCHAR  │◄────────┐
│ status         ENUM     │         │
│ started_at     TIMESTAMP│         │ 1:1
│ completed_at   TIMESTAMP│         │
│ error_message  TEXT     │         │
│ result_id      UUID     │         │
│ created_at     TIMESTAMP│         │
│ updated_at     TIMESTAMP│         │
└─────────────────────────┘         │
                                    │
                                    │
┌─────────────────────────┐         │
│        results          │         │
├─────────────────────────┤         │
│ id (PK)        UUID     │         │
│ task_id (FK)   UUID     │─────────┘
│ title          VARCHAR  │
│ description    TEXT     │
│ links          JSONB    │
│ text_content   TEXT     │
│ metadata       JSONB    │
│ scraped_at     TIMESTAMP│
│ created_at     TIMESTAMP│
│ updated_at     TIMESTAMP│
└─────────────────────────┘
```

---

## 模型详解

### 1️⃣ base.py - 基础模型层

**作用**：提供所有模型的基础类和通用功能

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class TimestampMixin:
    """时间戳混入类 - 自动管理创建和更新时间"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                       onupdate=datetime.utcnow, nullable=False)

class UUIDMixin:
    """UUID 主键混入类 - 统一使用 UUID 作为主键"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

#### 关键设计点

| 组件             | 作用                  | 好处                  |
| ---------------- | --------------------- | --------------------- |
| `Base`           | SQLAlchemy 声明式基类 | 所有模型继承它        |
| `TimestampMixin` | 自动时间戳            | 统一记录创建/更新时间 |
| `UUIDMixin`      | UUID 主键             | 分布式友好，不会冲突  |

#### Mixin 模式优势

**❌ 不用 Mixin（代码重复）**

```python
class Task(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    # ... 业务字段

class Result(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)  # 重复！
    created_at = Column(DateTime, default=datetime.utcnow)   # 重复！
    updated_at = Column(DateTime, default=datetime.utcnow)   # 重复！
    # ... 业务字段
```

**✅ 使用 Mixin（简洁优雅）**

```python
class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"
    # ... 只写业务字段

class Result(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "results"
    # ... 只写业务字段
```

---

### 2️⃣ task.py - 任务模型

**作用**：表示一个网页抓取任务

```python
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "PENDING"        # 等待处理
    PROCESSING = "PROCESSING"  # 正在处理
    SUCCESS = "SUCCESS"        # 成功完成
    FAILED = "FAILED"          # 失败

class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    url = Column(String(2048), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING,
                   nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, url={self.url}, status={self.status})>"
```

#### 字段设计说明

| 字段            | 类型         | 索引 | 可空 | 作用         | 设计考虑              |
| --------------- | ------------ | ---- | ---- | ------------ | --------------------- |
| `id`            | UUID         | PK   | ❌   | 主键         | 继承自 UUIDMixin      |
| `url`           | String(2048) | ✅   | ❌   | 要抓取的网址 | 索引加速查询          |
| `status`        | Enum         | ✅   | ❌   | 任务状态     | 索引加速筛选          |
| `started_at`    | DateTime     | ❌   | ✅   | 开始时间     | 任务开始时设置        |
| `completed_at`  | DateTime     | ❌   | ✅   | 完成时间     | 任务完成时设置        |
| `error_message` | Text         | ❌   | ✅   | 错误信息     | 失败时记录            |
| `result_id`     | UUID         | ❌   | ✅   | 结果 ID      | 外键关联              |
| `created_at`    | DateTime     | ❌   | ❌   | 创建时间     | 继承自 TimestampMixin |
| `updated_at`    | DateTime     | ❌   | ❌   | 更新时间     | 继承自 TimestampMixin |

#### 为什么使用 Enum？

**❌ 不用 Enum（容易出错）**

```python
task.status = "PENING"  # 拼写错误！运行时才发现
task.status = "pending"  # 大小写错误！
task.status = "完成"      # 随意命名！
```

**✅ 使用 Enum（类型安全）**

```python
task.status = TaskStatus.PENDING  # IDE 自动补全
task.status = TaskStatus.PENING   # 编译时报错！
```

#### 为什么加索引？

```python
# url 字段加索引 - 经常按 URL 查询
index=True  # CREATE INDEX idx_tasks_url ON tasks(url);

# status 字段加索引 - 经常按状态筛选
index=True  # CREATE INDEX idx_tasks_status ON tasks(status);

# 性能提升示例：
# 无索引：全表扫描 100 万条数据 → 5 秒
# 有索引：索引查找 → 10 毫秒
```

---

### 3️⃣ result.py - 结果模型

**作用**：存储网页抓取的结果数据

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base, UUIDMixin, TimestampMixin
from datetime import datetime

class Result(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "results"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"),
                    nullable=False, unique=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    links = Column(JSONB, nullable=True, default=list)
    text_content = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True, default=dict)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Result(id={self.id}, task_id={self.task_id}, title={self.title})>"
```

#### 关键设计点

**1. 外键约束（1:1 关系）**

```python
task_id = Column(UUID, ForeignKey("tasks.id"),
                nullable=False, unique=True)
# unique=True 确保一个任务只有一个结果
# ForeignKey 确保数据一致性
```

**2. JSONB 类型（PostgreSQL 特性）**

```python
# links - 存储链接数组
links = Column(JSONB, default=list)
# 数据示例：["https://link1.com", "https://link2.com"]

# metadata - 存储元数据字典
metadata = Column(JSONB, default=dict)
# 数据示例：{"status_code": 200, "content_type": "text/html"}
```

#### 为什么使用 JSONB？

| 对比     | JSON | JSONB  | 选择     |
| -------- | ---- | ------ | -------- |
| 存储方式 | 文本 | 二进制 | ✅ JSONB |
| 查询速度 | 慢   | 快     | ✅ JSONB |
| 支持索引 | ❌   | ✅     | ✅ JSONB |
| 存储空间 | 小   | 稍大   | ✅ JSONB |

**JSONB 优势示例**：

```python
# 灵活存储复杂数据
result.links = ["link1", "link2", "link3"]  # 数组
result.metadata = {
    "status_code": 200,
    "headers": {"content-type": "text/html"},
    "timing": {"dns": 10, "connect": 50}
}

# 支持 JSON 查询
db.query(Result).filter(
    Result.metadata['status_code'].astext == '200'
).all()
```

---

### 4️⃣ **init**.py - 模块导出

**作用**：统一导出所有模型

```python
from app.models.base import Base
from app.models.task import Task, TaskStatus
from app.models.result import Result

__all__ = ["Base", "Task", "TaskStatus", "Result"]
```

**好处**：

```python
# ✅ 简洁的导入方式
from app.models import Task, Result, TaskStatus

# ❌ 不用写复杂路径
from app.models.task import Task
from app.models.task import TaskStatus
from app.models.result import Result
```

---

## 设计模式与最佳实践

### 🎨 设计模式

#### 1. Mixin 模式（组合优于继承）

**定义**：将通用功能封装成 Mixin 类，通过多重继承组合功能

**优点**：

- ✅ 代码复用
- ✅ 灵活组合
- ✅ 避免深层继承

**示例**：

```python
# 可以灵活组合不同的 Mixin
class Task(Base, UUIDMixin, TimestampMixin):
    pass

class AuditLog(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    pass
```

#### 2. 枚举模式（类型安全）

**定义**：使用 Enum 定义有限状态集合

**优点**：

- ✅ 防止拼写错误
- ✅ IDE 自动补全
- ✅ 类型检查

**示例**：

```python
class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

# 使用
task.status = TaskStatus.PENDING  # ✅ 类型安全
task.status = "PENDING"            # ✅ 也可以（兼容字符串）
task.status = "INVALID"            # ❌ 运行时会报错
```

#### 3. Active Record 模式

**定义**：数据模型包含数据访问逻辑

**示例**：

```python
class Task(Base):
    # ... 字段定义

    @classmethod
    def get_pending_tasks(cls, db):
        return db.query(cls).filter(
            cls.status == TaskStatus.PENDING
        ).all()

    def mark_as_processing(self, db):
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.utcnow()
        db.commit()
```

---

### 💡 最佳实践

#### 1. 索引策略

**规则**：

- ✅ 频繁查询的字段加索引（url, status）
- ✅ 外键字段加索引（task_id）
- ❌ 不频繁查询的字段不加索引（减少写入开销）

**示例**：

```python
# 这个字段加索引 - 经常按 URL 查询
url = Column(String(2048), index=True)

# 这个字段不加索引 - 很少查询
error_message = Column(Text)  # 不加 index=True
```

#### 2. 字段长度设计

```python
# ✅ 合理的长度
url = Column(String(2048))      # URL 通常不超过 2048
title = Column(String(500))     # 标题一般不超过 500

# ❌ 过长或过短
url = Column(String(50))        # 太短！URL 可能被截断
title = Column(Text)            # 太长！影响索引性能
```

#### 3. 默认值设计

```python
# ✅ 合理的默认值
status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
links = Column(JSONB, default=list)  # 空列表而非 None
metadata = Column(JSONB, default=dict)  # 空字典而非 None

# ❌ 没有默认值（可能导致 NULL）
status = Column(Enum(TaskStatus))  # 没有默认值！
```

#### 4. 可空性设计

```python
# ✅ 清晰的可空性
url = Column(String, nullable=False)        # 必须有 URL
error_message = Column(Text, nullable=True) # 错误信息可选

# ❌ 不明确的可空性
url = Column(String)  # 默认 nullable=True，但 URL 应该必填！
```

---

## 数据库设计

### 📊 完整的数据库表结构

#### tasks 表

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(2048) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    error_message TEXT NULL,
    result_id UUID NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 索引
    INDEX idx_tasks_url (url),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_created_at (created_at DESC),

    -- 约束
    CHECK (status IN ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED'))
);
```

#### results 表

```sql
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL UNIQUE,
    title VARCHAR(500) NULL,
    description TEXT NULL,
    links JSONB NULL DEFAULT '[]',
    text_content TEXT NULL,
    metadata JSONB NULL DEFAULT '{}',
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,

    -- 索引
    INDEX idx_results_task_id (task_id),
    INDEX idx_results_scraped_at (scraped_at DESC)
);
```

### 🔍 性能优化

#### 查询优化示例

```python
# ❌ 慢查询（全表扫描）
tasks = db.query(Task).all()  # 扫描 100 万条数据

# ✅ 快查询（使用索引）
tasks = db.query(Task).filter(
    Task.status == TaskStatus.PENDING
).limit(100).all()  # 只查 100 条，使用 status 索引

# ✅ 更快查询（复合索引）
tasks = db.query(Task).filter(
    Task.status == TaskStatus.PENDING
).order_by(Task.created_at.desc()).limit(10).all()
# 使用 status + created_at 复合索引
```

---

## 面试高频问题

### 🔥 基础问题

#### Q1: 什么是 ORM？为什么使用 SQLAlchemy？

**答案**:

> ORM (Object-Relational Mapping) 是对象关系映射，将数据库表映射为 Python 类。
>
> **优点**：
>
> - ✅ 不需要写 SQL，使用 Python 代码操作数据库
> - ✅ 类型安全，编译时检查
> - ✅ 防止 SQL 注入
> - ✅ 数据库无关性，可以切换数据库
>
> **SQLAlchemy** 是 Python 最流行的 ORM，功能强大，文档完善。

---

#### Q2: 为什么使用 UUID 而不是自增 ID？

**答案**:

> **UUID 的优点**：
>
> 1. **分布式友好**：多个服务器可以独立生成，不会冲突
> 2. **安全性高**：不能通过 ID 猜测记录数量
> 3. **易于合并**：不同数据库的数据可以无冲突合并
>
> **自增 ID 的问题**：
>
> 1. 分布式环境需要协调（避免冲突）
> 2. 暴露业务信息（通过 ID 知道有多少用户）
> 3. 合并数据库时会冲突
>
> **项目中的使用**：
>
> ```python
> id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
> # 自动生成 UUID，如：a1b2c3d4-e5f6-...
> ```

---

#### Q3: Mixin 模式的作用和优点？

**答案**:

> **Mixin 是一种代码复用模式**，将通用功能封装成类，通过多重继承组合。
>
> **项目中的应用**：
>
> ```python
> class UUIDMixin:
>     id = Column(UUID, primary_key=True, default=uuid.uuid4)
>
> class TimestampMixin:
>     created_at = Column(DateTime, default=datetime.utcnow)
>     updated_at = Column(DateTime, default=datetime.utcnow)
>
> class Task(Base, UUIDMixin, TimestampMixin):
>     # 自动拥有 id, created_at, updated_at
>     pass
> ```
>
> **优点**：
>
> - ✅ DRY 原则（Don't Repeat Yourself）
> - ✅ 灵活组合不同功能
> - ✅ 易于维护（修改一处，所有模型都更新）

---

### 🔥 进阶问题

#### Q4: 为什么 Task 和 Result 是 1:1 关系？

**答案**:

> **设计决策**：一个任务对应一个结果
>
> **原因**：
>
> 1. 业务逻辑：每次抓取生成一个结果
> 2. 数据一致性：避免多个结果混淆
> 3. 查询简单：直接通过 task_id 查询结果
>
> **实现方式**：
>
> ```python
> task_id = Column(UUID, ForeignKey("tasks.id"), unique=True)
> # unique=True 确保一个任务只有一个结果
> ```
>
> **如果需要 1:N（多次抓取）**：
>
> ```python
> # 可以改为 1:N 关系
> task_id = Column(UUID, ForeignKey("tasks.id"))  # 去掉 unique
> version = Column(Integer, default=1)  # 增加版本号字段
> ```

---

#### Q5: 为什么使用 JSONB 而不是创建单独的表？

**答案**:

> **JSONB 的使用场景**：
>
> - ✅ 结构不固定（每个网页的链接数量不同）
> - ✅ 查询频率低（主要是存储，偶尔查询）
> - ✅ 简化数据模型（不需要额外的表和关联）
>
> **示例**：
>
> ```python
> links = Column(JSONB, default=list)
> # 可以存储任意数量的链接
> # ["link1", "link2", ...]
> ```
>
> **如果创建单独的表**：
>
> ```python
> class Link(Base):
>     id = Column(UUID, primary_key=True)
>     result_id = Column(UUID, ForeignKey("results.id"))
>     url = Column(String)
>     text = Column(String)
> # 优点：结构化，查询快
> # 缺点：复杂度高，需要额外的表和查询
> ```
>
> **权衡**：对于本项目，链接主要用于展示，不需要复杂查询，所以用 JSONB 更简单。

---

#### Q6: 数据库索引加在哪些字段？为什么？

**答案**:

> **项目中的索引策略**：
>
> | 表      | 字段    | 索引 | 原因                              |
> | ------- | ------- | ---- | --------------------------------- |
> | tasks   | url     | ✅   | 经常按 URL 查询（检查是否已存在） |
> | tasks   | status  | ✅   | 经常按状态筛选（获取待处理任务）  |
> | results | task_id | ✅   | 外键，经常关联查询                |
>
> **不加索引的字段**：
>
> - `error_message`: 很少查询
> - `text_content`: 太大，索引成本高
>
> **权衡**：
>
> - ✅ 索引加速查询
> - ❌ 索引减慢写入（每次插入需要更新索引）
> - ❌ 索引占用空间

---

#### Q7: 如何保证数据一致性？

**答案**:

> **项目中的一致性保证**：
>
> 1. **外键约束**：
>
> ```python
> task_id = Column(UUID, ForeignKey("tasks.id"))
> # 确保 result.task_id 必须存在于 tasks 表中
> ```
>
> 2. **唯一约束**：
>
> ```python
> task_id = Column(UUID, unique=True)
> # 确保一个任务只有一个结果
> ```
>
> 3. **非空约束**：
>
> ```python
> url = Column(String, nullable=False)
> # 确保 URL 必须填写
> ```
>
> 4. **枚举约束**：
>
> ```python
> status = Column(Enum(TaskStatus))
> # 确保状态只能是预定义的值
> ```
>
> 5. **事务**：
>
> ```python
> try:
>     db.add(task)
>     db.add(result)
>     db.commit()  # 原子性：要么都成功，要么都失败
> except:
>     db.rollback()
> ```

---

### 🔥 系统设计问题

#### Q8: 如果数据量很大（千万级），如何优化？

**答案**:

> **优化策略**：
>
> 1. **分表**（水平分片）：
>
> ```python
> # 按时间分表
> tasks_2024_01
> tasks_2024_02
> ...
>
> # 或按 URL hash 分表
> tasks_0  # hash(url) % 10 == 0
> tasks_1  # hash(url) % 10 == 1
> ...
> ```
>
> 2. **冷热数据分离**：
>
> ```python
> # 热数据（最近 30 天）
> tasks_hot  # 频繁查询
>
> # 冷数据（30 天前）
> tasks_cold  # 归档存储
> ```
>
> 3. **增加索引**：
>
> ```python
> # 复合索引
> Index('idx_status_created', 'status', 'created_at')
> ```
>
> 4. **读写分离**：
>
> ```
> 主库（写）→ 从库1（读）
>           → 从库2（读）
> ```
>
> 5. **缓存热点数据**：
>
> ```python
> # Redis 缓存最近查询的任务
> cache_key = f"task:{task_id}"
> ```

---

#### Q9: 如何处理并发更新？

**答案**:

> **并发场景**：多个 Worker 同时处理同一个任务
>
> **解决方案 1：乐观锁（Version）**
>
> ```python
> class Task(Base):
>     version = Column(Integer, default=1)
>
> # 更新时检查版本号
> task = db.query(Task).filter(Task.id == task_id).first()
> old_version = task.version
> task.status = TaskStatus.PROCESSING
> task.version += 1
>
> rows = db.query(Task).filter(
>     Task.id == task_id,
>     Task.version == old_version
> ).update({"status": TaskStatus.PROCESSING, "version": old_version + 1})
>
> if rows == 0:
>     # 版本冲突，其他 Worker 已更新
>     raise ConcurrentUpdateError
> ```
>
> **解决方案 2：分布式锁（Redis）**
>
> ```python
> # 使用 Redis 分布式锁
> lock_key = f"lock:task:{task_id}"
> if redis.set(lock_key, "1", nx=True, ex=300):
>     try:
>         # 处理任务
>         pass
>     finally:
>         redis.delete(lock_key)
> else:
>     # 任务已被其他 Worker 锁定
>     pass
> ```

---

## 代码示例

### 📝 创建和查询

```python
from app.models import Task, TaskStatus, Result
from datetime import datetime

# 1. 创建任务
task = Task(
    url="https://example.com",
    status=TaskStatus.PENDING
)
db.add(task)
db.commit()

# 2. 更新任务状态
task.status = TaskStatus.PROCESSING
task.started_at = datetime.utcnow()
db.commit()

# 3. 保存结果
result = Result(
    task_id=task.id,
    title="Example Domain",
    links=["https://link1.com", "https://link2.com"],
    text_content="This domain is for use in...",
    metadata={"status_code": 200, "content_type": "text/html"}
)
db.add(result)
db.commit()

# 4. 更新任务完成状态
task.status = TaskStatus.SUCCESS
task.completed_at = datetime.utcnow()
task.result_id = result.id
db.commit()
```

### 🔍 常用查询

```python
# 查询待处理任务
pending_tasks = db.query(Task).filter(
    Task.status == TaskStatus.PENDING
).order_by(Task.created_at.asc()).limit(10).all()

# 查询特定 URL 的任务
task = db.query(Task).filter(Task.url == "https://example.com").first()

# 查询任务及其结果（JOIN）
from sqlalchemy.orm import joinedload

task_with_result = db.query(Task).options(
    joinedload(Task.result)
).filter(Task.id == task_id).first()

# 统计各状态的任务数
from sqlalchemy import func

stats = db.query(
    Task.status,
    func.count(Task.id)
).group_by(Task.status).all()

# 查询最近的失败任务
failed_tasks = db.query(Task).filter(
    Task.status == TaskStatus.FAILED
).order_by(Task.completed_at.desc()).limit(10).all()

# JSONB 查询示例
results = db.query(Result).filter(
    Result.metadata['status_code'].astext == '200'
).all()
```

---

## 🎯 面试话术模板

### 项目介绍（30 秒）

> "在数据模型设计上，我使用了 **SQLAlchemy ORM**，采用了 **Mixin 模式**来复用代码。
>
> 核心有两个模型：**Task**（任务）和 **Result**（结果），是 **1:1 关系**。
>
> 使用了 **UUID 作为主键**（分布式友好），**Enum 保证状态类型安全**，**JSONB 存储灵活的结构化数据**。
>
> 在性能优化上，为高频查询的字段（url、status）**添加了索引**，并通过外键约束保证**数据一致性**。"

### 深入技术细节（根据面试官提问）

**如果问 Mixin**：

> "我用 Mixin 模式复用了两个通用功能：UUIDMixin 统一主键格式，TimestampMixin 自动管理创建和更新时间。这样避免了在每个模型中重复写这些字段，符合 DRY 原则。"

**如果问索引**：

> "我分析了业务场景，发现最频繁的查询是按 status 获取待处理任务，按 url 检查是否已存在。所以给这两个字段加了索引，查询性能提升明显。"

**如果问 JSONB**：

> "我用 JSONB 存储链接和元数据，因为每个网页的链接数量不同，结构不固定。JSONB 比创建单独的表更简单，而且 PostgreSQL 的 JSONB 支持索引和查询，性能也不错。"

---

## ✅ 总结

### 核心设计亮点

1. ✅ **Mixin 模式** - 代码复用，DRY 原则
2. ✅ **Enum 类型** - 类型安全，防止拼写错误
3. ✅ **UUID 主键** - 分布式友好，不会冲突
4. ✅ **索引优化** - url 和 status 字段加索引
5. ✅ **JSONB 类型** - 灵活存储复杂数据
6. ✅ **外键约束** - 保证数据一致性
7. ✅ **自动时间戳** - created_at/updated_at 自动管理

### 面试加分项

- 💡 能画出 ERD 图
- 💡 能解释每个设计决策
- 💡 能讨论性能优化
- 💡 能处理并发问题
- 💡 能扩展到大规模场景

---
