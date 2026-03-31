# Python 学习指南（从 Java 开发者视角出发）

> 本指南帮助 Java 开发者快速掌握 Python，聚焦于工程化实践

---

## 一、Python vs Java 生态对照表

| 领域 | Java 技术 | Python 替代方案 | 推荐理由 |
|------|-----------|-----------------|----------|
| **Web框架** | Spring Boot | **FastAPI** > Django > Flask | FastAPI 性能强、类型提示、自动文档 |
| **ORM** | MyBatis/JPA | **SQLAlchemy** > Django ORM | SQLAlchemy 灵活强大，最接近 MyBatis |
| **日志** | Log4j/SLF4J | **loguru** > logging | loguru 开箱即用，一行搞定 |
| **包管理** | Maven/Gradle | **Poetry** > pip + venv | Poetry 类似 Maven，依赖锁定 |
| **代码规范** | 阿里规范 | **PEP 8** + Black + Ruff | 官方规范 + 自动格式化 |
| **类型检查** | 无（编译时） | **mypy** + type hints | 静态类型检查，类似 Java |
| **测试** | JUnit | **pytest** | 更简洁的断言语法 |
| **配置管理** | application.yml | **pydantic-settings** | 类型安全的配置 |

---

## 二、Python 知识体系

```
Python 知识体系
├── 1. 基础语法
│   ├── 变量与数据类型
│   ├── 流程控制
│   ├── 函数
│   ├── 模块与包
│   └── 文件操作
│
├── 2. 进阶特性
│   ├── 列表推导式 / 字典推导式
│   ├── 生成器 与 迭代器
│   ├── 装饰器
│   ├── 上下文管理器
│   └── 异步编程
│
├── 3. OOP 面向对象
│   ├── 类与对象
│   ├── 继承与多态
│   ├── 魔术方法 (__init__, __str__, __repr__)
│   ├── 属性装饰器 (@property)
│   └── 数据类 (dataclass)
│
├── 4. 工程化工具链
│   ├── 包管理：Poetry
│   ├── 虚拟环境：venv / conda
│   ├── 代码格式化：Black + Ruff
│   ├── 类型检查：mypy
│   └── 测试框架：pytest
│
└── 5. Web 开发生态
    ├── Web框架：FastAPI
    ├── ORM：SQLAlchemy
    ├── 数据验证：Pydantic
    ├── 日志：loguru
    └── 数据库迁移：Alembic
```

---

## 三、Python 与 Java 详细对比

### 3.1 Spring Boot → FastAPI

```python
# Java Spring Boot
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
}

# Python FastAPI
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/api/users/{user_id}")
async def get_user(user_id: int) -> User:
    return await user_service.find_by_id(user_id)
```

**FastAPI 优势：**
- 自动生成 OpenAPI 文档（Swagger UI）
- 类型提示自动校验请求参数
- 异步支持，性能接近 Go
- 依赖注入系统

### 3.2 MyBatis → SQLAlchemy

```python
# Java MyBatis
@Select("SELECT * FROM users WHERE id = #{id}")
User findById(@Param("id") Long id);

# Python SQLAlchemy 2.0（最新写法）
from sqlalchemy import select
from sqlalchemy.orm import Session

async def find_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# 实体定义（类似 JPA）
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
```

### 3.3 SLF4J/Log4j → loguru

```python
# Java
private static final Logger log = LoggerFactory.getLogger(UserService.class);
log.info("User {} logged in", userId);

# Python loguru（推荐）
from loguru import logger

logger.info("User {} logged in", user_id)
logger.error("Failed to connect: {}", error)

# 一行配置即可
logger.add("app.log", rotation="10 MB", retention="7 days")
```

### 3.4 Maven → Poetry

```bash
# Java Maven
mvn init
mvn add dependency spring-boot-starter-web
mvn package

# Python Poetry（完全对标 Maven）
poetry init                    # 初始化项目
poetry add fastapi sqlalchemy  # 添加依赖
poetry add pytest --group dev  # 添加开发依赖
poetry install                 # 安装所有依赖
poetry build                   # 打包
```

**pyproject.toml（类似 pom.xml）：**

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "My Python Project"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
sqlalchemy = "^2.0"
pydantic = "^2.5"
loguru = "^0.7"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
black = "^24.1"
mypy = "^1.8"
ruff = "^0.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 3.5 阿里规范 → PEP 8 + Black + Ruff

```python
# 命名规范对照
# Java                    # Python
UserService              user_service        # 类名用大驼峰，其他用蛇形
MAX_RETRY_COUNT          MAX_RETRY_COUNT     # 常量都一样
getUserById()            get_user_by_id()    # 方法名蛇形
private String userName  user_name: str      # 变量蛇形

# 工具链
# 1. Black - 自动格式化（不用纠结格式）
# 2. Ruff - Linter（替代 flake8, isort, pylint）
# 3. mypy - 类型检查

# pyproject.toml 配置
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

---

## 四、Python OOP 核心要点

### 4.1 类定义对比

```python
# Java
public class User {
    private Long id;
    private String name;
    
    public User(Long id, String name) {
        this.id = id;
        this.name = name;
    }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}

# Python（传统写法）
class User:
    def __init__(self, id: int, name: str):
        self._id = id
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value

# Python（推荐写法 - dataclass）
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str = ""  # 默认值
    
    def __post_init__(self):
        # 初始化后逻辑
        pass

# Python（最强写法 - Pydantic，用于 API）
from pydantic import BaseModel, EmailStr, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: EmailStr  # 自动校验邮箱格式
```

### 4.2 继承与多态

```python
# Java
public abstract class Animal {
    public abstract void speak();
}
public class Dog extends Animal {
    @Override
    public void speak() { System.out.println("Woof"); }
}

# Python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

# 多态（鸭子类型）
def make_sound(animal: Animal) -> None:
    print(animal.speak())  # 任何有 speak() 方法的对象都行
```

### 4.3 魔术方法（类似 Java 的 toString/equals）

```python
class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __str__(self) -> str:
        """类似 Java toString()"""
        return f"User(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """开发者友好表示"""
        return f"User({self.id!r}, {self.name!r})"

    def __eq__(self, other: object) -> bool:
        """类似 Java equals()"""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """配合 __eq__ 使用，可放入 set/dict"""
        return hash(self.id)
```

#### 常用魔术方法速查表

| 分类 | 魔术方法 | 说明 | Java 对应 | 使用场景 |
|------|----------|------|-----------|----------|
| **对象表示** | `__str__` | 用户友好的字符串表示 | `toString()` | `print(obj)` 时调用 |
| | `__repr__` | 开发者友好的字符串表示 | `toString()` | 调试、日志时调用 |
| | `__format__` | 自定义格式化 | `String.format()` | `f"{obj:spec}"` |
| **比较运算** | `__eq__` | 相等比较 | `equals()` | `obj1 == obj2` |
| | `__ne__` | 不相等比较 | `!equals()` | `obj1 != obj2` |
| | `__lt__` | 小于 | `compareTo() < 0` | `obj1 < obj2` |
| | `__le__` | 小于等于 | `compareTo() <= 0` | `obj1 <= obj2` |
| | `__gt__` | 大于 | `compareTo() > 0` | `obj1 > obj2` |
| | `__ge__` | 大于等于 | `compareTo() >= 0` | `obj1 >= obj2` |
| | `__hash__` | 哈希值 | `hashCode()` | 作为 dict key 或 set 元素 |
| **算术运算** | `__add__` | 加法 | 无 | `obj + other` |
| | `__sub__` | 减法 | 无 | `obj - other` |
| | `__mul__` | 乘法 | 无 | `obj * other` |
| | `__truediv__` | 除法 | 无 | `obj / other` |
| | `__floordiv__` | 整除 | 无 | `obj // other` |
| | `__mod__` | 取模 | 无 | `obj % other` |
| | `__pow__` | 幂运算 | 无 | `obj ** other` |
| **位运算** | `__and__` | 按位与 | 无 | `obj & other` |
| | `__or__` | 按位或 | 无 | `obj \| other` |
| | `__xor__` | 按位异或 | 无 | `obj ^ other` |
| | `__invert__` | 按位取反 | 无 | `~obj` |
| **容器协议** | `__len__` | 长度 | `size()` | `len(obj)` |
| | `__getitem__` | 获取元素 | `get(index)` | `obj[key]` |
| | `__setitem__` | 设置元素 | `set(index, val)` | `obj[key] = value` |
| | `__delitem__` | 删除元素 | `remove(index)` | `del obj[key]` |
| | `__contains__` | 包含判断 | `contains()` | `item in obj` |
| | `__iter__` | 迭代器 | `iterator()` | `for item in obj` |
| | `__reversed__` | 反转 | `Collections.reverse()` | `reversed(obj)` |
| **属性访问** | `__getattr__` | 属性不存在时调用 | 无 | 动态属性 |
| | `__setattr__` | 设置属性时调用 | 无 | 属性拦截/验证 |
| | `__delattr__` | 删除属性时调用 | 无 | `del obj.attr` |
| | `__getattribute__` | 所有属性访问 | 无 | 拦截所有属性访问 |
| **可调用** | `__call__` | 使对象可调用 | 无 | `obj(*args)` |
| **上下文管理** | `__enter__` | 进入上下文 | `try-with-resources` | `with obj:` |
| | `__exit__` | 退出上下文 | `try-with-resources` | `with obj:` |
| **类型转换** | `__bool__` | 布尔转换 | 无 | `bool(obj)`, `if obj:` |
| | `__int__` | 整数转换 | 无 | `int(obj)` |
| | `__float__` | 浮点转换 | 无 | `float(obj)` |
| | `__str__` | 字符串转换 | `toString()` | `str(obj)` |
| | `__bytes__` | 字节转换 | `getBytes()` | `bytes(obj)` |
| **序列化** | `__getstate__` | pickle 序列化 | `Serializable` | 自定义序列化 |
| | `__setstate__` | pickle 反序列化 | `Serializable` | 自定义反序列化 |
| **描述符** | `__get__` | 获取属性值 | 无 | 属性代理 |
| | `__set__` | 设置属性值 | 无 | 属性验证 |
| | `__delete__` | 删除属性 | 无 | 属性清理 |
| **类创建** | `__new__` | 创建实例 | 构造函数第一部分 | 单例模式、不可变类型 |
| | `__init__` | 初始化实例 | 构造函数 | 初始化属性 |
| | `__del__` | 析构（不推荐依赖） | `finalize()` | 资源清理 |
| | `__init_subclass__` | 子类创建时调用 | 无 | 注册子类、验证子类 |
| **异步** | `__aiter__` | 异步迭代器 | 无 | `async for item in obj` |
| | `__anext__` | 异步下一个元素 | 无 | `async for` |
| | `__aenter__` | 异步上下文进入 | 无 | `async with obj:` |
| | `__aexit__` | 异步上下文退出 | 无 | `async with obj:` |

#### 常用魔术方法示例

```python
from functools import total_ordering

@total_ordering  # 只需定义 __eq__ 和一个比较方法，自动生成其他
class Money:
    """金额类 - 演示常用魔术方法"""

    def __init__(self, amount: float, currency: str = "CNY"):
        self.amount = amount
        self.currency = currency

    # === 对象表示 ===
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    # === 比较运算 ===
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    # === 算术运算 ===
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: float) -> "Money":  # 支持 factor * obj
        return self.__mul__(factor)

    # === 类型转换 ===
    def __float__(self) -> float:
        return self.amount

    def __bool__(self) -> bool:
        return self.amount > 0

    # === 容器协议 ===
    def __len__(self) -> int:
        """金额的整数部分位数"""
        return len(str(int(self.amount)))

# 使用示例
m1 = Money(100.50)
m2 = Money(50.25)

print(m1)              # 100.50 CNY (调用 __str__)
print(repr(m1))        # Money(100.5, 'CNY') (调用 __repr__)
print(m1 + m2)         # 150.75 CNY (调用 __add__)
print(m1 > m2)         # True (调用 __gt__，由 @total_ordering 自动生成)
print(m1 * 2)          # 201.00 CNY (调用 __mul__)
print(2 * m1)          # 201.00 CNY (调用 __rmul__)
print(float(m1))       # 100.5 (调用 __float__)
print(bool(Money(0)))  # False (调用 __bool__)
```

```python
# === 上下文管理器示例 ===
class Timer:
    """计时器 - 演示上下文管理"""

    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"耗时: {self.elapsed:.4f} 秒")
        return False  # 不抑制异常

# 使用
with Timer() as t:
    # 执行一些操作
    sum(range(1000000))
# 输出: 耗时: 0.0234 秒
```

```python
# === 可调用对象示例 ===
class Multiplier:
    """乘法器 - 演示 __call__"""

    def __init__(self, factor: float):
        self.factor = factor

    def __call__(self, value: float) -> float:
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
```

```python
# === 容器协议示例 ===
class Deck:
    """扑克牌组 - 演示容器协议"""

    suits = "♠♥♦♣"
    ranks = "A23456789TJQK"

    def __init__(self):
        self.cards = [r + s for s in self.suits for r in self.ranks]

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, index: int) -> str:
        return self.cards[index]

    def __contains__(self, card: str) -> bool:
        return card in self.cards

    def __iter__(self):
        return iter(self.cards)

deck = Deck()
print(len(deck))        # 52
print(deck[0])          # A♠
print("A♠" in deck)     # True
for card in deck[:5]:   # 支持切片
    print(card)
```

---

## 五、Python 如何定义接口

Python 中没有 Interface 关键字，但可以通过 **抽象基类（ABC）** 实现接口定义。

### 5.1 基础接口定义

```python
from abc import ABC, abstractmethod
from typing import Protocol

# 方式1：抽象基类（推荐，类似 Java 接口）
class UserRepository(ABC):
    """用户仓储接口"""
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> "User | None":
        """根据ID查询用户"""
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> "User | None":
        """根据用户名查询用户"""
        pass
    
    @abstractmethod
    def save(self, user: "User") -> "User":
        """保存用户"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        pass

# 方式2：Protocol（静态类型检查友好，Python 3.8+）
class Repository(Protocol):
    """泛型仓储协议"""
    
    def find_by_id(self, id: int) -> object | None: ...
    def save(self, entity: object) -> object: ...
    def delete(self, id: int) -> bool: ...
```

### 5.2 接口实现

```python
# 实现类（类似 implements）
class UserRepositoryImpl(UserRepository):
    """用户仓储实现类"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def find_by_id(self, user_id: int) -> User | None:
        # 实际数据库查询逻辑
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def find_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        user = self.find_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
```

### 5.3 依赖注入（类似 Spring）

```python
from fastapi import Depends

# 定义服务（需要依赖仓储接口）
class UserService:
    def __init__(self, user_repo: UserRepository):  # 注入接口
        self.user_repo = user_repo
    
    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.find_by_id(user_id)

# FastAPI 路由中使用
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(lambda: UserService(UserRepositoryImpl(db)))
) -> UserResponse:
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
```

### 5.4 泛型接口

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """泛型基础仓储接口"""
    
    @abstractmethod
    def find_by_id(self, id: int) -> T | None:
        pass
    
    @abstractmethod
    def find_all(self) -> list[T]:
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        pass

# 具体实现
class UserRepository(BaseRepository[User]):
    def find_by_id(self, id: int) -> User | None:
        # ...
        pass
    
    def find_all(self) -> list[User]:
        # ...
        pass
    
    def save(self, entity: User) -> User:
        # ...
        pass
```

---

## 六、实操路线图

### 6.1 环境搭建（第一天）

```bash
# 1. 安装 Python 3.11+（推荐 pyenv 管理版本）
# Windows: https://www.python.org/downloads/
# Mac/Linux:
curl https://pyenv.run | bash
pyenv install 3.12

# 2. 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 3. 创建项目
mkdir my-python-project
cd my-python-project
poetry init

# 4. 安装核心依赖
poetry add fastapi uvicorn sqlalchemy pydantic loguru
poetry add --group dev pytest black ruff mypy
```

### 6.2 项目结构（对标 Spring Boot）

```
my-python-project/
├── pyproject.toml          # 类似 pom.xml
├── poetry.lock             # 类似 Maven 锁定文件
├── .python-version         # 指定 Python 版本
├── README.md
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── main.py         # 入口文件
│       ├── config.py       # 配置类
│       ├── api/            # 路由层（Controller）
│       │   ├── __init__.py
│       │   ├── users.py
│       │   └── products.py
│       ├── services/       # 业务层
│       │   └── user_service.py
│       ├── models/         # 数据模型
│       │   ├── user.py     # SQLAlchemy 实体
│       │   └── schemas.py  # Pydantic DTOs
│       ├── repositories/   # 数据访问层
│       │   └── user_repo.py
│       └── core/           # 公共模块
│           ├── database.py
│           ├── security.py
│           └── exceptions.py
└── tests/
    ├── __init__.py
    └── test_users.py
```

### 6.3 从零到一：实现一个 RESTful API

**步骤1：定义模型**

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**步骤2：定义 Schema（DTO）**

```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    created_at: datetime
```

**步骤3：定义 Repository（数据访问层）**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

**步骤4：定义 Service（业务层）**

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def get_user(self, user_id: int) -> User | None:
        return await self.user_repo.find_by_id(user_id)
    
    async def create_user(self, user_data: UserCreate) -> User:
        # 业务逻辑：检查用户名是否存在
        existing = await self.user_repo.find_by_username(user_data.username)
        if existing:
            raise ValueError("Username already exists")
        
        # 创建用户（密码应该哈希处理）
        return await self.user_repo.create(user_data.model_dump())
```

**步骤5：定义路由（Controller）**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["用户管理"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**步骤6：主入口**

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时：清理资源
    await engine.dispose()

app = FastAPI(
    title="用户管理系统",
    version="1.0.0",
    description="基于 FastAPI + SQLAlchemy 的 RESTful API",
    lifespan=lifespan
)

app.include_router(users.router)

# 自动生成的 Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**步骤7：运行**

```bash
# 开发模式
poetry run uvicorn src.my_app.main:app --reload --port 8000

# 访问自动生成的 Swagger UI
# http://localhost:8000/docs
```

---

## 七、依赖管理方案

### 7.1 现代化方案：Poetry（推荐）

```bash
# 初始化项目
poetry init

# 添加依赖
poetry add fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings loguru
poetry add python-jose[cryptography] passlib[bcrypt]

# 添加开发依赖
poetry add --group dev pytest pytest-asyncio httpx black ruff mypy

# 安装所有依赖
poetry install

# 导出 requirements.txt（兼容其他工具）
poetry export -f requirements.txt --output requirements.txt
poetry export -f requirements.txt --with dev --output requirements-dev.txt
```

### 7.2 兼容方案：requirements.txt

如果需要 requirements.txt（兼容 Docker、CI/CD 等）：

```txt
# requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
loguru>=0.7.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

```txt
# requirements-dev.txt（开发环境额外依赖）
-r requirements.txt
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
black>=24.1.0
ruff>=0.2.0
mypy>=1.8.0
```

### 7.3 使用 uv（更快的新选择）

```bash
# 安装 uv（Rust 编写，比 pip 快 10-100 倍）
pip install uv

# 创建项目
uv init my-project
cd my-project

# 添加依赖
uv add fastapi sqlalchemy pydantic
uv add --dev pytest black ruff

# 运行
uv run uvicorn main:app --reload
```

---

## 八、学习资源推荐

### 8.1 官方文档（首选）

| 资源 | 链接 |
|------|------|
| Python 官方教程 | https://docs.python.org/zh-cn/3/tutorial/ |
| FastAPI 文档 | https://fastapi.tiangolo.com/zh/ |
| SQLAlchemy 2.0 | https://docs.sqlalchemy.org/en/20/ |
| Pydantic | https://docs.pydantic.dev/ |
| Poetry 文档 | https://python-poetry.org/docs/ |

### 8.2 学习路径

```
Week 1: Python 基础语法 + 类型提示
Week 2: OOP + dataclass + Pydantic
Week 3: FastAPI 构建 RESTful API
Week 4: SQLAlchemy + Alembic 数据库操作
Week 5: 项目实战：重构你的 Java 项目为 Python 版本
```

### 8.3 最佳实践 Checklist

```
- [ ] 使用 Python 3.11+（类型提示更完善）
- [ ] 使用 Poetry 管理依赖
- [ ] 使用 Black + Ruff 格式化和检查代码
- [ ] 使用 mypy 进行静态类型检查
- [ ] 使用 pytest 写测试
- [ ] 使用 loguru 记录日志
- [ ] 所有函数都加类型提示
```

---

## 九、常用 API 速查表（Java 开发者必备）

### 9.1 字符串操作

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `str.length()` | `len(s)` | 长度 | `len("hello") # 5` |
| `str.isEmpty()` | `not s` 或 `len(s) == 0` | 是否为空 | `if not s:` |
| `str.isBlank()` | `not s.strip()` | 是否为空白 | `if not s.strip():` |
| `str.charAt(i)` | `s[i]` | 获取字符 | `"hello"[0] # 'h'` |
| `str.substring(1, 3)` | `s[1:3]` | 子字符串 | `"hello"[1:3] # "el"` |
| `str.substring(2)` | `s[2:]` | 从索引截取 | `"hello"[2:] # "llo"` |
| `str.indexOf("el")` | `s.find("el")` | 查找子串位置 | `"hello".find("el") # 1` |
| `str.lastIndexOf("l")` | `s.rfind("l")` | 从后查找 | `"hello".rfind("l") # 3` |
| `str.contains("el")` | `"el" in s` | 是否包含 | `"el" in "hello" # True` |
| `str.startsWith("he")` | `s.startswith("he")` | 是否以...开头 | `"hello".startswith("he")` |
| `str.endsWith("lo")` | `s.endswith("lo")` | 是否以...结尾 | `"hello".endswith("lo")` |
| `str.toUpperCase()` | `s.upper()` | 转大写 | `"Hello".upper() # "HELLO"` |
| `str.toLowerCase()` | `s.lower()` | 转小写 | `"Hello".lower() # "hello"` |
| `str.trim()` | `s.strip()` | 去除两端空白 | `" hi ".strip() # "hi"` |
| `str.strip()` (Java 11) | `s.strip()` | 去除空白 | 同上 |
| `str.replace("a", "b")` | `s.replace("a", "b")` | 替换 | `"aaa".replace("a", "b")` |
| `str.replaceAll("\\d+", "x")` | `re.sub(r"\d+", "x", s)` | 正则替换 | `import re` |
| `str.split(",")` | `s.split(",")` | 分割 | `"a,b,c".split(",")` |
| `String.join(",", list)` | `",".join(list)` | 连接 | `",".join(["a","b"]) # "a,b"` |
| `str.concat(other)` | `s + other` 或 `s + other` | 拼接 | `"a" + "b" # "ab"` |
| `str.repeat(3)` | `s * 3` | 重复 | `"ab" * 3 # "ababab"` |
| `str.equals(other)` | `s == other` | 字符串比较 | `s1 == s2` |
| `str.equalsIgnoreCase(other)` | `s.lower() == other.lower()` | 忽略大小写比较 | - |
| `str.compareTo(other)` | `(s > other) - (s < other)` | 字典序比较 | - |
| `String.format("%s=%d", k, v)` | `f"{k}={v}"` 或 `"%s=%d" % (k, v)` | 格式化 | `f"name={name}"` |
| `str.stripIndent()` | `textwrap.dedent(s)` | 去除缩进 | `import textwrap` |
| `str.translate()` | `s.translate(table)` | 字符映射 | `str.maketrans()` |
| `" ".isBlank()` | `" ".isspace()` | 是否空白字符 | `" ".isspace() # True` |
| `str.chars()` | `iter(s)` 或 `[c for c in s]` | 字符迭代 | `for c in "hello":` |

```python
# Python 字符串常用操作示例
s = "  Hello, World!  "

# 基本操作
print(s.strip())           # "Hello, World!" - 去除两端空白
print(s.lower())           # "  hello, world!  "
print(s.upper())           # "  HELLO, WORLD!  "
print(s.replace("World", "Python"))  # "  Hello, Python!  "

# 查找与判断
print(s.find("World"))     # 9 - 找到返回索引
print(s.find("xyz"))       # -1 - 未找到
print("World" in s)        # True - 包含判断
print(s.startswith("  H")) # True
print(s.endswith("!  "))   # True

# 分割与连接
parts = "a,b,c".split(",")  # ["a", "b", "c"]
joined = "-".join(parts)    # "a-b-c"

# 格式化（推荐 f-string）
name, age = "张三", 25
print(f"姓名: {name}, 年龄: {age}")
print(f"价格: {99.9:.2f}")   # "价格: 99.90"
print(f"百分比: {0.856:.1%}") # "百分比: 85.6%"

# 多行字符串
multiline = """
第一行
第二行
"""
print(multiline.strip())  # 去除首尾空白
```

### 9.2 集合操作

#### List（列表）→ Python list

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `new ArrayList<>()` | `[]` 或 `list()` | 创建空列表 | `items = []` |
| `Arrays.asList(1,2,3)` | `[1, 2, 3]` | 创建列表 | `items = [1, 2, 3]` |
| `list.add(item)` | `items.append(item)` | 添加元素 | `items.append(4)` |
| `list.add(0, item)` | `items.insert(0, item)` | 插入元素 | `items.insert(0, 0)` |
| `list.addAll(other)` | `items.extend(other)` | 扩展列表 | `items.extend([4,5])` |
| `list.get(i)` | `items[i]` | 获取元素 | `items[0]` |
| `list.set(i, val)` | `items[i] = val` | 设置元素 | `items[0] = 10` |
| `list.remove(i)` | `items.pop(i)` 或 `del items[i]` | 按索引删除 | `items.pop(0)` |
| `list.remove(obj)` | `items.remove(obj)` | 按值删除（首个） | `items.remove(3)` |
| `list.contains(obj)` | `obj in items` | 是否包含 | `3 in items` |
| `list.indexOf(obj)` | `items.index(obj)` | 查找索引 | `items.index(3)` |
| `list.size()` | `len(items)` | 长度 | `len(items)` |
| `list.isEmpty()` | `not items` 或 `len(items) == 0` | 是否为空 | `if not items:` |
| `list.clear()` | `items.clear()` | 清空 | `items.clear()` |
| `list.sort()` | `items.sort()` 或 `sorted(items)` | 排序 | `items.sort()` |
| `list.sort(Comparator.reverseOrder())` | `items.sort(reverse=True)` | 降序排序 | `items.sort(reverse=True)` |
| `Collections.reverse(list)` | `items.reverse()` | 反转 | `items.reverse()` |
| `Collections.max(list)` | `max(items)` | 最大值 | `max(items)` |
| `Collections.min(list)` | `min(items)` | 最小值 | `min(items)` |
| `list.subList(1, 3)` | `items[1:3]` | 子列表 | `items[1:3]` |
| `list.toArray()` | `tuple(items)` | 转数组/元组 | `tuple(items)` |
| `new ArrayList<>(list)` | `items.copy()` 或 `items[:]` | 复制 | `copy = items[:]` |
| `list.stream().filter(...)` | `[x for x in items if ...]` | 过滤 | `[x for x in items if x > 0]` |
| `list.stream().map(...)` | `[f(x) for x in items]` | 映射 | `[x*2 for x in items]` |
| `list.stream().findFirst()` | `next((x for x in items if ...), None)` | 查找第一个 | `next((x for x in items if x > 0), None)` |

```python
# Python 列表常用操作
items = [3, 1, 4, 1, 5, 9, 2, 6]

# 增删改查
items.append(7)           # 末尾添加
items.insert(0, 0)        # 指定位置插入
items.pop()               # 删除并返回最后一个
items.pop(0)              # 删除并返回第一个
items.remove(1)           # 删除第一个值为1的元素

# 切片（Python 特色）
print(items[1:4])         # 索引1到3
print(items[:3])          # 前三个
print(items[-3:])         # 后三个
print(items[::2])         # 每隔一个取一个
print(items[::-1])        # 反转

# 列表推导式（类似 Java Stream）
squares = [x**2 for x in range(10)]
evens = [x for x in items if x % 2 == 0]
matrix = [[i*3+j for j in range(3)] for i in range(3)]

# 常用操作
items.sort()              # 原地排序
sorted_items = sorted(items)  # 返回新列表
items.reverse()           # 原地反转
reversed_items = list(reversed(items))  # 返回新列表

# 统计
print(sum(items))         # 求和
print(max(items))         # 最大值
print(min(items))         # 最小值
print(items.count(1))     # 统计出现次数
```

#### Set（集合）→ Python set

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `new HashSet<>()` | `set()` 或 `{}` | 创建空集合 | `s = set()` |
| `Set.of(1,2,3)` | `{1, 2, 3}` | 创建集合 | `s = {1, 2, 3}` |
| `set.add(e)` | `s.add(e)` | 添加元素 | `s.add(4)` |
| `set.remove(e)` | `s.remove(e)` 或 `s.discard(e)` | 删除元素 | `s.discard(1)` |
| `set.contains(e)` | `e in s` | 是否包含 | `1 in s` |
| `set.size()` | `len(s)` | 大小 | `len(s)` |
| `set.isEmpty()` | `not s` | 是否为空 | `if not s:` |
| `set.clear()` | `s.clear()` | 清空 | `s.clear()` |
| `set1.addAll(set2)` | `s1.update(s2)` | 并集更新 | `s1.update(s2)` |
| `set1.retainAll(set2)` | `s1.intersection_update(s2)` | 交集更新 | `s1 &= s2` |
| `set1.removeAll(set2)` | `s1.difference_update(s2)` | 差集更新 | `s1 -= s2` |
| 并集 | `s1 \| s2` 或 `s1.union(s2)` | 并集 | `{1,2} \| {2,3} # {1,2,3}` |
| 交集 | `s1 & s2` 或 `s1.intersection(s2)` | 交集 | `{1,2} & {2,3} # {2}` |
| 差集 | `s1 - s2` 或 `s1.difference(s2)` | 差集 | `{1,2} - {2,3} # {1}` |
| 对称差 | `s1 ^ s2` 或 `s1.symmetric_difference(s2)` | 对称差 | `{1,2} ^ {2,3} # {1,3}` |
| 子集判断 | `s1 <= s2` 或 `s1.issubset(s2)` | 子集 | `{1} <= {1,2} # True` |
| 超集判断 | `s1 >= s2` 或 `s1.issuperset(s2)` | 超集 | `{1,2} >= {1} # True` |

```python
# Python 集合操作
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# 集合运算
print(a | b)      # {1, 2, 3, 4, 5, 6} - 并集
print(a & b)      # {3, 4} - 交集
print(a - b)      # {1, 2} - 差集
print(a ^ b)      # {1, 2, 5, 6} - 对称差

# 去重（常见用法）
items = [1, 2, 2, 3, 3, 3]
unique = list(set(items))  # [1, 2, 3]

# 判断子集/超集
print({1, 2}.issubset(a))        # True
print(a.issuperset({1, 2}))      # True
```

#### Map（映射）→ Python dict

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `new HashMap<>()` | `{}` 或 `dict()` | 创建空字典 | `d = {}` |
| `Map.of("k1", 1, "k2", 2)` | `{"k1": 1, "k2": 2}` | 创建字典 | `d = {"a": 1}` |
| `map.put("key", value)` | `d["key"] = value` | 添加/更新 | `d["a"] = 1` |
| `map.get("key")` | `d["key"]` 或 `d.get("key")` | 获取值 | `d.get("a", 0)` |
| `map.getOrDefault("k", default)` | `d.get("k", default)` | 获取或默认 | `d.get("x", 0)` |
| `map.containsKey("key")` | `"key" in d` | 是否包含键 | `"a" in d` |
| `map.containsValue(v)` | `v in d.values()` | 是否包含值 | `1 in d.values()` |
| `map.remove("key")` | `d.pop("key")` 或 `del d["key"]` | 删除 | `d.pop("a")` |
| `map.remove("key", default)` | `d.pop("key", default)` | 删除或默认 | `d.pop("x", None)` |
| `map.size()` | `len(d)` | 大小 | `len(d)` |
| `map.isEmpty()` | `not d` | 是否为空 | `if not d:` |
| `map.clear()` | `d.clear()` | 清空 | `d.clear()` |
| `map.keySet()` | `d.keys()` | 所有键 | `list(d.keys())` |
| `map.values()` | `d.values()` | 所有值 | `list(d.values())` |
| `map.entrySet()` | `d.items()` | 所有键值对 | `list(d.items())` |
| `map.forEach((k,v) -> ...)` | `for k, v in d.items():` | 遍历 | 见示例 |
| `map.putIfAbsent(k, v)` | `d.setdefault(k, v)` | 不存在则添加 | `d.setdefault("a", 0)` |
| `map.computeIfAbsent(k, f)` | `d.setdefault(k, f())` | 计算并添加 | `d.setdefault("a", lambda: [])` |
| `map.merge(k, v, remapFunc)` | 复杂，见 Counter | 合并 | `from collections import Counter` |
| `new HashMap<>(map)` | `d.copy()` | 浅拷贝 | `copy = d.copy()` |

```python
# Python 字典操作
user = {"name": "张三", "age": 25, "city": "北京"}

# 访问
print(user["name"])           # "张三" - 键不存在会报错
print(user.get("name"))       # "张三" - 推荐方式
print(user.get("email", "N/A"))  # "N/A" - 带默认值

# 添加/修改
user["email"] = "zhangsan@example.com"
user["age"] = 26  # 更新

# 删除
del user["city"]
email = user.pop("email")     # 删除并返回
user.pop("nonexistent", None)  # 不报错

# 遍历
for key in user:              # 遍历键
    print(key)

for key, value in user.items():  # 遍历键值对
    print(f"{key}: {value}")

for value in user.values():   # 遍历值
    print(value)

# 字典推导式
scores = {"a": 90, "b": 85, "c": 95}
passed = {k: v for k, v in scores.items() if v >= 90}

# 合并字典 (Python 3.9+)
defaults = {"a": 1, "b": 2}
overrides = {"b": 3, "c": 4}
merged = defaults | overrides  # {"a": 1, "b": 3, "c": 4}

# 或使用 update
result = defaults.copy()
result.update(overrides)
```

### 9.3 迭代方式与推导式（Python 核心特性）

Python 的迭代和推导式是极其强大的特性，可以替代 Java 中大部分 Stream API 操作。

#### 9.3.1 迭代方式对照表

| Java | Python | 说明 |
|------|--------|------|
| `for (int i = 0; i < n; i++)` | `for i in range(n):` | 基础循环 |
| `for (int i = start; i < end; i += step)` | `for i in range(start, end, step):` | 带步长循环 |
| `for (String s : list)` | `for s in items:` | 增强for循环 |
| `for (int i = 0; i < list.size(); i++)` | `for i, item in enumerate(items):` | 带索引遍历 |
| `list.stream().forEach(System.out::println)` | `for item in items: print(item)` | 遍历 |
| `IntStream.range(0, 10).forEach(i -> ...)` | `for i in range(10):` | 范围遍历 |
| `IntStream.rangeClosed(1, 10)` | `range(1, 11)` | 闭区间 |
| `map.forEach((k, v) -> ...)` | `for k, v in d.items():` | Map遍历 |
| `for (int i = list.size() - 1; i >= 0; i--)` | `for item in reversed(items):` | 反向遍历 |
| `iterator.next()` | `next(iter(obj))` | 获取下一个元素 |
| `iterator.hasNext()` | 循环或捕获 StopIteration | 是否有下一个 |
| `list.listIterator()` | `enumerate(items)` | 双向迭代（索引） |

```python
# === 基础迭代 ===
# 遍历范围
for i in range(10):          # 0-9
for i in range(1, 11):       # 1-10
for i in range(0, 10, 2):    # 0,2,4,6,8 (步长为2)
for i in range(10, 0, -1):   # 10,9,8...1 (倒序)

# 遍历列表
items = ["a", "b", "c"]
for item in items:
    print(item)

# 带索引遍历（类似 for i = 0; i < n; i++）
for i, item in enumerate(items):
    print(f"索引 {i}: {item}")

# 从指定索引开始
for i, item in enumerate(items, start=1):
    print(f"第 {i} 个: {item}")

# 反向遍历
for item in reversed(items):
    print(item)

# 同时遍历多个列表
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}: {age}岁")

# 遍历字典
user = {"name": "张三", "age": 25}
for key in user:                    # 遍历键
    print(key)
for key, value in user.items():     # 遍历键值对
    print(f"{key}: {value}")
for value in user.values():         # 遍历值
    print(value)

# 无限循环（需要 break）
import itertools
for i in itertools.count():         # 0, 1, 2, 3...
    if i > 10:
        break

# 循环多个迭代器
colors = ["red", "green", "blue"]
sizes = ["S", "M", "L"]
for color, size in itertools.product(colors, sizes):
    print(f"{color}-{size}")  # red-S, red-M, red-L, green-S...
```

#### 9.3.2 列表推导式（List Comprehension）

**替代 Java Stream 的 map/filter/collect**

| Java Stream | Python 列表推导式 | 说明 |
|-------------|-------------------|------|
| `list.stream().map(x -> x*2).collect(toList())` | `[x*2 for x in items]` | 映射 |
| `list.stream().filter(x -> x > 0).collect(toList())` | `[x for x in items if x > 0]` | 过滤 |
| `list.stream().map(...).filter(...).collect(toList())` | `[f(x) for x in items if cond]` | 组合 |
| `list.stream().flatMap(...).collect(toList())` | `[y for x in items for y in f(x)]` | 扁平化 |
| `IntStream.range(0, n).map(...).toArray()` | `[f(i) for i in range(n)]` | 范围映射 |
| `list.stream().distinct().collect(toList())` | `list(set(items))` | 去重 |
| `list.stream().limit(n).collect(toList())` | `items[:n]` 或 `[items[i] for i in range(n)]` | 限制数量 |
| `list.stream().sorted().collect(toList())` | `sorted(items)` | 排序 |

```python
# === 基础列表推导式 ===
numbers = [1, 2, 3, 4, 5]

# 映射（类似 map）
squares = [x**2 for x in numbers]
# [1, 4, 9, 16, 25]

# 过滤（类似 filter）
evens = [x for x in numbers if x % 2 == 0]
# [2, 4]

# 映射 + 过滤（类似 map + filter）
squared_evens = [x**2 for x in numbers if x % 2 == 0]
# [4, 16]

# 带条件表达式（三元运算符）
labels = ["偶数" if x % 2 == 0 else "奇数" for x in numbers]
# ["奇数", "偶数", "奇数", "偶数", "奇数"]

# 带索引
indexed = [(i, x) for i, x in enumerate(numbers)]
# [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]

# 嵌套循环（类似 flatMap）
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [x for row in matrix for x in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 嵌套循环 + 条件
evens_from_matrix = [x for row in matrix for x in row if x % 2 == 0]
# [2, 4, 6, 8]

# 生成坐标对
coords = [(x, y) for x in range(3) for y in range(3)]
# [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]

# 字符串处理
words = ["Hello", "World", "Python"]
lower_words = [w.lower() for w in words]           # 全小写
first_letters = [w[0] for w in words if w]         # 首字母
word_lengths = [len(w) for w in words]             # 长度列表

# 从字典生成列表
scores = {"Alice": 95, "Bob": 87, "Charlie": 92}
names = [name for name in scores]                          # 键列表
high_scorers = [name for name, score in scores.items() if score >= 90]
score_list = [(name, score) for name, score in scores.items()]

# 文件处理
# lines = [line.strip() for line in open("file.txt") if line.strip()]

# 调用方法
def process(x: int) -> int:
    return x * 2 + 1

results = [process(x) for x in range(5)]
# [1, 3, 5, 7, 9]

# 复杂表达式
from math import sqrt
primes = [x for x in range(2, 100) if all(x % i != 0 for i in range(2, int(sqrt(x)) + 1))]
```

#### 9.3.3 字典推导式（Dict Comprehension）

```python
# === 基础字典推导式 ===
names = ["Alice", "Bob", "Charlie"]

# 从列表创建字典
name_lengths = {name: len(name) for name in names}
# {"Alice": 5, "Bob": 3, "Charlie": 7}

# 带条件
long_names = {name: len(name) for name in names if len(name) > 3}
# {"Alice": 5, "Charlie": 7}

# 交换键值
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}

# 过滤字典
scores = {"Alice": 95, "Bob": 67, "Charlie": 82, "David": 45}
passed = {name: score for name, score in scores.items() if score >= 60}
# {"Alice": 95, "Bob": 67, "Charlie": 82}

# 转换值
prices = {"apple": "$1.2", "banana": "$0.5", "orange": "$0.8"}
numeric_prices = {k: float(v.replace("$", "")) for k, v in prices.items()}
# {"apple": 1.2, "banana": 0.5, "orange": 0.8}

# 从两个列表创建字典
keys = ["name", "age", "city"]
values = ["张三", 25, "北京"]
user = {k: v for k, v in zip(keys, values)}
# {"name": "张三", "age": 25, "city": "北京"}

# 带枚举
items = ["a", "b", "c"]
indexed = {i: v for i, v in enumerate(items)}
# {0: "a", 1: "b", 2: "c"}

# 分组（类似 SQL GROUP BY）
from collections import defaultdict

students = [
    {"name": "Alice", "class": "A", "score": 90},
    {"name": "Bob", "class": "B", "score": 85},
    {"name": "Charlie", "class": "A", "score": 92},
]

# 按班级分组
classes = defaultdict(list)
for s in students:
    classes[s["class"]].append(s["name"])
# {"A": ["Alice", "Charlie"], "B": ["Bob"]}
```

#### 9.3.4 集合推导式（Set Comprehension）

```python
# === 集合推导式 ===
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]

# 去重
unique = {x for x in numbers}
# {1, 2, 3, 4}

# 带条件
even_unique = {x for x in numbers if x % 2 == 0}
# {2, 4}

# 转换后去重
squared_unique = {x**2 for x in range(-5, 6)}
# {0, 1, 4, 9, 16, 25}

# 字符串去重
text = "hello world"
unique_chars = {c for c in text if c != " "}
# {'h', 'e', 'l', 'o', 'w', 'r', 'd'}

# 从多个列表创建集合
list1 = [1, 2, 3]
list2 = [3, 4, 5]
combined = {x for lst in [list1, list2] for x in lst}
# {1, 2, 3, 4, 5}
```

#### 9.3.5 生成器表达式（Generator Expression）

**惰性求值，节省内存**，类似 Java Stream 的惰性特性。

```python
import sys

# === 列表推导式 vs 生成器表达式 ===
# 列表推导式：立即计算，占用内存
squares_list = [x**2 for x in range(1000000)]
print(sys.getsizeof(squares_list))  # ~8MB

# 生成器表达式：惰性计算，几乎不占内存
squares_gen = (x**2 for x in range(1000000))
print(sys.getsizeof(squares_gen))   # ~112 bytes

# 生成器表达式用法
numbers = [1, 2, 3, 4, 5]

# 求和（不需要创建中间列表）
total = sum(x**2 for x in numbers)  # 推荐
# 等价于 sum([x**2 for x in numbers]) 但更省内存

# 转列表
squares = list(x**2 for x in numbers)

# 转集合
unique = set(x % 3 for x in range(10))

# 转字典
name_len = dict((name, len(name)) for name in ["Alice", "Bob"])

# 用于 any/all
has_negative = any(x < 0 for x in numbers)
all_positive = all(x > 0 for x in numbers)

# 用于 max/min
max_square = max(x**2 for x in numbers)

# 用于 sorted
sorted_squares = sorted(x**2 for x in numbers, reverse=True)

# 链式操作（类似 Stream 链式调用）
result = sum(
    x**2
    for x in range(100)
    if x % 2 == 0
)

# 读取大文件（逐行处理，不一次性加载）
# total_chars = sum(len(line) for line in open("large_file.txt"))

# 嵌套生成器
matrix = [[1, 2, 3], [4, 5, 6]]
flat = (x for row in matrix for x in row)
print(list(flat))  # [1, 2, 3, 4, 5, 6]
```

#### 9.3.6 yield 与生成器函数

```python
# === 生成器函数 ===
def squares(n: int):
    """生成 0 到 n-1 的平方数"""
    for i in range(n):
        yield i ** 2

# 使用
for sq in squares(5):
    print(sq)  # 0, 1, 4, 9, 16

# 转列表
sq_list = list(squares(5))  # [0, 1, 4, 9, 16]

# 无限生成器
def fibonacci():
    """无限斐波那契数列"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 取前10个
fib = fibonacci()
first_10 = [next(fib) for _ in range(10)]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# 带条件的生成器
def primes():
    """无限素数生成器"""
    n = 2
    while True:
        if all(n % i != 0 for i in range(2, int(n**0.5) + 1)):
            yield n
        n += 1

# 分批处理大数据
def batch_process(items: list, batch_size: int):
    """分批处理生成器"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

data = list(range(100))
for batch in batch_process(data, 10):
    print(f"处理批次: {batch[:3]}...")  # 每批10个

# yield from（委托生成器）
def flatten(nested):
    """展平嵌套列表"""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)  # 递归委托
        else:
            yield item

nested = [1, [2, 3], [4, [5, 6]]]
print(list(flatten(nested)))  # [1, 2, 3, 4, 5, 6]
```

#### 9.3.7 itertools 常用函数（类似 Java Stream 工具）

```python
import itertools

# === 无限迭代器 ===
# count: 无限计数
for i in itertools.count(start=10, step=2):
    if i > 20:
        break
    print(i)  # 10, 12, 14, 16, 18, 20

# cycle: 无限循环
colors = itertools.cycle(["red", "green", "blue"])
print([next(colors) for _ in range(5)])  # ['red', 'green', 'blue', 'red', 'green']

# repeat: 重复元素
repeated = list(itertools.repeat("A", 3))  # ['A', 'A', 'A']

# === 排列组合 ===
# 排列（有序）
perms = list(itertools.permutations([1, 2, 3], 2))
# [(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)]

# 组合（无序）
combs = list(itertools.combinations([1, 2, 3, 4], 2))
# [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]

# 可重复组合
combs_wr = list(itertools.combinations_with_replacement([1, 2], 2))
# [(1,1), (1,2), (2,2)]

# 笛卡尔积
product = list(itertools.product([1, 2], ["a", "b"]))
# [(1,'a'), (1,'b'), (2,'a'), (2,'b')]

# === 过滤/分组 ===
# takewhile: 满足条件时取值
nums = [1, 2, 3, 10, 4, 5]
result = list(itertools.takewhile(lambda x: x < 5, nums))
# [1, 2, 3]

# dropwhile: 跳过满足条件的元素
result = list(itertools.dropwhile(lambda x: x < 5, nums))
# [10, 4, 5]

# filterfalse: 过滤不满足条件的
result = list(itertools.filterfalse(lambda x: x % 2 == 0, range(10)))
# [1, 3, 5, 7, 9]

# groupby: 分组（需先排序）
from operator import itemgetter
students = [
    {"name": "Alice", "grade": "A"},
    {"name": "Bob", "grade": "B"},
    {"name": "Charlie", "grade": "A"},
]
students.sort(key=itemgetter("grade"))  # 必须先排序
for grade, group in itertools.groupby(students, key=itemgetter("grade")):
    print(f"{grade}: {[s['name'] for s in group]}")
# A: ['Alice', 'Charlie']
# B: ['Bob']

# === 链式操作 ===
# chain: 连接多个迭代器
list1 = [1, 2, 3]
list2 = [4, 5, 6]
chained = list(itertools.chain(list1, list2))
# [1, 2, 3, 4, 5, 6]

# chain.from_iterable: 展平一层
nested = [[1, 2], [3, 4], [5, 6]]
flat = list(itertools.chain.from_iterable(nested))
# [1, 2, 3, 4, 5, 6]

# islice: 切片迭代器
result = list(itertools.islice(range(100), 5, 10))
# [5, 6, 7, 8, 9]

# starmap: 带解包的 map
pairs = [(2, 3), (4, 5), (6, 7)]
result = list(itertools.starmap(pow, pairs))
# [8, 1024, 279936]

# accumulate: 累积计算
nums = [1, 2, 3, 4, 5]
cumsum = list(itertools.accumulate(nums))  # 累加
# [1, 3, 6, 10, 15]
cummax = list(itertools.accumulate(nums, max))  # 累积最大值
# [1, 2, 3, 4, 5]

# zip_longest: 不等长压缩
a = [1, 2, 3]
b = ["a", "b"]
result = list(itertools.zip_longest(a, b, fillvalue=None))
# [(1, 'a'), (2, 'b'), (3, None)]

# tee: 复制迭代器
it = iter([1, 2, 3])
it1, it2 = itertools.tee(it, 2)
print(list(it1))  # [1, 2, 3]
print(list(it2))  # [1, 2, 3]
```

#### 9.3.8 functools 常用函数

```python
from functools import reduce, partial, lru_cache, wraps

# === reduce（类似 Java Stream.reduce）===
numbers = [1, 2, 3, 4, 5]

# 求和
total = reduce(lambda x, y: x + y, numbers, 0)  # 15

# 求积
product = reduce(lambda x, y: x * y, numbers, 1)  # 120

# 找最大值
maximum = reduce(lambda x, y: x if x > y else y, numbers)  # 5

# 嵌套列表扁平化
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda x, y: x + y, nested, [])  # [1, 2, 3, 4, 5, 6]

# === partial（部分应用/柯里化）===
def power(base: int, exp: int) -> int:
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)

print(square(5))  # 25
print(cube(3))    # 27

# 固定多个参数
def greet(greeting: str, name: str, punctuation: str = "!") -> str:
    return f"{greeting}, {name}{punctuation}"

say_hello = partial(greet, "Hello")
print(say_hello("World"))  # "Hello, World!"

# === lru_cache（缓存装饰器）===
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(100))  # 快速计算（有缓存）

# 查看缓存信息
print(fibonacci.cache_info())

# 清除缓存
fibonacci.cache_clear()

# === wraps（保留原函数元信息）===
import functools

def my_decorator(func):
    @functools.wraps(func)  # 保留原函数的 __name__, __doc__ 等
    def wrapper(*args, **kwargs):
        print("调用前")
        result = func(*args, **kwargs)
        print("调用后")
        return result
    return wrapper

@my_decorator
def my_function():
    """这是我的函数"""
    pass

print(my_function.__name__)  # "my_function"（没有 wraps 会是 "wrapper"）
print(my_function.__doc__)   # "这是我的函数"

# === singledispatch（单分派泛型函数）===
from functools import singledispatch

@singledispatch
def process(value):
    raise NotImplementedError(f"不支持的类型: {type(value)}")

@process.register
def _(value: int):
    return f"整数: {value}"

@process.register
def _(value: str):
    return f"字符串: {value}"

@process.register
def _(value: list):
    return f"列表: {len(value)} 个元素"

print(process(42))        # "整数: 42"
print(process("hello"))   # "字符串: hello"
print(process([1, 2, 3])) # "列表: 3 个元素"
```

### 9.4 日期时间

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `LocalDate.now()` | `date.today()` | 当前日期 | `from datetime import date` |
| `LocalTime.now()` | `datetime.now().time()` | 当前时间 | - |
| `LocalDateTime.now()` | `datetime.now()` | 当前日期时间 | `from datetime import datetime` |
| `Instant.now()` | `datetime.now(timezone.utc)` | UTC 时间 | - |
| `LocalDate.of(2024, 1, 1)` | `date(2024, 1, 1)` | 构造日期 | `date(2024, 1, 1)` |
| `LocalDateTime.of(2024,1,1,10,30)` | `datetime(2024, 1, 1, 10, 30)` | 构造日期时间 | - |
| `localDate.getYear()` | `d.year` | 获取年 | `d.year` |
| `localDate.getMonthValue()` | `d.month` | 获取月 | `d.month` |
| `localDate.getDayOfMonth()` | `d.day` | 获取日 | `d.day` |
| `localDate.plusDays(1)` | `d + timedelta(days=1)` | 加天数 | `from datetime import timedelta` |
| `localDate.minusDays(1)` | `d - timedelta(days=1)` | 减天数 | - |
| `localDate.plusMonths(1)` | `relativedelta(months=1)` | 加月 | `from dateutil.relativedelta import relativedelta` |
| `period.getDays()` | `(d2 - d1).days` | 日期差 | - |
| `duration.toSeconds()` | `(dt2 - dt1).total_seconds()` | 时间差秒数 | - |
| `localDate.format(DateTimeFormatter)` | `d.strftime("%Y-%m-%d")` | 格式化 | `d.strftime("%Y-%m-%d")` |
| `LocalDate.parse("2024-01-01")` | `datetime.strptime(s, fmt)` | 解析 | `datetime.strptime("2024-01-01", "%Y-%m-%d")` |
| `ZoneId.of("Asia/Shanghai")` | `timezone(timedelta(hours=8))` | 时区 | `from datetime import timezone` |
| `ZonedDateTime.now(zoneId)` | `datetime.now(zone)` | 带时区时间 | - |
| `System.currentTimeMillis()` | `time.time() * 1000` | 时间戳毫秒 | `import time` |

```python
from datetime import datetime, date, time, timedelta, timezone
import time

# 当前时间
now = datetime.now()
today = date.today()
utc_now = datetime.now(timezone.utc)

# 构造
d = date(2024, 1, 15)
dt = datetime(2024, 1, 15, 10, 30, 0)

# 获取属性
print(dt.year, dt.month, dt.day)        # 2024 1 15
print(dt.hour, dt.minute, dt.second)    # 10 30 0
print(dt.weekday())                      # 0=周一, 6=周日

# 日期运算
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(weeks=1)
delta = datetime(2024, 12, 31) - datetime(2024, 1, 1)
print(delta.days)  # 365

# 格式化
print(now.strftime("%Y-%m-%d %H:%M:%S"))
print(now.strftime("%Y年%m月%d日 %A"))  # 支持中文

# 解析
parsed = datetime.strptime("2024-01-15", "%Y-%m-%d")

# 时间戳
timestamp = time.time()           # 秒级时间戳
ms_timestamp = int(time.time() * 1000)  # 毫秒级
from_timestamp = datetime.fromtimestamp(timestamp)

# ISO 格式（Web API 常用）
iso_str = now.isoformat()         # "2024-01-15T10:30:00"
iso_str_with_tz = now.astimezone().isoformat()

# 时区转换
import zoneinfo  # Python 3.9+
shanghai_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
shanghai_time = datetime.now(shanghai_tz)
```

### 9.4 文件操作

| Java | Python | 说明 | 示例 |
|------|--------|------|------|
| `new File("path")` | `Path("path")` | 路径对象 | `from pathlib import Path` |
| `file.exists()` | `Path("path").exists()` | 是否存在 | `p.exists()` |
| `file.isFile()` | `Path("path").is_file()` | 是否文件 | `p.is_file()` |
| `file.isDirectory()` | `Path("path").is_dir()` | 是否目录 | `p.is_dir()` |
| `file.getName()` | `Path("path").name` | 文件名 | `p.name` |
| `file.getParent()` | `Path("path").parent` | 父目录 | `p.parent` |
| `file.getAbsolutePath()` | `Path("path").resolve()` | 绝对路径 | `p.resolve()` |
| `file.length()` | `Path("path").stat().st_size` | 文件大小 | `p.stat().st_size` |
| `file.createNewFile()` | `Path("path").touch()` | 创建文件 | `p.touch()` |
| `file.mkdir()` | `Path("path").mkdir()` | 创建目录 | `p.mkdir()` |
| `file.mkdirs()` | `Path("path").mkdir(parents=True)` | 创建多级目录 | `p.mkdir(parents=True, exist_ok=True)` |
| `file.delete()` | `Path("path").unlink()` | 删除文件 | `p.unlink()` |
| `file.delete()` | `Path("path").rmdir()` | 删除空目录 | `p.rmdir()` |
| `Files.deleteIfExists()` | `Path("path").unlink(missing_ok=True)` | 删除（不存在不报错） | - |
| `file.renameTo(newFile)` | `Path("path").rename(new_path)` | 重命名/移动 | `p.rename(new_p)` |
| `file.listFiles()` | `Path("path").iterdir()` | 列出目录内容 | `list(p.iterdir())` |
| `Files.walk(path)` | `Path("path").rglob("*")` | 递归遍历 | `list(p.rglob("*.py"))` |
| `Files.copy(src, dest)` | `shutil.copy(src, dst)` | 复制文件 | `import shutil` |
| `Files.move(src, dest)` | `shutil.move(src, dst)` | 移动文件 | - |
| `Files.readAllBytes(path)` | `Path("path").read_bytes()` | 读取字节 | `p.read_bytes()` |
| `Files.readAllLines(path)` | `Path("path").read_text().splitlines()` | 读取所有行 | `p.read_text().splitlines()` |
| `Files.writeString(path, text)` | `Path("path").write_text(text)` | 写入字符串 | `p.write_text("content")` |
| `new FileReader(path)` | `open(path, "r")` | 打开读取 | `with open(path) as f:` |
| `new FileWriter(path)` | `open(path, "w")` | 打开写入 | `with open(path, "w") as f:` |
| `new FileWriter(path, true)` | `open(path, "a")` | 追加写入 | `with open(path, "a") as f:` |

```python
from pathlib import Path
import shutil
import json

# === 使用 pathlib（推荐） ===
p = Path("data/users.json")

# 路径操作
print(p.name)          # "users.json" - 文件名
print(p.stem)          # "users" - 不带扩展名
print(p.suffix)        # ".json" - 扩展名
print(p.parent)        # Path("data") - 父目录
print(p.resolve())     # 绝对路径

# 检查
if p.exists():
    print(f"文件大小: {p.stat().st_size} 字节")

# 创建目录
Path("data/output").mkdir(parents=True, exist_ok=True)

# 读写文本
p.write_text("Hello, World!", encoding="utf-8")
content = p.read_text(encoding="utf-8")

# 读写 JSON
data = {"name": "张三", "age": 25}
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
loaded = json.loads(p.read_text(encoding="utf-8"))

# 遍历目录
for file in Path("src").rglob("*.py"):  # 递归查找所有 .py 文件
    print(file)

# === 使用 open（传统方式） ===
# 读取
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 全部读取
    # lines = f.readlines()     # 读取所有行为列表
    # for line in f:            # 逐行读取（内存友好）

# 写入
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.writelines(["第二行\n", "第三行\n"])

# 追加
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("新的日志\n")

# 二进制
with open("image.png", "rb") as f:
    data = f.read()

# 复制/移动
shutil.copy("source.txt", "dest.txt")
shutil.move("old.txt", "new.txt")
shutil.rmtree("directory")  # 删除整个目录树
```

### 9.5 JSON 处理

| Java (Jackson/Gson) | Python | 说明 |
|---------------------|--------|------|
| `ObjectMapper().writeValueAsString(obj)` | `json.dumps(obj)` | 对象转 JSON 字符串 |
| `ObjectMapper().readValue(json, Clazz)` | `json.loads(json_str)` | JSON 字符串转对象 |
| `ObjectMapper().writeValue(file, obj)` | `json.dump(obj, file)` | 写入 JSON 文件 |
| `ObjectMapper().readValue(file, Clazz)` | `json.load(file)` | 从文件读取 JSON |
| `@JsonProperty("name")` | 模型中使用字段名 | 字段映射 |
| `@JsonFormat(pattern="yyyy-MM-dd")` | 自定义序列化 | 见示例 |
| `objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL)` | `json.dumps(obj, skipkeys=True)` | 忽略空值 |

```python
import json
from datetime import datetime
from pydantic import BaseModel

# 基本操作
data = {"name": "张三", "age": 25, "hobbies": ["读书", "运动"]}

# 序列化
json_str = json.dumps(data, ensure_ascii=False, indent=2)
# ensure_ascii=False 保留中文
# indent=2 美化输出

# 反序列化
loaded = json.loads(json_str)

# 文件操作
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

# 使用 Pydantic（推荐，类似 Jackson）
class User(BaseModel):
    name: str
    age: int
    email: str | None = None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Pydantic 序列化
user = User(name="张三", age=25, created_at=datetime.now())
json_str = user.model_dump_json(indent=2)

# Pydantic 反序列化
user = User.model_validate_json(json_str)
```

### 9.6 正则表达式

| Java | Python | 说明 |
|------|--------|------|
| `Pattern.compile(regex)` | `re.compile(regex)` | 编译正则 |
| `matcher.matches()` | `re.fullmatch(pattern, string)` | 完全匹配 |
| `matcher.find()` | `re.search(pattern, string)` | 查找第一个 |
| `matcher.find()` 循环 | `re.finditer(pattern, string)` | 查找所有（迭代器） |
| `matcher.replaceAll(replacement)` | `re.sub(pattern, replacement, string)` | 替换全部 |
| `matcher.group(i)` | `match.group(i)` | 获取分组 |
| `matcher.group("name")` | `match.group("name")` | 命名分组 |
| `string.split(regex)` | `re.split(pattern, string)` | 正则分割 |

```python
import re

# 编译正则（性能更好）
pattern = re.compile(r'\b\w+@\w+\.\w+\b')

# 查找
text = "联系: test@example.com 和 admin@example.org"

# 查找第一个
match = re.search(r'\w+@\w+\.\w+', text)
if match:
    print(match.group())  # "test@example.com"

# 查找所有
emails = re.findall(r'\w+@\w+\.\w+', text)
# ['test@example.com', 'admin@example.org']

# 迭代查找（获取位置）
for match in re.finditer(r'\w+@\w+\.\w+', text):
    print(f"找到: {match.group()}, 位置: {match.start()}-{match.end()}")

# 替换
cleaned = re.sub(r'\w+@\w+\.\w+', '[EMAIL]', text)
# "联系: [EMAIL] 和 [EMAIL]"

# 分割
parts = re.split(r'[,;\s]+', "a,b;c d")
# ['a', 'b', 'c', 'd']

# 分组
match = re.search(r'(\w+)@(\w+)\.(\w+)', 'test@example.com')
print(match.group(0))  # "test@example.com" - 整体
print(match.group(1))  # "test" - 第一个分组
print(match.groups())  # ('test', 'example', 'com')

# 命名分组
match = re.search(r'(?P<user>\w+)@(?P<domain>\w+\.\w+)', 'test@example.com')
print(match.group('user'))    # "test"
print(match.group('domain'))  # "example.com"

# 常用正则
patterns = {
    'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
    'phone_cn': r'^1[3-9]\d{9}$',
    'url': r'^https?://[\w\.-]+(:\d+)?(/.*)?$',
    'ipv4': r'^(\d{1,3}\.){3}\d{1,3}$',
    'date': r'^\d{4}-\d{2}-\d{2}$',
}
```

### 9.7 异常处理

| Java | Python | 说明 |
|------|--------|------|
| `try { ... }` | `try:` | 尝试执行 |
| `catch (Exception e) { ... }` | `except Exception as e:` | 捕获异常 |
| `catch (IOException \| SQLException e)` | `except (IOError, SQLError) as e:` | 捕获多种异常 |
| `finally { ... }` | `finally:` | 最终执行 |
| `throw new Exception(msg)` | `raise Exception(msg)` | 抛出异常 |
| `throws Exception` | 无需声明 | 方法签名 |
| `e.getMessage()` | `str(e)` | 异常消息 |
| `e.printStackTrace()` | `import traceback; traceback.print_exc()` | 打印堆栈 |
| `e.getCause()` | `e.__cause__` | 原因异常 |
| 自定义异常 extends Exception | `class MyError(Exception): pass` | 自定义异常 |

```python
# 基本结构
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"除零错误: {e}")
except (TypeError, ValueError) as e:
    print(f"类型或值错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
    raise  # 重新抛出
else:
    print(f"成功: {result}")  # 无异常时执行
finally:
    print("清理资源")

# 上下文管理器（推荐）
with open("file.txt", "r") as f:  # 自动关闭
    content = f.read()

# 抛出异常
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 自定义异常
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

# 使用
raise ValidationError("email", "邮箱格式不正确")

# 获取堆栈信息
import traceback

try:
    raise ValueError("测试错误")
except Exception:
    traceback.print_exc()  # 打印到控制台
    # 或获取字符串
    tb_str = traceback.format_exc()
```

### 9.8 HTTP 请求（Web 项目常用）

| Java (OkHttp/RestTemplate) | Python | 说明 |
|----------------------------|--------|------|
| `HttpClient.newHttpClient().send(request, BodyHandlers.ofString())` | `requests.get(url)` | GET 请求 |
| `client.send(request, BodyHandlers.ofString())` | `requests.post(url, json=data)` | POST 请求 |
| `HttpRequest.newBuilder().header("Auth", "token")` | `headers={"Auth": "token"}` | 设置请求头 |
| `response.body()` | `response.json()` | 获取 JSON 响应 |
| `response.statusCode()` | `response.status_code` | 状态码 |
| `ObjectMapper.readValue(body, Clazz)` | `response.json()` | 自动解析 JSON |
| 异步请求 | `httpx.AsyncClient()` | 异步 HTTP |

```python
import httpx  # 推荐使用 httpx（支持同步和异步）
# 或 import requests  # 传统选择

# === 同步请求（requests 风格） ===
# GET 请求
response = httpx.get("https://api.example.com/users")
if response.status_code == 200:
    users = response.json()

# 带参数
response = httpx.get(
    "https://api.example.com/users",
    params={"page": 1, "size": 10},
    headers={"Authorization": "Bearer token"},
    timeout=10.0
)

# POST JSON
response = httpx.post(
    "https://api.example.com/users",
    json={"name": "张三", "email": "zhangsan@example.com"},
    headers={"Authorization": "Bearer token"}
)

# POST 表单
response = httpx.post(
    "https://api.example.com/login",
    data={"username": "admin", "password": "123456"}
)

# 文件上传
with open("image.png", "rb") as f:
    response = httpx.post(
        "https://api.example.com/upload",
        files={"file": ("image.png", f, "image/png")}
    )

# === 异步请求（推荐用于 FastAPI） ===
async def fetch_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        return response.json()

# 并发请求
async def fetch_multiple():
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"https://api.example.com/users/{i}")
            for i in range(1, 11)
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### 9.9 加密与哈希

| Java | Python | 说明 |
|------|--------|------|
| `MessageDigest.getInstance("SHA-256")` | `hashlib.sha256(data)` | SHA-256 哈希 |
| `MessageDigest.getInstance("MD5")` | `hashlib.md5(data)` | MD5 哈希 |
| `Base64.getEncoder().encodeToString(bytes)` | `base64.b64encode(bytes).decode()` | Base64 编码 |
| `Base64.getDecoder().decode(str)` | `base64.b64decode(str)` | Base64 解码 |
| `SecureRandom.getInstanceStrong()` | `secrets.token_bytes(32)` | 安全随机数 |
| `UUID.randomUUID()` | `uuid.uuid4()` | UUID |
| `SecretKeySpec` + `Cipher` | `cryptography` 库 | AES 加密 |
| BCryptPasswordEncoder | `passlib.hash.bcrypt` | BCrypt 密码哈希 |
| `JwtParserBuilder` | `jose` 库 | JWT |

```python
import hashlib
import base64
import secrets
import uuid
from passlib.hash import bcrypt
from jose import jwt, JWTError

# === 哈希 ===
# SHA-256
text = "Hello, World!"
hash_obj = hashlib.sha256(text.encode())
hash_hex = hash_obj.hexdigest()  # 十六进制字符串

# MD5（不推荐用于安全场景）
md5_hash = hashlib.md5(text.encode()).hexdigest()

# === Base64 ===
encoded = base64.b64encode(b"Hello").decode()  # "SGVsbG8="
decoded = base64.b64decode(encoded)  # b"Hello"

# URL 安全的 Base64
url_safe = base64.urlsafe_b64encode(b"data").decode()

# === 安全随机数 ===
# 生成安全的随机字节
random_bytes = secrets.token_bytes(32)

# 生成安全的随机字符串
token = secrets.token_urlsafe(32)  # URL 安全的 token

# === UUID ===
uuid_str = str(uuid.uuid4())  # "550e8400-e29b-41d4-a716-446655440000"

# === BCrypt 密码哈希 ===
# 哈希密码
hashed = bcrypt.hash("password123")

# 验证密码
is_valid = bcrypt.verify("password123", hashed)

# === JWT ===
from datetime import datetime, timedelta

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

# 创建 JWT
def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 解析 JWT
def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
```

### 9.10 并发与异步

| Java | Python | 说明 |
|------|--------|------|
| `ExecutorService` | `concurrent.futures.ThreadPoolExecutor` | 线程池 |
| `CompletableFuture` | `asyncio` | 异步编程 |
| `synchronized` | `threading.Lock()` | 锁 |
| `CountDownLatch` | `threading.Barrier()` | 屏障 |
| `Semaphore` | `threading.Semaphore()` | 信号量 |
| `BlockingQueue` | `asyncio.Queue` | 异步队列 |
| `Thread.sleep(ms)` | `time.sleep(seconds)` 或 `await asyncio.sleep(seconds)` | 睡眠 |
| `volatile` | 无直接对应 | 共享变量可见性 |

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# === 异步编程（FastAPI 推荐） ===
async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1)  # 模拟 IO
    return {"url": url, "data": "result"}

async def main():
    # 顺序执行
    result1 = await fetch_data("url1")

    # 并发执行
    results = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3"),
    )

# 运行
asyncio.run(main())

# === 线程池 ===
def cpu_intensive_task(n: int) -> int:
    return sum(i * i for i in range(n))

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(cpu_intensive_task, 1000000) for _ in range(4)]
    results = [f.result() for f in futures]

# === 锁 ===
lock = Lock()
counter = 0

def increment():
    global counter
    with lock:
        counter += 1

# === 异步上下文管理器 ===
class AsyncResource:
    async def __aenter__(self):
        print("获取资源")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")

async def use_resource():
    async with AsyncResource() as r:
        await asyncio.sleep(1)
```

### 9.11 类型提示（Python 特有，类似 Java 类型系统）

```python
from typing import (
    Optional, List, Dict, Set, Tuple,
    Union, Callable, TypeVar, Generic,
    Protocol, Final, Literal, TypeAlias
)

# 基本类型
name: str = "张三"
age: int = 25
score: float = 95.5
active: bool = True

# 可选类型（类似 Java 的 @Nullable）
email: str | None = None  # Python 3.10+ 推荐
phone: Optional[str] = None  # 旧写法

# 集合类型
names: list[str] = ["a", "b"]  # Python 3.9+
scores: dict[str, int] = {"a": 90, "b": 85}
unique_ids: set[int] = {1, 2, 3}
point: tuple[int, int, int] = (1, 2, 3)  # 固定长度元组

# 联合类型
result: str | int | None = None  # 可以是多种类型之一

# 函数类型
def process(data: list[str]) -> dict[str, int]:
    return {s: len(s) for s in data}

# 可调用类型
Callback = Callable[[int, str], bool]

def register(callback: Callback) -> None:
    pass

# 类型别名
JsonDict = dict[str, Any]
UserId = int

# 常量（类似 Java final）
MAX_RETRY: Final[int] = 3
API_URL: Final[str] = "https://api.example.com"

# 字面量类型
Status = Literal["pending", "active", "completed"]

def set_status(status: Status) -> None:
    pass

# 泛型
T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

box: Box[int] = Box(42)

# Protocol（类似 Java 接口）
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()
```

### 9.12 日志（loguru）

```python
from loguru import logger
import sys

# 基本使用
logger.info("用户登录成功")
logger.warning("磁盘空间不足")
logger.error("数据库连接失败")
logger.debug("调试信息: {}", some_value)

# 格式化参数（类似 SLF4J）
user_id = 123
logger.info("用户 {} 执行了操作 {}", user_id, "登录")

# 配置
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# 文件输出
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="10 MB",       # 文件大小轮转
    retention="30 days",    # 保留天数
    compression="zip",      # 压缩旧日志
    level="INFO",
    encoding="utf-8"
)

# 异常捕获
@logger.catch
def risky_function():
    return 1 / 0  # 异常会被自动记录

# 上下文绑定
logger.add("logs/app.log", format="{extra[ip]} {message}")

with logger.contextualize(ip="192.168.1.1"):
    logger.info("请求处理中")  # 自动带上 IP
```

---

## 十、快速对比速查表

```python
# Java vs Python 语法对照

# 变量声明
String name = "test";        name: str = "test"
final int COUNT = 10;        COUNT: Final[int] = 10

# 列表
List<String> list = new ArrayList<>();    names: list[str] = []
list.add("a");                            names.append("a")

# Map
Map<String, Integer> map = new HashMap<>();    data: dict[str, int] = {}
map.put("key", 1);                            data["key"] = 1

# 循环
for (int i = 0; i < 10; i++)    for i in range(10):
for (String s : list)           for s in names:

# 异常
try { ... } catch (Exception e) { ... }    try:
                                               ...
                                           except Exception as e:
                                               ...

# Lambda
list.stream().map(s -> s.toUpperCase())    [s.upper() for s in names]

# 空值
if (obj != null)    if obj is not None:
```

---

## 十一、完整项目配置示例

### pyproject.toml（完整配置）

```toml
[tool.poetry]
name = "online-shopping-backend"
version = "1.0.0"
description = "在线购物平台后端 API"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.25"
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"
loguru = "^0.7.2"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
alembic = "^1.13.1"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-asyncio = "^0.23.3"
httpx = "^0.26.0"
black = "^24.1.1"
ruff = "^0.2.1"
mypy = "^1.8.0"
pre-commit = "^3.6.0"

[tool.poetry.scripts]
app = "uvicorn:run"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "ASYNC", # flake8-async
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
show_error_codes = true
show_column_numbers = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

---

## 十二、Docker 部署配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction

# 复制源代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.my_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@db:3306/shop
    depends_on:
      - db
      - redis

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: shop
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine

volumes:
  mysql_data:
```

---

**核心建议**：作为 Java 开发者，你已经有很好的编程基础。学习 Python 时：

1. **用类型提示**（Type Hints）保持 Java 的严谨性
2. **用 Pydantic** 做数据校验，类似 Java Bean Validation
3. **用 Poetry** 管理项目，类似 Maven
4. **用 FastAPI + SQLAlchemy**，这是目前 Python Web 的最佳实践
