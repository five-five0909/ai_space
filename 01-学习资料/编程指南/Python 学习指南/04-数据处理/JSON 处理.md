# JSON 处理

Python 内置 `json` 模块处理 JSON 数据。

## 基础操作

```python
import json

# Python -> JSON (序列化)
data = {"name": "张三", "age": 25}
json_str = json.dumps(data, ensure_ascii=False)  # ensure_ascii=False 支持中文

# JSON -> Python (反序列化)
parsed = json.loads(json_str)
```

## 文件操作

```python
# 写入 JSON 文件
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取 JSON 文件
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

> **提示**：`dumps/loads` 处理字符串，`dump/load` 处理文件。

## LeetCode 实战场景

### 1. 解析 API 返回的 JSON

```python
def parse_leetcode_response(json_str: str):
    """解析类似 LeetCode API 返回的 JSON"""
    import json
    try:
        data = json.loads(json_str)
        return {
            'status': data.get('status', 0),
            'answer': data.get('answer'),
            'explanation': data.get('explanation')
        }
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        return None
```

### 2. 序列化复杂对象

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def listnode_to_json(head: ListNode) -> str:
    """将链表转换为 JSON 数组"""
    import json
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return json.dumps(result)
```

### 3. 测试用例数据加载

```python
def load_test_cases(json_file: str):
    """从 JSON 文件加载测试用例"""
    import json
    with open(json_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return [(c['input'], c['expected']) for c in cases]
```

## 科研实战场景

### 1. 保存/加载训练配置

```python
from dataclasses import dataclass, asdict
import json

@dataclass
class TrainingConfig:
    learning_rate: float = 1e-4
    batch_size: int = 32
    num_epochs: int = 100
    model_name: str = "resnet50"

# 保存配置
config = TrainingConfig()
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(asdict(config), f, indent=2)

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config_dict = json.load(f)
    config = TrainingConfig(**config_dict)
```

### 2. 实验结果记录

```python
import json
from datetime import datetime

def log_experiment_result(metrics: dict, experiment_name: str):
    """记录实验结果到 JSONL 文件"""
    record = {
        'timestamp': datetime.now().isoformat(),
        'experiment': experiment_name,
        'metrics': metrics
    }
    with open('results.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
```

### 3. 数据预处理缓存

```python
import json
import hashlib

def get_data_hash(data_path: str) -> str:
    """计算数据文件的哈希值，用于缓存判断"""
    with open(data_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def save_preprocessing_cache(data_info: dict, cache_file: str):
    """保存预处理结果缓存"""
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data_info, f, indent=2)
```

## 易错点

### 1. 中文乱码问题

```python
# 错误：默认 ASCII 编码
json.dumps({"name": "张三"})  # '{"name": "\u5f20\u4e09"}'

# 正确：关闭 ASCII 转义
json.dumps({"name": "张三"}, ensure_ascii=False)  # '{"name": "张三"}'
```

### 2. 文件编码问题

```python
# 始终指定 encoding='utf-8'
with open('data.json', 'w', encoding='utf-8') as f:  # ✅
    json.dump(data, f)
```

### 3. 缩进格式

```python
# 人类可读
json.dumps(data, indent=2)

# 紧凑格式（网络传输）
json.dumps(data, separators=(',', ':'))
```

## 性能提示

> **时间复杂度**：
> - `dumps/loads`: O(n)，n 为数据大小
> - `dump/load`: O(n)，包含文件 IO

> **优化建议**：
> - 大文件使用流式处理
> - 频繁读写考虑使用 pickle（仅 Python）
> - 生产环境考虑 msgpack/ujson
