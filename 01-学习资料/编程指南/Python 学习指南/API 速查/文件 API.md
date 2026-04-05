# 文件 API

## 基础读写

```python
# 读取整个文件
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 逐行读取
with open('file.txt', 'r', encoding='utf-8') as f:
    for line in f:
        process(line)

# 读取所有行
with open('file.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 写入文件
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("内容")
    f.writelines(lines)
```

## 文件模式

| 模式 | 说明 |
|------|------|
| 'r' | 只读 |
| 'w' | 写入（覆盖） |
| 'a' | 追加 |
| 'x' | 独占创建 |
| 'b' | 二进制模式 |
| '+' | 读写 |

## LeetCode 实战场景

### 1. 批量读取测试用例

```python
from pathlib import Path

def load_test_cases(test_dir: str) -> list:
    test_path = Path(test_dir)
    cases = []

    for f in sorted(test_path.glob('test_*.txt')):
        with open(f, 'r') as file:
            cases.append({
                'name': f.name,
                'input': file.read().strip()
            })
    return cases
```

## 科研实战场景

### 1. 保存/加载实验配置

```python
import json
from pathlib import Path

def save_config(config: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### 2. 检查点保存

```python
import torch

def save_checkpoint(model, optimizer, epoch, path: str):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, path)

def load_checkpoint(path: str, model, optimizer=None):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch']
```

### 3. 日志文件写入

```python
from datetime import datetime

class Logger:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
```

### 4. 大文件分块读取

```python
def read_large_file(path: str, chunk_size: int = 8192):
    with open(path, 'r', encoding='utf-8') as f:
        while chunk := f.read(chunk_size):
            process(chunk)
```

## pathlib (现代文件路径处理)

```python
from pathlib import Path

# 创建路径
p = Path('data') / 'train' / 'images'

# 获取信息
p.parent      # PosixPath('data/train')
p.name        # 'images'
p.suffix      # 文件扩展名
p.stem        # 文件名不含扩展名

# 检查
p.exists()    # 是否存在
p.is_file()   # 是否文件
p.is_dir()    # 是否目录

# 遍历
for f in p.glob('*.jpg'):  # 所有 jpg 文件
    print(f)

# 创建/删除
p.mkdir(parents=True, exist_ok=True)
p.rmdir()
```

## 易错点

### 1. 忘记指定编码

```python
# 可能乱码
open('file.txt', 'r')

# 始终指定编码
open('file.txt', 'r', encoding='utf-8')
```

### 2. 忘记关闭文件

```python
# 资源泄漏
f = open('file.txt')
content = f.read()

# 使用 with
with open('file.txt') as f:
    content = f.read()
```
