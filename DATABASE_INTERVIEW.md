# 数据库相关面试问题大全

> 基于 WebProbe 项目的数据库面试准备
>
> 包含：基础概念、SQL、索引、事务、设计、优化、实战

---

## 📚 目录

1. [数据库基础概念](#1-数据库基础概念)
2. [SQL 查询](#2-sql-查询)
3. [索引优化](#3-索引优化)
4. [事务与并发](#4-事务与并发)
5. [数据库设计](#5-数据库设计)
6. [性能优化](#6-性能优化)
7. [PostgreSQL 特性](#7-postgresql-特性)
8. [ORM 相关](#8-orm-相关)
9. [实战场景题](#9-实战场景题)
10. [数据库监控](#10-数据库监控)

---

## 1. 数据库基础概念

### Q1.1：什么是主键？为什么需要主键？

**答案**：

```
主键（Primary Key）是表中能唯一标识每一行记录的字段或字段组合。

特点：
1. 唯一性：不能重复
2. 非空性：不能为 NULL
3. 稳定性：值不应该改变

为什么需要：
✅ 唯一标识记录
✅ 建立表间关系（外键引用）
✅ 提高查询性能（自动创建索引）
✅ 保证数据完整性
```

**WebProbe 项目示例**：

```python
class Task(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    # UUID 作为主键：
    # - 全局唯一
    # - 分布式友好
    # - 安全性高（不可预测）
```

**追问**：为什么你选择 UUID 而不是自增 ID？

```
答：考虑到未来可能的分布式部署：
- UUID 不会冲突（多服务器同时生成）
- 安全性更高（防止遍历攻击）
- 可以在应用层生成，减轻数据库压力

缺点是占用空间大（16字节 vs 4字节），但现代硬件可接受。
```

---

### Q1.2：什么是外键？外键约束的作用是什么？

**答案**：

```
外键（Foreign Key）是一个表中引用另一个表主键的字段。

作用：
1. 维护引用完整性：保证引用的记录存在
2. 级联操作：自动处理关联数据
3. 数据一致性：防止孤儿记录

级联选项：
- CASCADE：级联删除/更新
- SET NULL：设为 NULL
- RESTRICT：禁止操作
- NO ACTION：默认行为
```

**WebProbe 项目示例**：

```python
class Result(Base):
    task_id = Column(UUID, ForeignKey("tasks.id"), nullable=False, unique=True)

    # 含义：
    # - Result 必须关联一个 Task
    # - Task 删除时，Result 如何处理？（默认 RESTRICT）
    # - unique=True 保证 1:1 关系
```

**SQL 示例**：

```sql
-- 创建外键约束
ALTER TABLE results
ADD CONSTRAINT fk_task_id
FOREIGN KEY (task_id)
REFERENCES tasks(id)
ON DELETE CASCADE;  -- Task 删除时，Result 也删除
```

**追问**：什么时候不应该用外键？

```
答：
1. 高并发写入场景：外键检查影响性能
2. 分库分表：跨库无法建立外键
3. 临时数据表：不需要严格约束

我们可以在应用层保证一致性：
- 先插入父表，再插入子表
- 事务保证原子性
- 定期数据校验
```

---

### Q1.3：解释 ACID 特性

**答案**：

**A - Atomicity（原子性）**

```
事务中的所有操作要么全部成功，要么全部失败。

例子：转账
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 扣款
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- 入账
COMMIT;

如果第二条失败，第一条也会回滚。
```

**C - Consistency（一致性）**

```
事务执行前后，数据库从一个一致状态转到另一个一致状态。

例子：
- 转账前后总金额不变
- 外键约束不被破坏
- 检查约束（CHECK）有效
```

**I - Isolation（隔离性）**

```
并发事务互不干扰。

隔离级别（从低到高）：
1. READ UNCOMMITTED：脏读
2. READ COMMITTED：不可重复读
3. REPEATABLE READ：幻读
4. SERIALIZABLE：完全隔离
```

**D - Durability（持久性）**

```
事务提交后，数据永久保存，即使系统崩溃。

实现：
- WAL（Write-Ahead Logging）
- 数据刷盘
- 备份恢复
```

**WebProbe 项目示例**：

```python
# 创建任务和触发抓取是原子操作
try:
    task = task_repo.create(task_data)  # 插入数据库
    scrape_task.delay(task.id)          # 触发 Celery
    db.commit()                          # 提交
except:
    db.rollback()                        # 失败回滚
    raise
```

---

### Q1.4：什么是数据库范式？为什么要范式化？

**答案**：

**第一范式（1NF）- 原子性**

```
每个字段不可再分。

❌ 错误：
| id | name | phones           |
|----|------|------------------|
| 1  | Tom  | 123-456, 789-012 |

✅ 正确：
| id | name | phone    |
|----|------|----------|
| 1  | Tom  | 123-456  |
| 1  | Tom  | 789-012  |
```

**第二范式（2NF）- 消除部分依赖**

```
非主键字段完全依赖主键。

❌ 错误：
| order_id | product_id | product_name | quantity |
|----------|------------|--------------|----------|
| 1        | 101        | iPhone       | 2        |

product_name 只依赖 product_id，不依赖 order_id

✅ 正确：分两张表
orders: order_id, product_id, quantity
products: product_id, product_name
```

**第三范式（3NF）- 消除传递依赖**

```
非主键字段不依赖其他非主键字段。

❌ 错误：
| task_id | url | domain      | domain_ip  |
|---------|-----|-------------|------------|
| 1       | ... | example.com | 1.2.3.4    |

domain_ip 依赖 domain，而 domain 依赖 task_id（传递依赖）

✅ 正确：分两张表
tasks: task_id, url, domain
domains: domain, domain_ip
```

**WebProbe 项目示例**：

```python
# 我们的设计符合 3NF
class Task(Base):
    # 所有字段直接依赖 id
    id = Column(UUID, primary_key=True)
    url = Column(String)
    status = Column(Enum)

class Result(Base):
    # 所有字段直接依赖 id
    id = Column(UUID, primary_key=True)
    task_id = Column(UUID, ForeignKey("tasks.id"))
    title = Column(String)
```

**反范式化**：

```
为了性能，有时会违反范式：

# 例：冗余 task.url 到 result 表
class Result(Base):
    task_id = Column(UUID)
    url = Column(String)  # 冗余字段，避免 JOIN

优点：查询快（不用 JOIN）
缺点：数据冗余，更新复杂
```

---

## 2. SQL 查询

### Q2.1：写出查询所有状态为 PENDING 的任务的 SQL

**基础查询**：

```sql
SELECT * FROM tasks WHERE status = 'PENDING';
```

**带排序**：

```sql
SELECT * FROM tasks
WHERE status = 'PENDING'
ORDER BY created_at DESC;
```

**带分页**：

```sql
SELECT * FROM tasks
WHERE status = 'PENDING'
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;  -- 第一页，每页10条
```

**带统计**：

```sql
SELECT
    status,
    COUNT(*) as count,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM tasks
GROUP BY status;
```

**SQLAlchemy 写法**：

```python
# 基础查询
tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).all()

# 带排序
tasks = db.query(Task)\
    .filter(Task.status == TaskStatus.PENDING)\
    .order_by(Task.created_at.desc())\
    .all()

# 带分页
tasks = db.query(Task)\
    .filter(Task.status == TaskStatus.PENDING)\
    .order_by(Task.created_at.desc())\
    .limit(10)\
    .offset(0)\
    .all()
```

---

### Q2.2：如何查询每个状态的任务数量？

**SQL**：

```sql
SELECT
    status,
    COUNT(*) as task_count
FROM tasks
GROUP BY status
ORDER BY task_count DESC;
```

**结果**：

```
| status      | task_count |
|-------------|------------|
| PENDING     | 150        |
| SUCCESS     | 89         |
| PROCESSING  | 12         |
| FAILED      | 8          |
```

**SQLAlchemy**：

```python
from sqlalchemy import func

counts = db.query(
    Task.status,
    func.count(Task.id).label('task_count')
).group_by(Task.status).all()

# 结果：
# [('PENDING', 150), ('SUCCESS', 89), ...]
```

**Repository 封装**：

```python
class TaskRepository:
    def count_by_status(self, status: TaskStatus) -> int:
        return self.db.query(Task).filter(Task.status == status).count()

    def get_status_summary(self) -> dict:
        counts = self.db.query(
            Task.status,
            func.count(Task.id)
        ).group_by(Task.status).all()

        return {status: count for status, count in counts}
```

---

### Q2.3：查询有结果的任务（JOIN 查询）

**INNER JOIN**：

```sql
-- 只查询有结果的任务
SELECT
    t.id,
    t.url,
    t.status,
    r.title,
    r.scraped_at
FROM tasks t
INNER JOIN results r ON t.id = r.task_id
WHERE t.status = 'SUCCESS';
```

**LEFT JOIN**：

```sql
-- 查询所有任务及其结果（可能没有结果）
SELECT
    t.id,
    t.url,
    t.status,
    r.title
FROM tasks t
LEFT JOIN results r ON t.id = r.task_id;
```

**查询没有结果的任务**：

```sql
SELECT t.*
FROM tasks t
LEFT JOIN results r ON t.id = r.task_id
WHERE r.id IS NULL;
```

**SQLAlchemy**：

```python
# INNER JOIN
tasks_with_results = db.query(Task, Result)\
    .join(Result, Task.id == Result.task_id)\
    .filter(Task.status == TaskStatus.SUCCESS)\
    .all()

# LEFT JOIN
all_tasks = db.query(Task, Result)\
    .outerjoin(Result, Task.id == Result.task_id)\
    .all()

# 没有结果的任务
tasks_without_results = db.query(Task)\
    .outerjoin(Result)\
    .filter(Result.id == None)\
    .all()
```

---

### Q2.4：查询最近 7 天创建的任务

**SQL**：

```sql
SELECT * FROM tasks
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

**PostgreSQL 特定**：

```sql
-- 使用 CURRENT_DATE
SELECT * FROM tasks
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';

-- 按天分组统计
SELECT
    DATE(created_at) as date,
    COUNT(*) as count
FROM tasks
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

**SQLAlchemy**：

```python
from datetime import datetime, timedelta

seven_days_ago = datetime.utcnow() - timedelta(days=7)

recent_tasks = db.query(Task)\
    .filter(Task.created_at >= seven_days_ago)\
    .order_by(Task.created_at.desc())\
    .all()
```

---

### Q2.5：JSONB 字段查询

**查询 extra_data 中 status_code 为 200 的结果**：

```sql
-- PostgreSQL JSONB 查询
SELECT * FROM results
WHERE extra_data->>'status_code' = '200';

-- 查询数组包含特定元素
SELECT * FROM results
WHERE links @> '["https://example.com"]';

-- 查询嵌套 JSON
SELECT * FROM results
WHERE extra_data->'headers'->>'content-type' = 'text/html';
```

**创建 JSONB 索引**：

```sql
-- GIN 索引（通用倒排索引）
CREATE INDEX idx_extra_data ON results USING GIN (extra_data);

-- 特定键索引
CREATE INDEX idx_status_code ON results ((extra_data->>'status_code'));
```

**SQLAlchemy**：

```python
# 查询 JSONB 字段
results = db.query(Result)\
    .filter(Result.extra_data['status_code'].astext == '200')\
    .all()

# 查询嵌套字段
results = db.query(Result)\
    .filter(Result.extra_data['headers']['content-type'].astext == 'text/html')\
    .all()
```

---

## 3. 索引优化

### Q3.1：什么是索引？为什么需要索引？

**答案**：

```
索引是数据库表中一列或多列值的排序结构，用于快速查找数据。

类比：书的目录
- 没有目录：从头到尾翻书（全表扫描）
- 有目录：直接翻到对应页（索引查询）

优点：
✅ 加快查询速度
✅ 加速排序（ORDER BY）
✅ 加速分组（GROUP BY）
✅ 唯一性约束

缺点：
❌ 占用存储空间
❌ 降低写入速度（INSERT/UPDATE/DELETE）
❌ 需要维护成本
```

**WebProbe 项目示例**：

```python
class Task(Base):
    url = Column(String(2048), index=True)      # 频繁查询
    status = Column(Enum(TaskStatus), index=True)  # 频繁过滤

# 生成的 SQL：
# CREATE INDEX ix_tasks_url ON tasks (url);
# CREATE INDEX ix_tasks_status ON tasks (status);
```

**性能对比**：

```sql
-- 无索引：全表扫描 100 万行 → 1000ms
SELECT * FROM tasks WHERE status = 'PENDING';

-- 有索引：索引查找 10 行 → 5ms
SELECT * FROM tasks WHERE status = 'PENDING';
```

---

### Q3.2：索引的类型有哪些？

**B-Tree 索引（默认）**

```
特点：
- 平衡树结构
- 适合范围查询、排序
- 大部分场景的首选

适用场景：
- =、>、<、>=、<=、BETWEEN
- ORDER BY
- 前缀匹配（LIKE 'abc%'）

不适用：
- 后缀匹配（LIKE '%abc'）
- 函数操作（UPPER(name)）
```

**Hash 索引**

```
特点：
- 哈希表结构
- 只支持等值查询
- 速度极快

适用：= 查询
不适用：范围查询、排序
```

**GIN 索引（通用倒排索引）**

```
特点：
- 适合多值类型
- PostgreSQL 特有

适用场景：
- JSONB 查询
- 数组查询
- 全文搜索
```

**WebProbe 项目示例**：

```sql
-- B-Tree（默认）
CREATE INDEX idx_tasks_status ON tasks (status);

-- GIN（JSONB）
CREATE INDEX idx_extra_data ON results USING GIN (extra_data);

-- 复合索引
CREATE INDEX idx_status_created ON tasks (status, created_at);
```

---

### Q3.3：什么时候应该创建索引？

**应该创建索引的场景**：

```
1. WHERE 子句中的列
   SELECT * FROM tasks WHERE status = 'PENDING';
   → 给 status 加索引

2. JOIN 条件列
   SELECT * FROM tasks t JOIN results r ON t.id = r.task_id;
   → task_id 自动有索引（外键）

3. ORDER BY 列
   SELECT * FROM tasks ORDER BY created_at DESC;
   → 给 created_at 加索引

4. GROUP BY 列
   SELECT status, COUNT(*) FROM tasks GROUP BY status;
   → 给 status 加索引

5. 频繁查询的列
   经常用于搜索、过滤的列
```

**不应该创建索引的场景**：

```
1. 小表（< 1000 行）
   全表扫描更快

2. 频繁更新的列
   维护索引成本高

3. 选择性低的列
   如：性别（只有男/女）
   扫描半个表还不如全表扫描

4. 很少查询的列
   浪费空间

5. 大文本列（TEXT, BLOB）
   可以考虑全文索引
```

**WebProbe 项目决策**：

```python
class Task(Base):
    id = Column(UUID, primary_key=True)           # 自动索引
    url = Column(String, index=True)              # ✅ 需要：检查重复
    status = Column(Enum, index=True)             # ✅ 需要：频繁过滤
    created_at = Column(DateTime)                 # ❌ 暂不需要：少用排序
    error_message = Column(Text)                  # ❌ 不需要：很少查询
```

---

### Q3.4：什么是复合索引？如何使用？

**答案**：

```
复合索引（Composite Index）：多个列组合的索引。

语法：
CREATE INDEX idx_name ON table (col1, col2, col3);
```

**最左前缀原则**：

```sql
CREATE INDEX idx_status_created ON tasks (status, created_at);

-- ✅ 会使用索引
SELECT * FROM tasks WHERE status = 'PENDING';
SELECT * FROM tasks WHERE status = 'PENDING' AND created_at > '2024-01-01';

-- ❌ 不会使用索引（跳过了第一列）
SELECT * FROM tasks WHERE created_at > '2024-01-01';
```

**索引顺序**：

```
规则：选择性高的列放前面

选择性 = 不同值数量 / 总行数

示例：
tasks 表有 10000 行
- status: 4 个不同值（PENDING, PROCESSING, SUCCESS, FAILED）
  选择性 = 4 / 10000 = 0.0004
- url: 9500 个不同值
  选择性 = 9500 / 10000 = 0.95

正确顺序：
CREATE INDEX idx_url_status ON tasks (url, status);  -- url 在前
```

**WebProbe 项目示例**：

```sql
-- 场景：经常按状态和时间查询
SELECT * FROM tasks
WHERE status = 'PENDING'
ORDER BY created_at DESC
LIMIT 10;

-- 创建复合索引
CREATE INDEX idx_status_created ON tasks (status, created_at DESC);

-- 性能提升：
-- 无索引：全表扫描 + 排序 → 500ms
-- 有索引：索引扫描 → 10ms
```

---

### Q3.5：如何分析索引是否生效？

**使用 EXPLAIN ANALYZE**：

```sql
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE status = 'PENDING';
```

**输出示例（无索引）**：

```
Seq Scan on tasks  (cost=0.00..18.50 rows=5 width=100) (actual time=0.015..0.234 rows=5 loops=1)
  Filter: (status = 'PENDING'::task_status)
  Rows Removed by Filter: 995
Planning Time: 0.123 ms
Execution Time: 0.267 ms
```

**Seq Scan** = 全表扫描（慢）

**输出示例（有索引）**：

```
Index Scan using idx_tasks_status on tasks  (cost=0.28..8.30 rows=5 width=100) (actual time=0.012..0.015 rows=5 loops=1)
  Index Cond: (status = 'PENDING'::task_status)
Planning Time: 0.098 ms
Execution Time: 0.032 ms
```

**Index Scan** = 索引扫描（快）

**关键指标**：

```
1. Scan Type:
   - Seq Scan: 全表扫描（❌）
   - Index Scan: 索引扫描（✅）
   - Index Only Scan: 只扫描索引（✅✅）

2. Cost:
   - 越低越好
   - 第一个数字：启动成本
   - 第二个数字：总成本

3. Actual Time:
   - 实际执行时间
   - 第一个数字：返回第一行时间
   - 第二个数字：返回所有行时间

4. Rows:
   - 预估行数 vs 实际行数
   - 差距太大说明统计信息过期
```

**PostgreSQL 查看索引使用情况**：

```sql
-- 查看表的所有索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'tasks';

-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public';

-- 查看未使用的索引
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey';
```

---

## 4. 事务与并发

### Q4.1：什么是事务？如何使用？

**答案**：

```
事务（Transaction）是一组原子性的数据库操作。

基本操作：
BEGIN;    -- 开始事务
...       -- SQL 语句
COMMIT;   -- 提交
ROLLBACK; -- 回滚
```

**示例：创建任务并记录日志**：

```sql
BEGIN;

-- 创建任务
INSERT INTO tasks (id, url, status)
VALUES (uuid_generate_v4(), 'https://example.com', 'PENDING');

-- 记录日志
INSERT INTO logs (action, details)
VALUES ('create_task', 'Created task for example.com');

COMMIT;  -- 两条语句要么都成功，要么都失败
```

**SQLAlchemy 事务**：

```python
# 自动事务（推荐）
try:
    task = task_repo.create(task_data)
    log_repo.create(log_data)
    db.commit()
except Exception as e:
    db.rollback()
    raise

# 显式事务
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    session.add(task)
    session.add(log)
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()
```

**FastAPI 依赖注入**：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
        # 自动 commit（如果没有异常）
    except:
        db.rollback()
        raise
    finally:
        db.close()
```

---

### Q4.2：事务的隔离级别有哪些？

**四个隔离级别（从低到高）**：

**1. READ UNCOMMITTED（读未提交）**

```
问题：脏读（Dirty Read）

事务 A                事务 B
BEGIN;
UPDATE tasks          BEGIN;
SET status='DONE'     SELECT status FROM tasks;  -- 读到 'DONE'
WHERE id=1;           -- 但 A 还没提交！
ROLLBACK;             -- 读到了脏数据

PostgreSQL 不支持此级别
```

**2. READ COMMITTED（读已提交）- PostgreSQL 默认**

```
问题：不可重复读（Non-repeatable Read）

事务 A                事务 B
BEGIN;
SELECT COUNT(*)
FROM tasks            -- 返回 100
WHERE status='PENDING';

                      BEGIN;
                      INSERT INTO tasks ...;
                      COMMIT;

SELECT COUNT(*)
FROM tasks            -- 返回 101（不一致！）
WHERE status='PENDING';
COMMIT;
```

**3. REPEATABLE READ（可重复读）**

```
问题：幻读（Phantom Read）

PostgreSQL 的 REPEATABLE READ 实际上避免了幻读（通过 MVCC）

事务 A                事务 B
BEGIN;
SELECT * FROM tasks   -- 返回 10 行
WHERE status='PENDING';

                      INSERT INTO tasks ...;
                      COMMIT;

SELECT * FROM tasks
WHERE status='PENDING'; -- 还是返回 10 行（一致）
COMMIT;
```

**4. SERIALIZABLE（可串行化）**

```
最严格的隔离级别，事务串行执行。

优点：完全隔离
缺点：性能最差

适用场景：
- 金融系统
- 库存扣减
- 关键业务
```

**设置隔离级别**：

```sql
-- 会话级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 事务级别
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
...
COMMIT;
```

**SQLAlchemy**：

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    isolation_level="REPEATABLE READ"
)
```

**WebProbe 项目选择**：

```
默认 READ COMMITTED 足够：
- 任务创建是独立的
- 不需要严格串行化
- 性能更好

如果需要严格一致性（如库存扣减）：
使用 SERIALIZABLE 或应用层锁
```

---

### Q4.3：如何处理并发冲突？

**场景：多个请求同时创建相同 URL 的任务**

**问题演示**：

```python
# 请求 1 和请求 2 同时到达
def create_task(url: str):
    # 1. 检查是否存在
    existing = task_repo.get_by_url(url)
    if existing:
        return existing

    # 2. 不存在，创建新任务
    task = task_repo.create({"url": url})
    return task

# 结果：创建了两个重复任务！
```

**解决方案 1：唯一约束**

```sql
-- 数据库层保证唯一
CREATE UNIQUE INDEX idx_unique_url ON tasks (url);

-- Python 捕获异常
try:
    task = task_repo.create({"url": url})
except IntegrityError:
    # 违反唯一约束，查询已存在的
    task = task_repo.get_by_url(url)
```

**解决方案 2：SELECT FOR UPDATE（悲观锁）**

```python
def create_task(url: str):
    # 锁定行，其他事务等待
    existing = db.query(Task)\
        .filter(Task.url == url)\
        .with_for_update()\
        .first()

    if existing:
        return existing

    task = task_repo.create({"url": url})
    db.commit()
    return task
```

**解决方案 3：乐观锁**

```python
class Task(Base):
    version = Column(Integer, default=1)  # 版本号

def update_task(task_id, new_status):
    task = task_repo.get_by_id(task_id)
    old_version = task.version

    # 更新时检查版本号
    result = db.execute(
        update(Task)
        .where(Task.id == task_id)
        .where(Task.version == old_version)
        .values(
            status=new_status,
            version=old_version + 1
        )
    )

    if result.rowcount == 0:
        raise ConflictError("Task was modified by another transaction")
```

**解决方案 4：分布式锁（Redis）**

```python
import redis
from contextlib import contextmanager

@contextmanager
def redis_lock(key: str, timeout: int = 10):
    """Redis 分布式锁"""
    lock_key = f"lock:{key}"
    lock_value = str(uuid.uuid4())

    # 获取锁
    acquired = redis_client.set(lock_key, lock_value, nx=True, ex=timeout)
    if not acquired:
        raise LockError("Failed to acquire lock")

    try:
        yield
    finally:
        # 释放锁（只有持有者才能释放）
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        redis_client.eval(lua_script, 1, lock_key, lock_value)

# 使用
def create_task(url: str):
    with redis_lock(f"task:{url}"):
        existing = task_repo.get_by_url(url)
        if existing:
            return existing
        return task_repo.create({"url": url})
```

**WebProbe 项目推荐**：

```
组合使用：
1. 唯一索引（数据库层）
2. Redis 锁（应用层，高并发场景）

CREATE UNIQUE INDEX idx_url ON tasks (url)
WHERE status IN ('PENDING', 'PROCESSING');

只对进行中的任务做唯一约束，完成的任务可以重复抓取。
```

---

## 5. 数据库设计

### Q5.1：设计一个任务调度系统的数据库

**需求**：

```
- 用户可以提交任务
- 任务定时执行
- 记录执行历史
- 支持任务依赖
```

**表设计**：

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 任务表
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    schedule VARCHAR(50),  -- cron 表达式
    command TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 任务执行历史
CREATE TABLE task_executions (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id),
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output TEXT,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 任务依赖
CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id),
    depends_on_id UUID NOT NULL REFERENCES tasks(id),
    UNIQUE(task_id, depends_on_id)
);

-- 索引
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_enabled ON tasks(enabled);
CREATE INDEX idx_executions_task ON task_executions(task_id);
CREATE INDEX idx_executions_status ON task_executions(status);
```

**面试亮点**：

```
1. 职责分离：任务定义 vs 执行历史
2. 外键约束：保证数据一致性
3. 索引设计：常查询字段加索引
4. 灵活性：cron 表达式支持复杂调度
5. 可扩展：依赖表支持 DAG（有向无环图）
```

---

### Q5.2：如何设计一个评论系统？

**需求**：

```
- 支持多级评论（评论的评论）
- 显示评论树
- 统计评论数
```

**方案 1：邻接表（Adjacency List）**

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES comments(id),
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 查询某条评论的所有子评论
SELECT * FROM comments WHERE parent_id = 'xxx';

-- 缺点：查询整个树需要递归，性能差
```

**方案 2：路径枚举（Path Enumeration）**

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    path VARCHAR(255) NOT NULL,  -- '1/2/3/4'
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_path ON comments(path);

-- 查询所有子评论
SELECT * FROM comments WHERE path LIKE '1/2/%';

-- 优点：查询快
-- 缺点：path 更新复杂
```

**方案 3：嵌套集（Nested Set）**

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    lft INTEGER NOT NULL,
    rgt INTEGER NOT NULL,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 查询所有子节点
SELECT * FROM comments
WHERE lft BETWEEN parent.lft AND parent.rgt;

-- 优点：查询极快
-- 缺点：插入更新复杂
```

**WebProbe 推荐**：

```
小规模：邻接表 + 递归查询（PostgreSQL WITH RECURSIVE）
大规模：路径枚举
极大规模：嵌套集 + 缓存
```

**PostgreSQL 递归查询**：

```sql
-- 查询评论树
WITH RECURSIVE comment_tree AS (
    -- 根评论
    SELECT * FROM comments WHERE id = 'root_id'

    UNION ALL

    -- 递归查询子评论
    SELECT c.* FROM comments c
    INNER JOIN comment_tree ct ON c.parent_id = ct.id
)
SELECT * FROM comment_tree;
```

---

## 6. 性能优化

### Q6.1：如何优化慢查询？

**步骤**：

**1. 识别慢查询**

```sql
-- PostgreSQL 慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 记录 > 1s 的查询

-- 查看慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**2. 分析查询计划**

```sql
EXPLAIN ANALYZE
SELECT t.*, r.title
FROM tasks t
LEFT JOIN results r ON t.id = r.task_id
WHERE t.status = 'PENDING'
ORDER BY t.created_at DESC
LIMIT 10;
```

**3. 优化策略**

**策略 1：添加索引**

```sql
-- 问题：Seq Scan on tasks
-- 解决：添加索引
CREATE INDEX idx_status_created ON tasks (status, created_at DESC);
```

**策略 2：避免 SELECT \***

```sql
-- ❌ 慢：查询所有字段
SELECT * FROM results;

-- ✅ 快：只查询需要的字段
SELECT id, title, scraped_at FROM results;
```

**策略 3：分页优化**

```sql
-- ❌ 慢：OFFSET 很大时性能差
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10 OFFSET 100000;

-- ✅ 快：基于游标的分页
SELECT * FROM tasks
WHERE created_at < '2024-01-01'
ORDER BY created_at DESC
LIMIT 10;
```

**策略 4：JOIN 优化**

```sql
-- ❌ 慢：大表 JOIN
SELECT t.*, r.*
FROM tasks t
LEFT JOIN results r ON t.id = r.task_id;

-- ✅ 快：先过滤再 JOIN
SELECT t.*, r.*
FROM (
    SELECT * FROM tasks WHERE status = 'SUCCESS'
) t
LEFT JOIN results r ON t.id = r.task_id;
```

**策略 5：使用 UNION ALL 代替 OR**

```sql
-- ❌ 慢：OR 条件难以优化
SELECT * FROM tasks
WHERE status = 'PENDING' OR status = 'PROCESSING';

-- ✅ 快：UNION ALL
SELECT * FROM tasks WHERE status = 'PENDING'
UNION ALL
SELECT * FROM tasks WHERE status = 'PROCESSING';
```

---

### Q6.2：如何设计高性能的分页？

**传统分页（OFFSET）**：

```sql
-- 第 1 页
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- 第 1000 页
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10 OFFSET 9990;
-- 问题：扫描了 10000 行，只返回 10 行
```

**游标分页（Cursor-based）**：

```sql
-- 第 1 页
SELECT * FROM tasks
ORDER BY created_at DESC
LIMIT 10;

-- 第 2 页（基于上一页最后一条记录）
SELECT * FROM tasks
WHERE created_at < '2024-01-15 10:00:00'
ORDER BY created_at DESC
LIMIT 10;
```

**Keyset 分页**：

```sql
-- 使用主键
SELECT * FROM tasks
WHERE id > 'last_id'
ORDER BY id
LIMIT 10;

-- 优点：性能稳定，不受页数影响
-- 缺点：不能随机跳页
```

**WebProbe 项目实现**：

```python
class TaskRepository:
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        cursor: Optional[datetime] = None
    ) -> dict:
        query = self.db.query(Task)

        # 游标分页
        if cursor:
            query = query.filter(Task.created_at < cursor)

        tasks = query.order_by(Task.created_at.desc())\
            .limit(page_size)\
            .all()

        # 下一页游标
        next_cursor = tasks[-1].created_at if tasks else None

        return {
            "tasks": tasks,
            "next_cursor": next_cursor,
            "has_more": len(tasks) == page_size
        }
```

---

### Q6.3：数据库连接池如何配置？

**连接池参数**：

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,

    # 核心参数
    pool_size=10,          # 保持的连接数
    max_overflow=20,       # 额外可创建的连接数
    pool_timeout=30,       # 获取连接的超时时间（秒）
    pool_recycle=3600,     # 连接回收时间（秒）
    pool_pre_ping=True,    # 使用前检查连接是否有效

    # 其他参数
    echo=False,            # 是否打印 SQL（生产环境关闭）
    echo_pool=False,       # 是否打印连接池日志
)
```

**参数说明**：

**pool_size（连接池大小）**

```
建议值：
- 小型应用：5-10
- 中型应用：10-20
- 大型应用：20-50

计算公式：
pool_size = (core_count * 2) + 磁盘数

例如：4 核 CPU + 1 个磁盘 = 10 个连接
```

**max_overflow（溢出连接数）**

```
peak_connections = pool_size + max_overflow

例如：pool_size=10, max_overflow=20
- 正常：10 个连接
- 峰值：30 个连接
- 超过 30：等待或报错
```

**pool_recycle（连接回收）**

```
问题：数据库会关闭长时间空闲的连接
解决：定期回收连接

建议：小于数据库的 wait_timeout
PostgreSQL 默认没有超时，可设为 1 小时
```

**pool_pre_ping（连接检查）**

```
作用：使用前 ping 一下，确保连接有效
代价：每次查询多一次网络往返

建议：生产环境开启
```

**监控连接池**：

```python
# 查看连接池状态
print(f"Pool size: {engine.pool.size()}")
print(f"Checked out: {engine.pool.checkedout()}")
print(f"Overflow: {engine.pool.overflow()}")
print(f"Checked in: {engine.pool.checkedin()}")
```

---

## 7. PostgreSQL 特性

### Q7.1：JSONB 的优势是什么？

**JSONB vs JSON**：

```
JSON：存储为文本，查询时解析
JSONB：存储为二进制，支持索引和高效查询

选择：几乎总是用 JSONB
```

**操作符**：

```sql
-- -> 返回 JSON 对象
SELECT extra_data->'headers' FROM results;

-- ->> 返回文本
SELECT extra_data->>'status_code' FROM results;

-- @> 包含
SELECT * FROM results WHERE extra_data @> '{"status_code": 200}';

-- ? 存在键
SELECT * FROM results WHERE extra_data ? 'headers';

-- #> 嵌套路径
SELECT extra_data#>'{headers,content-type}' FROM results;
```

**索引**：

```sql
-- GIN 索引（推荐）
CREATE INDEX idx_extra_data ON results USING GIN (extra_data);

-- 表达式索引
CREATE INDEX idx_status_code ON results ((extra_data->>'status_code'));
```

**WebProbe 项目示例**：

```python
class Result(Base):
    extra_data = Column(JSONB)  # 灵活存储 HTTP 响应信息

# 查询
results = db.query(Result)\
    .filter(Result.extra_data['status_code'].astext == '200')\
    .all()
```

---

### Q7.2：PostgreSQL 的 UUID 类型

**生成 UUID**：

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 生成 UUID
SELECT uuid_generate_v4();  -- 随机 UUID

-- 在表中使用
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL
);
```

**SQLAlchemy**：

```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Task(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # as_uuid=True: Python 中使用 uuid.UUID 对象
```

**UUID vs 自增 ID**：

```
UUID 优势：
✅ 全局唯一
✅ 分布式友好
✅ 安全性高
✅ 可在应用层生成

自增 ID 优势：
✅ 占用空间小（4 vs 16 字节）
✅ 有序（对 B-Tree 索引友好）
✅ 可读性好

WebProbe 选择 UUID：
考虑未来可能的微服务架构
```

---

### Q7.3：PostgreSQL 的数组类型

**定义和使用**：

```sql
-- 定义数组列
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    title TEXT,
    tags TEXT[]  -- 文本数组
);

-- 插入数据
INSERT INTO posts (id, title, tags)
VALUES (uuid_generate_v4(), 'Hello', ARRAY['tech', 'python', 'database']);

-- 或使用 {} 语法
INSERT INTO posts (id, title, tags)
VALUES (uuid_generate_v4(), 'World', '{java,spring,orm}');

-- 查询包含特定标签的文章
SELECT * FROM posts WHERE 'python' = ANY(tags);

-- 查询包含所有标签的文章
SELECT * FROM posts WHERE tags @> ARRAY['python', 'database'];

-- 查询数组长度
SELECT title, array_length(tags, 1) FROM posts;
```

**索引数组**：

```sql
-- GIN 索引
CREATE INDEX idx_tags ON posts USING GIN (tags);
```

**SQLAlchemy**：

```python
from sqlalchemy.dialects.postgresql import ARRAY

class Post(Base):
    tags = Column(ARRAY(String))

# 查询
posts = db.query(Post).filter(Post.tags.contains(['python'])).all()
```

---

## 8. ORM 相关

### Q8.1：ORM 的 N+1 问题是什么？如何解决？

**问题演示**：

```python
# 查询所有任务及其结果
tasks = db.query(Task).all()  # 1 次查询

for task in tasks:
    print(task.result.title)  # N 次查询（每个 task 一次）

# 总共：1 + N 次查询
# 如果有 100 个任务 → 101 次查询！
```

**解决方案 1：JOIN（推荐）**

```python
# 使用 joinedload
from sqlalchemy.orm import joinedload

tasks = db.query(Task)\
    .options(joinedload(Task.result))\
    .all()

# 只有 1 次查询（LEFT JOIN）
```

**解决方案 2：子查询加载**

```python
from sqlalchemy.orm import subqueryload

tasks = db.query(Task)\
    .options(subqueryload(Task.result))\
    .all()

# 2 次查询：
# 1. SELECT * FROM tasks
# 2. SELECT * FROM results WHERE task_id IN (...)
```

**解决方案 3：立即加载**

```python
# 在模型中配置
class Task(Base):
    result = relationship("Result", lazy='joined')  # 默认 JOIN

# 或按需选择
tasks = db.query(Task).options(joinedload(Task.result)).all()
```

**WebProbe 项目配置**：

```python
class Task(Base):
    # 默认懒加载，按需加载
    result = relationship("Result", lazy='select')

# 需要时显式 JOIN
def get_tasks_with_results(self):
    return self.db.query(Task)\
        .options(joinedload(Task.result))\
        .all()
```

---

### Q8.2：如何在 SQLAlchemy 中使用原生 SQL？

**方法 1：execute()**

```python
# 查询
result = db.execute(
    "SELECT * FROM tasks WHERE status = :status",
    {"status": "PENDING"}
)
tasks = result.fetchall()

# 返回元组列表
for task in tasks:
    print(task.id, task.url)
```

**方法 2：text()**

```python
from sqlalchemy import text

result = db.execute(
    text("SELECT * FROM tasks WHERE status = :status"),
    {"status": "PENDING"}
)
```

**方法 3：from_statement()**

```python
from sqlalchemy import text

tasks = db.query(Task).from_statement(
    text("SELECT * FROM tasks WHERE status = :status")
).params(status="PENDING").all()

# 返回 Task 对象
```

**何时使用原生 SQL**：

```
1. 复杂查询（ORM 难以表达）
2. 性能优化（特定 PostgreSQL 特性）
3. 批量操作
4. 数据迁移
```

---

## 9. 实战场景题

### Q9.1：设计一个短网址系统的数据库

**需求**：

```
- 长网址 → 短网址
- 记录访问次数
- 支持自定义短码
- 防止重复
```

**表设计**：

```sql
CREATE TABLE short_urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    custom BOOLEAN DEFAULT FALSE,
    user_id UUID,
    visit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,

    INDEX idx_short_code (short_code),
    INDEX idx_long_url_hash (MD5(long_url))  -- 查重用
);

CREATE TABLE url_visits (
    id BIGSERIAL PRIMARY KEY,
    short_url_id BIGINT NOT NULL REFERENCES short_urls(id),
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    visited_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_short_url_id (short_url_id),
    INDEX idx_visited_at (visited_at)
);
```

**短码生成算法**：

```python
import hashlib
import base64

def generate_short_code(url: str, length: int = 6) -> str:
    # 方法 1：哈希 + Base62
    hash_digest = hashlib.md5(url.encode()).digest()
    short_code = base64.urlsafe_b64encode(hash_digest)[:length].decode()
    return short_code

    # 方法 2：自增 ID + Base62
    # id=12345 → Base62 → 'dnh'
```

**面试亮点**：

```
1. 短码唯一性：UNIQUE 约束
2. 长网址查重：哈希索引
3. 访问记录分表：历史数据与主表分离
4. 过期时间：支持临时链接
5. 性能优化：visit_count 冗余字段（避免 COUNT）
```

---

### Q9.2：如何设计一个点赞系统？

**需求**：

```
- 用户可以点赞文章
- 不能重复点赞
- 显示点赞数
- 显示是否点赞
```

**方案 1：关系表**

```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,  -- 冗余字段
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE post_likes (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES posts(id),
    user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(post_id, user_id),  -- 防止重复点赞
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id)
);

-- 查询文章和点赞状态
SELECT
    p.*,
    EXISTS(
        SELECT 1 FROM post_likes
        WHERE post_id = p.id AND user_id = 'current_user_id'
    ) as is_liked
FROM posts p
WHERE p.id = 'post_id';
```

**方案 2：Redis + 定期同步**

```python
# 点赞
redis.sadd(f"post:{post_id}:likes", user_id)
redis.incr(f"post:{post_id}:like_count")

# 取消点赞
redis.srem(f"post:{post_id}:likes", user_id)
redis.decr(f"post:{post_id}:like_count")

# 检查是否点赞
is_liked = redis.sismember(f"post:{post_id}:likes", user_id)

# 定时任务：同步到数据库
def sync_likes_to_db():
    for post_id in redis.keys("post:*:likes"):
        likes = redis.smembers(post_id)
        # 批量插入数据库
```

**方案对比**：

```
关系表：
✅ 数据可靠
✅ 支持复杂查询
❌ 高并发性能差

Redis：
✅ 性能极高
✅ 支持高并发
❌ 数据可能丢失
❌ 查询功能有限

推荐：组合使用
- 写入 Redis（快速响应）
- 定期同步数据库（持久化）
- 查询从数据库（复杂筛选）
```

---

### Q9.3：如何实现排行榜功能？

**需求**：

```
- 实时更新分数
- 查询 Top 100
- 查询用户排名
```

**方案 1：数据库**

```sql
CREATE TABLE leaderboard (
    user_id UUID PRIMARY KEY,
    score BIGINT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_score (score DESC)
);

-- 查询 Top 100
SELECT user_id, score,
       ROW_NUMBER() OVER (ORDER BY score DESC) as rank
FROM leaderboard
ORDER BY score DESC
LIMIT 100;

-- 查询用户排名
WITH ranked AS (
    SELECT user_id, score,
           ROW_NUMBER() OVER (ORDER BY score DESC) as rank
    FROM leaderboard
)
SELECT * FROM ranked WHERE user_id = 'xxx';
```

**方案 2：Redis Sorted Set（推荐）**

```python
# 更新分数
redis.zadd("leaderboard", {user_id: score})

# 增加分数
redis.zincrby("leaderboard", 100, user_id)

# Top 100（分数从高到低）
top100 = redis.zrevrange("leaderboard", 0, 99, withscores=True)

# 用户排名（从 0 开始）
rank = redis.zrevrank("leaderboard", user_id)

# 用户分数
score = redis.zscore("leaderboard", user_id)

# 获取某个范围的用户
users = redis.zrevrangebyscore("leaderboard", "+inf", 1000, start=0, num=10)
```

**方案对比**：

```
数据库：
✅ 持久化
✅ 支持复杂查询
❌ 性能较差（大量排名查询）

Redis Sorted Set：
✅ 性能极高（O(log N)）
✅ 内存占用小
✅ 操作简单
❌ 内存有限

推荐：
- 热门排行榜：Redis（前 10000 名）
- 历史排行榜：数据库（定期快照）
```

---

## 10. 数据库监控

### Q10.1：如何监控数据库性能？

**关键指标**：

**1. 连接数**

```sql
-- 当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 最大连接数
SHOW max_connections;

-- 按状态分组
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;
```

**2. 慢查询**

```sql
-- 开启慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 秒

-- 查看慢查询统计
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**3. 缓存命中率**

```sql
-- Buffer Cache 命中率（应该 > 99%）
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

**4. 表膨胀**

```sql
-- 查看表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 死元组（需要 VACUUM）
SELECT
    schemaname,
    tablename,
    n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

**5. 锁等待**

```sql
-- 当前锁
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

**监控工具**：

```
1. pg_stat_statements：查询统计
2. pg_stat_activity：当前连接
3. Prometheus + Grafana：可视化
4. pgAdmin：图形化管理
5. New Relic / Datadog：APM 监控
```

---

### Q10.2：数据库备份策略

**备份类型**：

**1. 逻辑备份（pg_dump）**

```bash
# 备份单个数据库
pg_dump dbname > backup.sql

# 备份所有数据库
pg_dumpall > backup.sql

# 自定义格式（可并行恢复）
pg_dump -Fc dbname > backup.dump

# 恢复
pg_restore -d dbname backup.dump
```

**2. 物理备份（pg_basebackup）**

```bash
# 基础备份
pg_basebackup -D /path/to/backup -Ft -z -P

# 优点：速度快，可用于主从复制
# 缺点：只能恢复整个数据库
```

**3. 持续归档（WAL）**

```bash
# 配置 postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'

# 恢复到任意时间点（PITR）
```

**备份策略（3-2-1 原则）**：

```
3 份副本：
- 生产数据库
- 本地备份
- 远程备份

2 种介质：
- 磁盘
- 云存储（S3）

1 份异地：
- 不同地理位置
```

**自动化备份脚本**：

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="webprobe_db"

# 备份
pg_dump -Fc $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.dump

# 上传到 S3
aws s3 cp $BACKUP_DIR/${DB_NAME}_${DATE}.dump s3://my-backups/

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete

# crontab 定时任务
# 0 2 * * * /path/to/backup.sh
```

---

## 📝 面试准备清单

### ✅ 必须掌握

- [ ] 主键、外键、索引的概念
- [ ] ACID 特性
- [ ] 常用 SQL 查询（JOIN、GROUP BY、子查询）
- [ ] 索引类型和使用场景
- [ ] 事务隔离级别
- [ ] 数据库范式
- [ ] ORM 基础操作

### ✅ 进阶掌握

- [ ] 复合索引和最左前缀原则
- [ ] EXPLAIN 分析查询计划
- [ ] N+1 问题及解决
- [ ] 并发控制（乐观锁、悲观锁）
- [ ] 连接池配置
- [ ] 慢查询优化
- [ ] 分页优化

### ✅ 高级掌握

- [ ] PostgreSQL JSONB
- [ ] 数组和枚举类型
- [ ] 递归查询（CTE）
- [ ] 物化视图
- [ ] 分区表
- [ ] 主从复制
- [ ] 性能监控

---

## 🎯 面试技巧

### 回答框架

**1. 概念题**

```
1. 是什么（定义）
2. 为什么（原因）
3. 怎么用（示例）
4. 注意点（最佳实践）
```

**2. 设计题**

```
1. 需求分析
2. 实体识别
3. 关系设计
4. 字段设计
5. 索引优化
6. 权衡说明
```

**3. 优化题**

```
1. 问题定位（EXPLAIN）
2. 分析原因
3. 解决方案（多个）
4. 效果对比
5. 监控验证
```

### 加分项

```
1. 结合实际项目经验
2. 提到权衡（trade-off）
3. 说明多种方案
4. 考虑边界情况
5. 关注性能和可维护性
6. 提到监控和运维
```

---

**祝你面试成功！** 🚀💪

---

**文档版本**：v1.0  
**最后更新**：2025-10-16
