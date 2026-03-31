# 编码规范

> 本文件定义项目的代码风格和质量标准。

## Python 规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 行长度不超过 120 字符
- 使用 UTF-8 编码

### 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块 | snake_case | `data_processor.py` |
| 类 | PascalCase | `DataProcessor` |
| 函数/方法 | snake_case | `process_data()` |
| 常量 | UPPER_SNAKE | `MAX_BATCH_SIZE` |
| 变量 | snake_case | `user_count` |

### 类型注解

```python
# 推荐：使用类型注解
def process_data(items: list[str], threshold: float = 0.5) -> dict[str, int]:
    ...

# 私有方法使用下划线前缀
def _internal_helper(self) -> None:
    ...
```

### 错误处理

```python
# 推荐：显式处理错误
def read_config(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {path}")
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误: {e}") from e
```

## 文档规范

### 函数文档

```python
def calculate_metrics(predictions: np.ndarray, labels: np.ndarray) -> Metrics:
    """计算模型预测指标。

    Args:
        predictions: 模型预测值，形状 (N, C)
        labels: 真实标签，形状 (N,)

    Returns:
        Metrics 对象，包含 accuracy, precision, recall, f1

    Raises:
        ValueError: 当输入形状不匹配时
    """
    ...
```

## 禁止事项

- ❌ 硬编码敏感信息（密钥、密码）
- ❌ 使用裸 `except:` 捕获所有异常
- ❌ 忽略类型检查警告
- ❌ 在循环中使用 `+` 拼接字符串
- ❌ 导入未使用的模块