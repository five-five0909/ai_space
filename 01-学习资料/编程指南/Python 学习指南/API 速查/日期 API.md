# 日期 API

## datetime 基础

```python
from datetime import datetime, date, timedelta

# 当前时间
now = datetime.now()
today = date.today()

# 创建日期
dt = datetime(2024, 1, 15, 10, 30)

# 格式化
now.strftime("%Y-%m-%d %H:%M:%S")
now.strftime("%Y/%m/%d")

# 解析字符串
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
```

## 日期计算

```python
# 时间差
delta = timedelta(days=7, hours=2)
future = now + delta
past = now - timedelta(days=3)

# 计算相差天数
diff = future - now
print(diff.days)
```

## LeetCode 实战场景

### 1. 日期差计算 (LC 1360)

```python
def days_between(date1: str, date2: str) -> int:
    fmt = "%Y-%m-%d"
    d1 = datetime.strptime(date1, fmt)
    d2 = datetime.strptime(date2, fmt)
    return abs((d2 - d1).days)
```

### 2. 判断闰年

```python
def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
```

### 3. 一周中的第几天 (LC 1185)

```python
def dayOfTheWeek(day: int, month: int, year: int) -> str:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    dt = datetime(year, month, day)
    return days[dt.weekday()]
```

## 科研实战场景

### 1. 实验时间戳

```python
def gen_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
# 输出：20240405_143052
```

### 2. 训练时间统计

```python
import time
from datetime import timedelta

def format_time(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))
# 输出：1:23:45
```

### 3. 实验日志时间戳

```python
def log_with_timestamp(message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}")
```

### 4. 学习率调度

```python
def get_lr_at_epoch(initial_lr: float, epoch: int,
                    milestones: list = [30, 60, 90]) -> float:
    lr = initial_lr
    for milestone in milestones:
        if epoch >= milestone:
            lr *= 0.1
    return lr
```

## 常用格式字符串

| 格式 | 说明 | 示例 |
|------|------|------|
| %Y | 4 位年份 | 2024 |
| %y | 2 位年份 | 24 |
| %m | 月份 | 01-12 |
| %d | 日期 | 01-31 |
| %H | 小时 | 00-23 |
| %M | 分钟 | 00-59 |
| %S | 秒 | 00-59 |
| %w | 星期 | 0=周日 |

## 性能提示

- 高精度计时使用 `time.perf_counter()`
- 存储时间使用 ISO 格式或时间戳
- 跨时区应用使用 UTC
