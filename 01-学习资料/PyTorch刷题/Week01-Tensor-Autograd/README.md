# Week 1 · Tensor + Autograd

> 基础API入门，建立PyTorch手感

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P001 | 广播规则验证器 | Easy | Tensor、广播 |
| P002 | 高光谱波段切片 | Easy | Tensor、索引 |
| P003 | 手动矩阵乘法+梯度验证 | Medium | Tensor、Autograd |
| P004 | 纯Tensor线性回归 | Easy | Autograd、梯度下降 |

---

## P001 广播规则验证器 ⭐

### 题目描述

给定两个shape不同的Tensor，不用reshape，用广播完成加法，并打印结果shape。

### 函数签名

```python
def broadcast_add(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
```

### 约束条件

- a.ndim >= 1, b.ndim >= 1
- 两个shape必须满足广播规则，否则raise ValueError
- 不允许使用 .reshape() / .view() / .expand()

### 验收断言（assert）

```python
broadcast_add(torch.ones(3,1), torch.ones(1,4)).shape == (3,4)
broadcast_add(torch.ones(5), torch.ones(3,5)).shape == (3,5)
broadcast_add(torch.ones(2), torch.ones(3,4))  # → ValueError
```

### 提示

> 把两个shape从右往左对齐，逐位检查：相等 or 其中一个为1 → 合法

---

## P002 高光谱波段切片 ⭐

### 题目描述

给定shape=(N, C, H, W)的高光谱Tensor，提取第[start, end)范围的波段，并对每个样本按波段维度做归一化（min-max到[0,1]）。

### 函数签名

```python
def extract_bands(x: torch.Tensor, start: int, end: int) -> torch.Tensor:
```

### 约束条件

- 0 <= start < end <= C
- 输出shape=(N, end-start, H, W)
- 归一化在每个样本、每个波段上独立进行，不跨样本

### 验收断言（assert）

```python
output.shape == (N, end-start, H, W)
output.min() >= 0.0 and output.max() <= 1.0
x = torch.arange(24.).reshape(1,4,2,3)
extract_bands(x, 1, 3).shape == (1, 2, 2, 3)
```

### 提示

> 先用 x[:, start:end] 切片，再沿 H×W 维度求min/max做归一化，注意加 eps 防除零

---

## P003 手动矩阵乘法+梯度验证 ⭐⭐

### 题目描述

不用 torch.matmul，用循环或einsum实现(M,K)×(K,N)矩阵乘，然后用 torch.allclose 与 matmul 结果对比，误差 < 1e-5。

### 函数签名

```python
def my_matmul(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
```

### 约束条件

- A.shape=(M,K), B.shape=(K,N)
- 允许用 torch.einsum 或 for 循环，不允许直接调 matmul/mm/bmm
- 结果需要保持 requires_grad 可追踪

### 验收断言（assert）

```python
torch.allclose(my_matmul(A, B), A@B, atol=1e-5) == True
A = torch.randn(4, 3, requires_grad=True)
(my_matmul(A, B).sum()).backward()  # 不报错
```

### 提示

> einsum('mk,kn->mn', A, B) 是最简洁的一行实现

---

## P004 纯Tensor线性回归 ⭐

### 题目描述

给定100个点的 (x, y) 数据（y=3x+2+noise），用 requires_grad=True 的 w, b，手写梯度下降50步，最终 w 在 [2.5, 3.5] 之间，b 在 [1.0, 3.0] 之间。

### 函数签名

```python
def linear_regression_scratch(x, y, lr=0.01, steps=50) -> tuple[float, float]:
```

### 约束条件

- 不允许使用 nn.Module、optim、autograd.grad 以外的高级API
- 每步必须手动 .zero_() 梯度（不能用 optimizer.zero_grad）
- 返回 (w.item(), b.item())

### 验收断言（assert）

```python
2.5 <= w <= 3.5
1.0 <= b <= 3.0
loss第50步 < loss第1步  # 必须在收敛
```

### 提示

> loss = ((w*x + b - y)**2).mean(); loss.backward(); w.data -= lr*w.grad; w.grad.zero_()

---

## 本周学习目标

- [ ] 理解Tensor的广播机制
- [ ] 掌握Tensor索引和切片
- [ ] 理解Autograd计算图
- [ ] 手动实现梯度下降

## 参考答案

> 见 `../solutions/Week01-参考答案.md`