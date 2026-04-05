# MySQL 数据库连接

## 安装依赖

```bash
pip install mysql-connector-python
# 或
pip install pymysql
```

## 基础连接

```python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="mydb",
    charset="utf8mb4"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")

for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
```

## 使用上下文管理器

```python
from contextlib import contextmanager
import mysql.connector

@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="mydb"
    )
    try:
        yield conn
    finally:
        conn.close()

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
```

## 参数化查询（防止 SQL 注入）

```python
# 错误：字符串拼接（易受 SQL 注入攻击）
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

# 正确：参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

## 事务处理

```python
try:
    conn.start_transaction()
    cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
```

## 科研实战场景

### 1. 存储实验配置

```python
def save_experiment_config(config: dict, experiment_name: str):
    """保存实验配置到数据库"""
    import mysql.connector
    import json

    conn = mysql.connector.connect(
        host="localhost", user="root",
        password="password", database="experiments"
    )
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO experiments
           (name, config_json, created_at)
           VALUES (%s, %s, NOW())""",
        (experiment_name, json.dumps(config, ensure_ascii=False))
    )
    experiment_id = cursor.lastrowid
    conn.commit()

    cursor.close()
    conn.close()
    return experiment_id
```

### 2. 记录训练指标

```python
def log_metrics(experiment_id: int, epoch: int, metrics: dict):
    """记录训练指标"""
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost", user="root",
        password="password", database="experiments"
    )
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO training_metrics
           (experiment_id, epoch, loss, accuracy, timestamp)
           VALUES (%s, %s, %s, %s, NOW())""",
        (experiment_id, epoch, metrics.get('loss'), metrics.get('accuracy'))
    )
    conn.commit()
    cursor.close()
    conn.close()
```

### 3. 批量插入数据

```python
def batch_insert_samples(data_list: list):
    """批量插入样本数据"""
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost", user="root",
        password="password", database="datasets"
    )
    cursor = conn.cursor()

    # executemany 比循环 execute 快得多
    cursor.executemany(
        "INSERT INTO samples (text, label, source) VALUES (%s, %s, %s)",
        data_list
    )
    conn.commit()
    cursor.close()
    conn.close()
```

### 4. 使用连接池

```python
from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    user="root",
    password="password",
    database="mydb"
)

# 从池中获取连接
conn = connection_pool.get_connection()
```

## ORM 方案：SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))

engine = create_engine("mysql+pymysql://root:password@localhost/mydb")
Session = sessionmaker(bind=engine)
session = Session()

# 查询
users = session.query(User).filter(User.name.like("%张%")).all()
```

## 易错点

### 1. 连接未关闭

```python
# 错误
conn = mysql.connector.connect(...)
cursor = conn.cursor()
cursor.execute("...")
# 忘记关闭

# 正确
try:
    conn = mysql.connector.connect(...)
    cursor = conn.cursor()
    cursor.execute("...")
finally:
    cursor.close()
    conn.close()
```

### 2. 字符集问题

```python
# 指定 utf8mb4 支持 emoji
conn = mysql.connector.connect(..., charset="utf8mb4")
```

## 性能提示

> **批量操作**：
> - `executemany` 比循环 `execute` 快 10-100 倍
> - 大量数据使用 `LOAD DATA INFILE`

> **连接管理**：
> - 使用连接池减少连接开销
> - 长连接优于频繁创建/销毁
