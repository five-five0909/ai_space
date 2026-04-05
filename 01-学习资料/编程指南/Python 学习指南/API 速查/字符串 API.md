# 字符串 API

## 基础操作

```python
s = "Hello, Python!"

len(s)           # 13
s[0]             # 'H'
s[-1]            # '!'
s[0:5]           # 'Hello'
s[::-1]          # 反转
```

## 常用方法

```python
s = "  Hello  "

# 去除空白
s.strip()        # 'Hello'
s.lstrip()       # 'Hello  '
s.rstrip()       # '  Hello'

# 大小写转换
s.lower()        # '  hello  '
s.upper()        # '  HELLO  '
s.capitalize()   # '  hello  '
s.title()        # '  Hello  '

# 检查
s.startswith("Hello")  # False (有前导空格)
s.endswith("lo")       # False

# 查找
s.find("lo")     # 4 (首次出现位置)
s.rfind("l")     # 10 (最后出现位置)
s.count("l")     # 2

# 替换和分割
s.replace("Hello", "World")  # '  World  '
s.split(" ")     # ['', '', 'Hello', '', '']
```

## LeetCode 实战场景

### 1. 字母异位词判断 (LC 242)

```python
def is_anagram(s: str, t: str) -> bool:
    return sorted(s.lower()) == sorted(t.lower())
```

### 2. 有效的字母异位词

```python
def is_anagram_v2(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    from collections import Counter
    return Counter(s) == Counter(t)
```

### 3. 最长公共前缀 (LC 14)

```python
def longest_common_prefix(strs: list) -> str:
    if not strs:
        return ""

    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
```

### 4. 无重复字符的最长子串 (LC 3)

```python
def length_of_longest_substring(s: str) -> int:
    char_set = set()
    left = 0
    max_len = 0

    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len
```

## 科研实战场景

### 1. 论文标题规范化

```python
def format_title(title: str) -> str:
    # 去除多余空白，首字母大写
    return ' '.join(title.strip().split()).title()
```

### 2. 实验名称生成

```python
from datetime import datetime

def gen_experiment_name(model: str, dataset: str) -> str:
    ts = datetime.now().strftime("%m%d_%H%M")
    return f"{ts}_{model}_{dataset}"
# 输出：0405_1430_resnet_cifar10
```

### 3. 日志解析

```python
import re

def parse_log_line(line: str) -> dict:
    # [INFO] Epoch 1 - Loss: 0.234
    pattern = r'\[(\w+)\] Epoch (\d+) - Loss: ([\d.]+)'
    match = re.match(pattern, line)
    if match:
        return {
            'level': match.group(1),
            'epoch': int(match.group(2)),
            'loss': float(match.group(3))
        }
    return None
```

## 格式化

```python
name = "张三"
score = 95.5678

# f-string (Python 3.6+)
f"姓名：{name}"
f"分数：{score:.2f}"  # '分数：95.57'
f"双倍：{score * 2}"

# format 方法
"姓名：{}, 分数：{:.2f}".format(name, score)

# 字典格式化
"姓名：{name}, 分数：{score}".format(name=name, score=score)
```

## 性能提示

- 多字符串连接使用 `"".join(list)` 而非 `+`
- 频繁修改使用 `io.StringIO`
- 查找用 `in` 操作符最快
