# OS 操作

## 基础系统操作

```python
import os
from pathlib import Path

# 当前工作目录
os.getcwd()

# 切换目录
os.chdir("/path/to/dir")

# 创建目录
os.makedirs("nested/dir", exist_ok=True)

# 删除目录
os.rmdir("empty_dir")
os.removedirs("nested/empty")

# 环境变量
os.getenv("PATH")
os.environ.get("CUDA_VISIBLE_DEVICES", "0")
```

## LeetCode 实战场景

### 1. 批量读取测试用例

```python
from pathlib import Path

def load_test_cases(test_dir: str):
    """从目录加载所有测试用例文件"""
    test_path = Path(test_dir)
    results = []

    for f in sorted(test_path.glob("test_*.txt")):
        with open(f, 'r') as file:
            input_data = file.read().strip()
            expected = f.with_suffix('.expected').read_text().strip()
            results.append((f.name, input_data, expected))

    return results
```

### 2. 文件批量重命名

```python
from pathlib import Path

def batch_rename(directory: str, pattern: str, replacement: str):
    """批量重命名文件"""
    dir_path = Path(directory)

    for f in dir_path.iterdir():
        if f.is_file():
            new_name = f.name.replace(pattern, replacement)
            f.rename(f.with_name(new_name))
            print(f"Renamed: {f.name} -> {new_name}")
```

## 科研实战场景

### 1. 实验目录自动创建

```python
from pathlib import Path
from datetime import datetime

def create_experiment_dir(base_dir: str, experiment_name: str) -> Path:
    """创建标准实验目录结构"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = Path(base_dir) / f"{timestamp}_{experiment_name}"

    # 创建子目录
    (exp_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    (exp_dir / "logs").mkdir(parents=True, exist_ok=True)
    (exp_dir / "results").mkdir(parents=True, exist_ok=True)
    (exp_dir / "configs").mkdir(parents=True, exist_ok=True)

    return exp_dir

# 使用
exp_dir = create_experiment_dir("experiments", "resnet_cifar10")
print(f"Experiment directory: {exp_dir}")
```

### 2. 查找最近检查点

```python
from pathlib import Path

def find_latest_checkpoint(checkpoint_dir: str) -> Path:
    """查找最新的检查点文件"""
    dir_path = Path(checkpoint_dir)

    checkpoints = list(dir_path.glob("*.pt"))
    if not checkpoints:
        return None

    # 按修改时间排序
    latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
    return latest

# 使用
ckpt = find_latest_checkpoint("checkpoints/")
if ckpt:
    print(f"Found checkpoint: {ckpt}")
```

### 3. 清理过期实验

```python
from pathlib import Path
import time

def cleanup_old_experiments(experiments_dir: str, days: int = 30):
    """清理超过指定天数的实验"""
    exp_path = Path(experiments_dir)
    cutoff = time.time() - (days * 24 * 60 * 60)

    for exp_dir in exp_path.iterdir():
        if exp_dir.is_dir():
            # 检查目录中最新文件的修改时间
            files = list(exp_dir.rglob("*"))
            if files:
                latest = max(f.stat().st_mtime for f in files)
                if latest < cutoff:
                    print(f"Removing old experiment: {exp_dir}")
                    # shutil.rmtree(exp_dir)  # 取消注释以启用删除
```

### 4. 读取配置文件

```python
import os
from pathlib import Path
import json

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent

def load_config(config_name: str = "config.json") -> dict:
    """从项目目录加载配置"""
    config_path = get_project_root() / "configs" / config_name
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 使用环境变量覆盖配置
def get_config_value(key: str, default=None):
    """获取配置值，环境变量优先"""
    env_value = os.getenv(key.upper())
    if env_value:
        return env_value

    config = load_config()
    return config.get(key, default)
```

## 常用系统命令

```python
import subprocess

# 运行系统命令
result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
print(result.stdout)

# 运行 Python 脚本
subprocess.run(["python", "train.py", "--epochs", "100"])

# 带超时运行
try:
    subprocess.run(["long_running_script.py"], timeout=3600)
except subprocess.TimeoutExpired:
    print("Script timed out!")
```

## 性能提示

> **最佳实践**：
> - 使用 `pathlib` 代替 `os.path`（更现代、更可读）
> - 使用 `exist_ok=True` 避免目录已存在的错误
> - 使用 `shutil` 进行高级文件操作（复制、移动、删除）
