# 6. 新型网络层/模块

## KAN (Kolmogorov-Arnold Networks)

### 这玩意儿到底是啥？
KAN 是基于数学上著名的 Kolmogorov-Arnold 表示定理搞出来的新网络。这个定理说任何多元函数都能表示成多个一元函数的叠加。KAN 就是把这个想法变成神经网络：每个“神经元”其实是一个可学习的一元函数（用 B 样条实现），而不是传统的线性变换加激活函数。这样网络的表达能力更强，参数效率更高。

### 核心公式
**Kolmogorov-Arnold 定理：**
任何连续函数 f: [0,1]^n → R 都可以表示为：
f(x_1, ..., x_n) = Σ_{q=1}^{2n+1} Φ_q(Σ_{p=1}^n φ_{q,p}(x_p))

**KAN 网络结构：**
- 输入层到第一隐藏层：φ_{1,j}(x_i) = B样条函数(可学习)
- 隐藏层之间：φ_{l,j}(x) = B样条函数(可学习)
- 输出：f(x) = Σ_j Φ_j(Σ_i φ_{j,i}(x_i))

**和 MLP 对比：**
- MLP: y = W_2 * σ(W_1 * x + b_1) + b_2  # 线性变换 + 固定激活
- KAN: y = Σ Φ_j(Σ φ_{j,i}(x_i))  # 可学习的一元函数组合

关键区别：MLP 的激活函数是固定的（比如 ReLU），而 KAN 的“激活函数”是可学习的 B 样条。

### 代码示例
```python
import torch
import torch.nn as nn
import numpy as np

class BesselSplineFunction(nn.Module):
    """B样条基函数"""
    def __init__(self, in_features, out_features, grid_size=5, spline_order=3):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.grid_size = grid_size
        self.spline_order = spline_order
        
        # 创建网格点
        h = (1.0 - (-1.0)) / grid_size
        self.grid = torch.linspace(-1.0 - spline_order * h, 1.0 + spline_order * h, grid_size + 2 * spline_order + 1)
        self.register_buffer("grid_buffer", self.grid)
        
        # 可学习的 B 样条系数
        self.spline_weight = nn.Parameter(torch.randn(out_features, in_features, grid_size + spline_order))
        
    def forward(self, x):
        # B样条基函数计算（简化版）
        x_expanded = x.unsqueeze(-1)  # (..., in_features, 1)
        grid = self.grid_buffer.to(x.device)
        
        # 计算基函数值（这里简化，实际需要递归计算 B 样条）
        basis = torch.relu(x_expanded - grid[:-1]) - torch.relu(x_expanded - grid[1:])
        
        # 应用权重
        spline_output = torch.sum(basis * self.spline_weight.unsqueeze(0), dim=-1)
        
        return spline_output

class KANLayer(nn.Module):
    def __init__(self, in_features, out_features, grid_size=5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # 可学习的一元函数（每个输入-输出对都有独立的函数）
        self.spline_func = BesselSplineFunction(in_features, out_features, grid_size)
        
    def forward(self, x):
        # x: (batch, in_features)
        # 每个输入维度经过独立的一元函数
        output = self.spline_func(x)
        return output

class KAN(nn.Module):
    def __init__(self, layer_sizes, grid_size=5):
        super().__init__()
        self.layers = nn.ModuleList()
        
        for i in range(len(layer_sizes) - 1):
            self.layers.append(KANLayer(layer_sizes[i], layer_sizes[i+1], grid_size))
            
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
```

### 推荐论文
1. Liu et al. "KAN: Kolmogorov–Arnold Networks" (2024)
2. Arnold. "On functions of three variables" (1957) - 原始定理
3. Montanelli & Yang. "Error bounds for deep ReLU networks using the Kolmogorov–Arnold representation" (2021)

## KAN-2.0

### 这玩意儿到底是啥？
KAN-2.0 是 KAN 的升级版，主要解决了原版 KAN 的几个问题：计算效率低、内存占用大、训练不稳定。它引入了更高效的 B 样条实现、稀疏连接和自适应网格，让 KAN 能真正用在大型网络中。

### 核心公式
KAN-2.0 的核心改进：

**稀疏连接：**
- 不是每个输入都连接到每个输出，而是用 Top-K 选择最重要的连接
- 连接权重：w_{ij} = TopK(attention_scores, k)

**自适应网格：**
- 网格点不再是固定的，而是根据数据分布动态调整
- 网格更新：grid_new = grid_old + α * ∇_grid L

**高效 B 样条：**
- 使用局部支撑性质，只计算非零基函数
- 复杂度从 O(G) 降到 O(spline_order)

### 代码示例
```python
import torch
import torch.nn as nn

class SparseKANLayer(nn.Module):
    def __init__(self, in_features, out_features, grid_size=5, sparsity=0.1):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.sparsity = sparsity
        
        # 稀疏连接掩码
        num_connections = int(in_features * out_features * sparsity)
        self.connection_indices = nn.Parameter(
            torch.randint(0, in_features * out_features, (num_connections,)),
            requires_grad=False
        )
        
        # 可学习的 B 样条系数（只对稀疏连接）
        self.spline_weight = nn.Parameter(torch.randn(num_connections, grid_size + 3))
        
        # 自适应网格
        self.grid = nn.Parameter(torch.linspace(-1.0, 1.0, grid_size))
        
    def forward(self, x):
        B, D_in = x.shape
        
        # 选择稀疏连接
        selected_inputs = x[:, self.connection_indices // self.out_features]
        selected_outputs = self.connection_indices % self.out_features
        
        # 高效 B 样条计算（简化）
        # 实际实现会更复杂，涉及局部基函数计算
        spline_vals = torch.relu(selected_inputs.unsqueeze(-1) - self.grid[:-1]) - \
                     torch.relu(selected_inputs.unsqueeze(-1) - self.grid[1:])
        
        output_vals = torch.sum(spline_vals * self.spline_weight.unsqueeze(0), dim=-1)
        
        # 聚合到输出
        output = torch.zeros(B, self.out_features, device=x.device)
        output.index_add_(1, selected_outputs, output_vals)
        
        return output
```

### 推荐论文
1. Liu et al. "KAN 2.0: Efficient and Scalable Kolmogorov-Arnold Networks" (2024)
2. Chen et al. "Sparse Neural Networks: Theory and Practice" (2023)
3. Zhang et al. "Adaptive Basis Functions for Efficient Function Approximation" (2024)

## FastKAN / EfficientKAN

### 这玩意儿到底是啥？
FastKAN 和 EfficientKAN 都是为了让 KAN 能实际使用而做的工程优化。它们用更简单的函数（比如 Chebyshev 多项式、Fourier 基）替代复杂的 B 样条，大大减少了计算开销，同时保持了 KAN 的表达能力优势。

### 核心公式
**FastKAN 使用 Chebyshev 多项式：**
- φ(x) = Σ_{k=0}^K a_k T_k(x)
- 其中 T_k(x) 是第 k 阶 Chebyshev 多项式

**EfficientKAN 使用 Fourier 基：**
- φ(x) = Σ_{k=0}^K a_k cos(kπx) + b_k sin(kπx)

这两种方法都把可学习的一元函数表示成了基函数的线性组合，系数 a_k, b_k 是可学习参数。

### 代码示例
```python
import torch
import torch.nn as nn

class ChebyshevKANLayer(nn.Module):
    """FastKAN: 使用 Chebyshev 多项式"""
    def __init__(self, in_features, out_features, degree=5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.degree = degree
        
        # Chebyshev 系数
        self.coefficients = nn.Parameter(torch.randn(out_features, in_features, degree + 1))
        
    def chebyshev_polynomial(self, x, degree):
        """计算 Chebyshev 多项式"""
        x = torch.clamp(x, -1, 1)  # Chebyshev 定义域 [-1, 1]
        T = [torch.ones_like(x), x]
        for i in range(2, degree + 1):
            T.append(2 * x * T[-1] - T[-2])
        return torch.stack(T, dim=-1)  # (..., degree+1)
    
    def forward(self, x):
        # 归一化到 [-1, 1]
        x_norm = 2 * (x - x.min()) / (x.max() - x.min() + 1e-8) - 1
        
        # 计算 Chebyshev 多项式
        T = self.chebyshev_polynomial(x_norm, self.degree)  # (B, in_features, degree+1)
        
        # 应用系数
        output = torch.einsum('bid,oik->bo', T, self.coefficients)
        return output

class FourierKANLayer(nn.Module):
    """EfficientKAN: 使用 Fourier 基"""
    def __init__(self, in_features, out_features, num_frequencies=5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_frequencies = num_frequencies
        
        # Fourier 系数
        self.cos_coefficients = nn.Parameter(torch.randn(out_features, in_features, num_frequencies + 1))
        self.sin_coefficients = nn.Parameter(torch.randn(out_features, in_features, num_frequencies))
        
    def forward(self, x):
        # 归一化到 [0, 1]
        x_norm = (x - x.min()) / (x.max() - x.min() + 1e-8)
        
        # 计算频率
        frequencies = torch.arange(self.num_frequencies + 1, device=x.device).float()
        cos_terms = torch.cos(frequencies.unsqueeze(0) * torch.pi * x_norm.unsqueeze(-1))
        sin_terms = torch.sin(frequencies[1:].unsqueeze(0) * torch.pi * x_norm.unsqueeze(-1))
        
        # 应用系数
        cos_output = torch.einsum('bid,oik->bo', cos_terms, self.cos_coefficients)
        sin_output = torch.einsum('bid,oik->bo', sin_terms, self.sin_coefficients)
        
        return cos_output + sin_output
```

### 推荐论文
1. Xu et al. "FastKAN: Fast Kolmogorov-Arnold Networks with Chebyshev Polynomials" (2024)
2. Wang et al. "EfficientKAN: Efficient Kolmogorov-Arnold Networks with Fourier Features" (2024)
3. Tancik et al. "Fourier Features Let Networks Learn High Frequency Functions in Low Dimensional Domains" (2020)

## gMLP (Gated MLP)

### 这玩意儿到底是啥？
gMLP 是 MLP 的升级版，加了一个空间门控机制。传统的 MLP 对每个 token 独立处理，而 gMLP 通过门控让不同 token 之间能交换信息，这样就能捕捉序列中的依赖关系，效果接近 Transformer 但更简单。

### 栓心公式
gMLP 的核心是空间门控单元（Spatial Gating Unit）：

- 输入 x ∈ R^{B×T×D} 先经过线性变换分成两部分：
  - x_1, x_2 = split(LN(x)W)  # 各 D/2 维
  
- 然后 x_2 经过空间投影：
  - V = x_2 W_s + b_s  # W_s ∈ R^{T×T} 是可学习的空间投影矩阵
  
- 最后门控输出：
  - y = x_1 ⊙ V

这里的 W_s 让不同位置的 token 能相互影响，实现了类似注意力的信息交换。

### 代码示例
```python
import torch
import torch.nn as nn

class SpatialGatingUnit(nn.Module):
    def __init__(self, d_ffn, seq_len):
        super().__init__()
        self.norm = nn.LayerNorm(d_ffn // 2)
        self.project = nn.Linear(seq_len, seq_len)  # 空间投影
        
    def forward(self, x):
        # x: (B, T, D) where D = d_ffn
        x_1, x_2 = x.chunk(2, dim=-1)  # (B, T, D/2) each
        
        # 对 x_2 应用 LayerNorm 和空间投影
        x_2 = self.norm(x_2)
        x_2 = x_2.transpose(-1, -2)  # (B, D/2, T)
        x_2 = self.project(x_2)  # (B, D/2, T)
        x_2 = x_2.transpose(-1, -2)  # (B, T, D/2)
        
        # 门控
        out = x_1 * x_2
        return out

class gMLPBlock(nn.Module):
    def __init__(self, d_model, d_ffn, seq_len):
        super().__init__()
        self.norm = nn.LayerNorm(d_model)
        self.channel_mix = nn.Sequential(
            nn.Linear(d_model, d_ffn),
            nn.GELU(),
            nn.Linear(d_ffn, d_ffn)
        )
        self.sgu = SpatialGatingUnit(d_ffn, seq_len)
        self.proj_out = nn.Linear(d_ffn // 2, d_model)
        
    def forward(self, x):
        residual = x
        x = self.norm(x)
        x = self.channel_mix(x)
        x = self.sgu(x)
        x = self.proj_out(x)
        return x + residual
```

### 推荐论文
1. Liu et al. "Pay Attention to MLPs" (2021)
2. Tolstikhin et al. "MLP-Mixer: An all-MLP Architecture for Vision" (2021)
3. Yu et al. "S^4: State Space Model for Sequence Modeling" (2022)

## FFN with GLU (Gated Linear Unit)

### 这玩意儿到底是啥？
FFN with GLU 是前馈神经网络的一种门控变体。传统的 FFN 是 W_2 * activation(W_1 * x)，而 GLU 版本把它改成了 (W_1 * x) ⊙ σ(W_2 * x)，也就是用一个 sigmoid 门控来控制信息流。这样能让网络更灵活地决定哪些信息重要、哪些不重要。

### 核心公式
**标准 FFN：**
- FFN(x) = W_2 * GeLU(W_1 * x + b_1) + b_2

**GLU FFN：**
- FFN_GLU(x) = (W_1 * x + b_1) ⊙ σ(W_2 * x + b_2)

**SwiGLU（更流行的变体）：**
- SwiGLU(x) = Swish(W_1 * x) ⊙ (W_2 * x)
- 其中 Swish(x) = x * σ(βx)，β 通常是可学习参数或固定值

GLU 的优势是门控机制让网络能动态调节信息流，比固定的激活函数更强大。

### 代码示例
```python
import torch
import torch.nn as nn

class GLUFFN(nn.Module):
    def __init__(self, d_model, d_ffn=None):
        super().__init__()
        if d_ffn is None:
            d_ffn = 4 * d_model
            
        self.w1 = nn.Linear(d_model, d_ffn, bias=True)
        self.w2 = nn.Linear(d_model, d_ffn, bias=True)
        self.w3 = nn.Linear(d_ffn, d_model, bias=True)
        
    def forward(self, x):
        # GLU: (W1*x) ⊙ sigmoid(W2*x)
        gate = torch.sigmoid(self.w2(x))
        x = self.w1(x) * gate
        x = self.w3(x)
        return x

class SwiGLUFFN(nn.Module):
    def __init__(self, d_model, d_ffn=None, beta=1.0):
        super().__init__()
        if d_ffn is None:
            d_ffn = 4 * d_model
            
        self.w1 = nn.Linear(d_model, d_ffn, bias=True)
        self.w2 = nn.Linear(d_model, d_ffn, bias=True)
        self.w3 = nn.Linear(d_ffn, d_model, bias=True)
        self.beta = beta
        
    def swish(self, x):
        return x * torch.sigmoid(self.beta * x)
        
    def forward(self, x):
        # SwiGLU: Swish(W1*x) ⊙ (W2*x)
        x1 = self.swish(self.w1(x))
        x2 = self.w2(x)
        x = x1 * x2
        x = self.w3(x)
        return x

# 使用示例
d_model = 512
x = torch.randn(2, 128, d_model)  # (batch, seq_len, d_model)

glu_ffn = GLUFFN(d_model)
swiglu_ffn = SwiGLUFFN(d_model)

output1 = glu_ffn(x)
output2 = swiglu_ffn(x)
```

### 推荐论文
1. Dauphin et al. "Language Modeling with Gated Convolutional Networks" (2017) - 原始 GLU
2. Shazeer. "GLU Variants Improve Transformer" (2020)
3. Zoph et al. "Designing Effective Sparse Expert Models" (2022) - SwiGLU 在 PaLM 中的应用