# 文件 IO

## 基础文件操作

```python
from pathlib import Path

# 读取文件
content = Path("data.txt").read_text(encoding='utf-8')

# 写入文件
Path("output.txt").write_text("Hello", encoding='utf-8')

# 追加写入
with open("log.txt", "a", encoding='utf-8') as f:
    f.write("New line\n")
```

> **提示**：优先使用 `pathlib` 而不是 `open()`，代码更简洁。

## LeetCode 实战场景

### 1. 大文件读取（逐行处理）

```python
def process_large_file(filepath):
    """处理超大文件，避免内存溢出"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 使用
for line in process_large_file("large_input.txt"):
    process(line)
```

### 2. 读取输入文件

```python
def read_lc_input(filepath):
    """读取 LeetCode 风格输入"""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # 解析输入
    nums = list(map(int, lines[0].strip().split(',')))
    target = int(lines[1].strip())
    return nums, target
```

## 科研实战场景

### 1. 日志文件读写

```python
from pathlib import Path
from datetime import datetime

def log_message(message: str, log_file: str = "train.log"):
    """写入带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

# 使用
log_message("Epoch 1 completed, loss=0.5234")
```

### 2. CSV 结果保存

```python
import csv

def save_results(results: list, filepath: str):
    """保存实验结果到 CSV"""
    if not results:
        return

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

# 使用
results = [
    {"epoch": 1, "train_loss": 0.5, "val_loss": 0.45},
    {"epoch": 2, "train_loss": 0.4, "val_loss": 0.38},
]
save_results(results, "results.csv")
```

### 3. JSON 配置/结果保存

```python
import json

def save_config(config: dict, filepath: str):
    """保存配置到 JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_config(filepath: str) -> dict:
    """从 JSON 加载配置"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### 4. Checkpoint 保存/加载

```python
import torch

def save_checkpoint(model, optimizer, epoch, filepath):
    """保存训练检查点"""
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    torch.save(checkpoint, filepath)
    print(f"Checkpoint saved to {filepath}")

def load_checkpoint(filepath, model, optimizer=None):
    """加载训练检查点"""
    checkpoint = torch.load(filepath, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch']
    return start_epoch
```

## pathlib 常用操作

```python
from pathlib import Path

# 创建目录
Path("data/train").mkdir(parents=True, exist_ok=True)

# 检查文件/目录
Path("file.txt").exists()
Path("file.txt").is_file()
Path("dir/").is_dir()

# 列出文件
for f in Path("data/").glob("*.txt"):
    print(f)

# 递归列出
for f in Path("data/").rglob("*.txt"):
    print(f)

# 路径拼接
Path("data") / "train" / "image.jpg"
```

## 性能提示

> **最佳实践**：
> - 始终使用 `with` 语句打开文件（自动关闭）
> - 大文件使用迭代器逐行读取
> - 指定 `encoding='utf-8'` 避免编码问题
> - 使用 `pathlib` 而不是 `os.path`（更现代）
