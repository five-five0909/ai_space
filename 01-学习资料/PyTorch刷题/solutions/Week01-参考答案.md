# Week 1 参考答案

> 建议完成练习后再查看本答案

---

## P001 广播规则验证器

### 解题思路

1. 检查两个Tensor的shape是否满足广播规则
2. 从右往左对齐shape，逐位检查：相等或其中一个为1
3. 满足条件则直接相加（PyTorch自动广播）

### 参考代码

```python
"""
P001 广播规则验证器
思路：检查广播规则，满足则直接相加
"""

import torch

def broadcast_add(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """广播加法，不满足规则则抛出异常"""
    # 获取两个shape
    shape_a = list(a.shape)
    shape_b = list(b.shape)

    # 从右往左对齐
    max_len = max(len(shape_a), len(shape_b))
    shape_a = [1] * (max_len - len(shape_a)) + shape_a
    shape_b = [1] * (max_len - len(shape_b)) + shape_b

    # 逐位检查广播规则
    for sa, sb in zip(shape_a, shape_b):
        if sa != sb and sa != 1 and sb != 1:
            raise ValueError(f"Shape {a.shape} and {b.shape} are not broadcastable")

    # 直接相加，PyTorch自动广播
    return a + b


# 测试验证
if __name__ == "__main__":
    # Test 1
    result1 = broadcast_add(torch.ones(3, 1), torch.ones(1, 4))
    assert result1.shape == (3, 4), f"Expected (3, 4), got {result1.shape}"
    print(f"Test 1 passed: {result1.shape}")

    # Test 2
    result2 = broadcast_add(torch.ones(5), torch.ones(3, 5))
    assert result2.shape == (3, 5), f"Expected (3, 5), got {result2.shape}"
    print(f"Test 2 passed: {result2.shape}")

    # Test 3 - 应该报错
    try:
        broadcast_add(torch.ones(2), torch.ones(3, 4))
        print("Test 3 failed: Should have raised ValueError")
    except ValueError as e:
        print(f"Test 3 passed: Correctly raised ValueError")
```

### 知识点解析

- **广播规则**: 从右往左对齐维度，每位必须相等或其中一个为1
- **常见陷阱**: (3, 4) 和 (4,) 可以广播，但 (3, 4) 和 (3,) 不行

---

## P002 高光谱波段切片

### 参考代码

```python
"""
P002 高光谱波段切片
思路：切片 + min-max归一化
"""

import torch

def extract_bands(x: torch.Tensor, start: int, end: int) -> torch.Tensor:
    """
    提取指定波段并做min-max归一化
    Args:
        x: shape=(N, C, H, W)
        start: 起始波段索引
        end: 结束波段索引（不含）
    Returns:
        归一化后的波段 shape=(N, end-start, H, W)
    """
    # 切片
    extracted = x[:, start:end, :, :]  # (N, end-start, H, W)

    # Min-max归一化（在每个样本、每个波段上独立）
    # 在 H×W 维度上求 min 和 max
    eps = 1e-8
    min_val = extracted.amin(dim=(2, 3), keepdim=True)  # (N, end-start, 1, 1)
    max_val = extracted.amax(dim=(2, 3), keepdim=True)  # (N, end-start, 1, 1)

    # 归一化到 [0, 1]
    normalized = (extracted - min_val) / (max_val - min_val + eps)

    return normalized


if __name__ == "__main__":
    # 测试
    x = torch.arange(24.).reshape(1, 4, 2, 3)
    result = extract_bands(x, 1, 3)
    print(f"Shape: {result.shape}")
    print(f"Min: {result.min()}, Max: {result.max()}")
```

---

## P003 手动矩阵乘法+梯度验证

### 参考代码

```python
"""
P003 手动矩阵乘法
思路：用einsum实现，保持梯度追踪
"""

import torch

def my_matmul(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    """
    手动矩阵乘法 (M, K) @ (K, N) -> (M, N)
    """
    # 方法1: einsum（推荐）
    return torch.einsum('mk,kn->mn', A, B)

    # 方法2: for循环（理解原理）
    # M, K = A.shape
    # K, N = B.shape
    # C = torch.zeros(M, N)
    # for i in range(M):
    #     for j in range(N):
    #         for k in range(K):
    #             C[i, j] += A[i, k] * B[k, j]
    # return C


if __name__ == "__main__":
    # 测试
    A = torch.randn(4, 3, requires_grad=True)
    B = torch.randn(3, 5)

    my_result = my_matmul(A, B)
    ref_result = A @ B

    print(f"Close: {torch.allclose(my_result, ref_result, atol=1e-5)}")

    # 测试梯度
    loss = my_result.sum()
    loss.backward()
    print(f"A.grad shape: {A.grad.shape}")
```

---

## P004 纯Tensor线性回归

### 参考代码

```python
"""
P004 纯Tensor线性回归
思路：手动梯度下降
"""

import torch

def linear_regression_scratch(x, y, lr=0.01, steps=50) -> tuple[float, float]:
    """
    纯Tensor实现线性回归
    y = w * x + b
    """
    # 初始化参数
    w = torch.randn(1, requires_grad=True)
    b = torch.randn(1, requires_grad=True)

    losses = []

    for step in range(steps):
        # 前向传播
        y_pred = w * x + b

        # 计算损失 (MSE)
        loss = ((y_pred - y) ** 2).mean()
        losses.append(loss.item())

        # 反向传播
        loss.backward()

        # 更新参数（手动）
        with torch.no_grad():
            w -= lr * w.grad
            b -= lr * b.grad

            # 清零梯度
            w.grad.zero_()
            b.grad.zero_()

    print(f"Loss: {losses[0]:.4f} -> {losses[-1]:.4f}")
    print(f"w = {w.item():.3f}, b = {b.item():.3f}")

    return w.item(), b.item()


if __name__ == "__main__":
    # 生成数据 y = 3x + 2 + noise
    torch.manual_seed(42)
    x = torch.randn(100)
    y = 3 * x + 2 + torch.randn(100) * 0.5

    w, b = linear_regression_scratch(x, y, lr=0.1, steps=100)

    assert 2.5 <= w <= 3.5, f"w={w} not in [2.5, 3.5]"
    assert 1.0 <= b <= 3.0, f"b={b} not in [1.0, 3.0]"
    print("All tests passed!")
```

### 易错点提醒

- 每步必须 `w.grad.zero_()`，否则梯度会累加
- `with torch.no_grad()` 包裹参数更新，否则会记录计算图