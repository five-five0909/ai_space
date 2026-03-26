# 3. 注意力机制完整版

> 一句话：注意力就是让模型学会"看哪里"，从O(n²)的全局看到各种稀疏/线性/硬件优化的变体。

---

## Self-Attention

### 这玩意儿到底是啥？

Self-Attention就是**序列内部的相互关注**。每个token都问自己："我应该关注序列中的哪些位置？"

### 核心公式，一步步推导

**输入：** X = [x₁, x₂, ..., xₙ] ∈ ℝ^(n×d)

**1. QKV投影：**
```
Q = XW_Q ∈ ℝ^(n×d_k)
K = XW_K ∈ ℝ^(n×d_k)  
V = XW_V ∈ ℝ^(n×d_v)
```

**2. 计算注意力分数：**
```
A = QK^T ∈ ℝ^(n×n)
```
A[i,j] 表示第i个位置对第j个位置的关注程度

**3. 缩放（关键！）：**
```
A_scaled = A / √d_k
```
**为什么缩放？** 
- Q和K的每个元素假设是独立同分布N(0,1)
- QK^T的每个元素是d_k个随机数的点积
- 方差 = d_k × Var(N(0,1)) = d_k
- 所以除以√d_k让方差变成1
- 不然softmax会饱和（梯度≈0）

**4. Softmax归一化：**
```
P = softmax(A_scaled) ∈ ℝ^(n×n)
```
P[i,:] 是概率分布，∑_j P[i,j] = 1

**5. 加权求和：**
```
Y = PV ∈ ℝ^(n×d_v)
```

**完整公式：**
```
SelfAttention(Q, K, V) = softmax(QK^T / √d_k) V
```

### 复杂度分析

- QK^T: O(n²d_k)
- softmax: O(n²)  
- PV: O(n²d_v)
- 总复杂度: O(n²(d_k + d_v))

**问题：** 序列长度n一长，n²就爆炸了！

### PyTorch实现

```python
import torch
import torch.nn as nn

def scaled_dot_product_attention(q, k, v, mask=None):
    """
    q, k, v: (batch_size, seq_len, d_k)
    mask: (batch_size, 1, seq_len) for causal attention
    """
    d_k = q.size(-1)
    
    # 计算注意力分数
    scores = torch.matmul(q, k.transpose(-2, -1))  # (batch, seq_len, seq_len)
    scores = scores / (d_k ** 0.5)
    
    # 应用mask（比如因果注意力）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # Softmax
    attn_weights = torch.softmax(scores, dim=-1)
    
    # 加权求和
    output = torch.matmul(attn_weights, v)
    return output, attn_weights

class SelfAttention(nn.Module):
    def __init__(self, d_model, d_k, d_v):
        super().__init__()
        self.d_k = d_k
        self.w_q = nn.Linear(d_model, d_k)
        self.w_k = nn.Linear(d_model, d_k)
        self.w_v = nn.Linear(d_model, d_v)
        self.w_o = nn.Linear(d_v, d_model)
    
    def forward(self, x, mask=None):
        q = self.w_q(x)
        k = self.w_k(x)
        v = self.w_v(x)
        
        output, attn_weights = scaled_dot_product_attention(q, k, v, mask)
        output = self.w_o(output)
        return output, attn_weights
```

### 推荐论文

1. **Vaswani, A., et al. (2017).** "Attention Is All You Need." *NeurIPS 2017.*
   - 原始论文，缩放点积注意力的提出

2. **Bahdanau, D., Cho, K., & Bengio, Y. (2015).** "Neural Machine Translation by Jointly Learning to Align and Translate." *ICLR 2015.*
   - 注意力机制的早期工作

3. **Luong, M.-T., Pham, H., & Manning, C. D. (2015).** "Effective Approaches to Attention-based Neural Machine Translation." *EMNLP 2015.*
   - 注意力的另一种形式

---

## Multi-Head Attention (MHA)

### 这玩意儿到底是啥？

MHA就是**多个Self-Attention并行计算**，每个头学习不同的注意力模式，最后拼起来。

### 核心公式

**单头：**
```
head_i = Attention(XW_Q^i, XW_K^i, XW_V^i)
```

**多头拼接：**
```
MultiHead = Concat(head_1, ..., head_h)W_O
```

**维度设置：**
- d_model = 768（总维度）
- h = 12（头数）
- d_k = d_v = d_model / h = 64（每头维度）

**为什么有效？**
- 不同头可以关注不同类型的依赖关系
- 比如：语法头、语义头、位置头、实体头...
- 实验证明多头比单头效果好

### PyTorch实现

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
    
    def split_heads(self, x, batch_size):
        """将输入分成多头"""
        x = x.view(batch_size, -1, self.num_heads, self.d_k)
        return x.transpose(1, 2)  # (batch, num_heads, seq_len, d_k)
    
    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)
        
        # 线性投影
        q = self.w_q(q)  # (batch, seq_len, d_model)
        k = self.w_k(k)
        v = self.w_v(v)
        
        # 分头
        q = self.split_heads(q, batch_size)  # (batch, num_heads, seq_len, d_k)
        k = self.split_heads(k, batch_size)
        v = self.split_heads(v, batch_size)
        
        # 缩放点积注意力
        scaled_attention, attn_weights = scaled_dot_product_attention(q, k, v, mask)
        
        # 合并头: (batch, seq_len, num_heads, d_k)
        scaled_attention = scaled_attention.transpose(1, 2).contiguous()
        scaled_attention = scaled_attention.view(batch_size, -1, self.d_model)
        
        # 输出投影
        output = self.w_o(scaled_attention)
        return output, attn_weights
```

### 推荐论文

1. **Vaswani, A., et al. (2017).** "Attention Is All You Need." *NeurIPS 2017.*
   - MHA原始定义

2. **Voita, E., et al. (2019).** "Analyzing Multi-Head Self-Attention: Specialized Heads Do the Heavy Lifting, the Rest Can Be Pruned." *ACL 2019.*
   - 多头注意力分析

3. **Michel, P., Levy, O., & Neubig, G. (2019).** "Are Sixteen Heads Really Better than One?" *NeurIPS 2019.*
   - 头的重要性分析

---

## Flash Attention

### 这玩意儿到底是啥？

Flash Attention是**IO感知的精确注意力算法**，不改变数学计算，只优化GPU内存访问，速度提升2-4倍，内存节省5-20倍。

### 核心思想：分块计算 + 避免中间存储

**标准注意力的问题：**
- QK^T 需要 O(n²) 内存存储
- GPU HBM（主存）带宽是瓶颈

**Flash Attention的解决方案：**
1. **分块**：把Q、K、V分成小块
2. **SRAM计算**：在片上缓存（SRAM）中计算块内注意力
3. **在线softmax**：逐块计算softmax，不需要全局统计量
4. **重计算**：反向传播时重算前向值，省掉存中间状态

### 数学等价性证明

**标准注意力：**
```
P = softmax(QK^T / √d)
Y = PV
```

**Flash Attention：**
- 分块计算得到相同的P和Y
- 只是计算顺序不同，结果完全一样
- **不是近似算法，是精确算法！**

### 复杂度对比

| 方法 | 时间复杂度 | 内存复杂度 | HBM读写 |
|------|------------|------------|---------|
| 标准 | O(n²d) | O(n² + nd) | O(n²d) |
| Flash | O(n²d) | O(nd) | O(nd) |

**HBM读写减少O(n)倍！**

### PyTorch使用示例

```python
# 安装: pip install flash-attn
from flash_attn import flash_attn_func

# 输入: (batch_size, seqlen, nheads, headdim)
q = torch.randn(2, 1024, 12, 64, device='cuda', dtype=torch.float16)
k = torch.randn(2, 1024, 12, 64, device='cuda', dtype=torch.float16)
v = torch.randn(2, 1024, 12, 64, device='cuda', dtype=torch.float16)

# Flash Attention
output = flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None, causal=False)
```

### 推荐论文

1. **Dao, T., et al. (2022).** "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness." *NeurIPS 2022.*
   - Flash Attention原始论文

2. **Dao, T. (2023).** "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning." *arXiv:2307.08691.*
   - Flash Attention 2

3. **Rabe, M. M., & Staats, C. (2021).** "Self-attention Does Not Need O(n²) Memory." *arXiv:2112.05682.*
   - 内存优化的早期工作

---

## Sparse Attention（稀疏注意力）

### 这玩意儿到底是啥？

稀疏注意力的核心思想是：**不是所有位置都需要两两计算**。通过限制注意力范围，将复杂度从O(n²)降到接近O(n)。

**为什么稀疏注意力有效？**
- 语言有局部性：相邻词关系更紧密
- 远距离依赖往往是稀疏的
- 很多注意力权重本身就很小

### 常见稀疏模式

**1. 滑动窗口注意力（Sliding Window）：**
```
每个token只关注局部窗口内的token
窗口大小w，复杂度O(nw)

示例（w=3）：
位置0: [0, 1, 2]
位置1: [0, 1, 2, 3]
位置2: [0, 1, 2, 3, 4]
位置3: [1, 2, 3, 4, 5]
...
```

**2. 扩张注意力（Dilated Attention）：**
```
类似扩张卷积，间隔采样
窗口内的token不是连续的，而是等间隔的

示例（扩张率=2）：
位置i关注: [i-4, i-2, i, i+2, i+4]
```

**3. 全局注意力（Global Attention）：**
```
少数"全局token"可以看到所有位置
其他token只能看到局部

比如：[CLS]、句号等作为全局token
```

**4. 随机注意力（Random Attention）：**
```
每个位置随机采样若干个位置
数学上可以证明覆盖所有位置的概率很高
```

### Longformer

Longformer结合了**滑动窗口**和**全局注意力**：

```python
import torch
import torch.nn as nn

class LongformerAttention(nn.Module):
    def __init__(self, d_model, num_heads, window_size=512):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.window_size = window_size

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, x, global_mask=None):
        """
        x: (batch, seq_len, d_model)
        global_mask: (batch, seq_len) - True表示全局注意力位置
        """
        batch_size, seq_len, _ = x.shape

        q = self.w_q(x).view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)
        k = self.w_k(x).view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)
        v = self.w_v(x).view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)

        # 创建滑动窗口mask
        mask = torch.zeros(seq_len, seq_len, device=x.device)
        for i in range(seq_len):
            start = max(0, i - self.window_size // 2)
            end = min(seq_len, i + self.window_size // 2 + 1)
            mask[i, start:end] = 1

        # 添加全局注意力
        if global_mask is not None:
            global_positions = global_mask.nonzero(as_tuple=True)[1]
            mask[global_positions, :] = 1
            mask[:, global_positions] = 1

        # 计算注意力
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_model ** 0.5)
        scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = torch.softmax(scores, dim=-1)

        output = torch.matmul(attn, v)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.w_o(output)
```

### BigBird

BigBird结合了**随机注意力 + 滑动窗口 + 全局注意力**：

```
BigBird注意力模式：
1. 随机注意力：每个位置随机关注r个位置
2. 滑动窗口：每个位置关注局部w个邻居
3. 全局注意力：g个全局token可以看到所有位置

总复杂度：O(n(r + w + g)) = O(n)
```

### 推荐论文

1. **Beltagy et al., 2020** - "Longformer: The Long-Document Transformer" - Longformer
2. **Zaheer et al., 2020** - "Big Bird: Transformers for Longer Sequences" - BigBird
3. **Child et al., 2019** - "Generating Long Sequences with Sparse Transformers" - Sparse Transformer

---

## Linear Attention（线性注意力）

### 这玩意儿到底是啥？

线性注意力通过**改变计算顺序**，将复杂度从O(n²)降到O(n)。核心技巧是利用**矩阵结合律**：

```
标准注意力：softmax(QK^T)V
计算顺序：(QK^T) → softmax → 乘V
复杂度：O(n²d)

线性注意力：Q(K^T V)
计算顺序：K^T V → 乘Q
复杂度：O(nd²)
```

当n >> d时，线性注意力更快！

### 核心公式推导

**标准注意力：**
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) V
$$

**线性注意力：**

用核函数$\phi$替代softmax：
$$
\text{LinearAttn}(Q, K, V) = \frac{\phi(Q)(\phi(K)^T V)}{\phi(Q)\phi(K)^T \mathbf{1}}
$$

其中$\phi$常用：
- ReLU
- ELU + 1
- softmax逐行

**关键洞察：**
$$
\phi(Q)(\phi(K)^T V) = \sum_{j=1}^{n} \phi(q_i) \cdot (\phi(k_j)^T v_j)
$$

可以**递推计算**，不需要存储整个注意力矩阵！

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class LinearAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, q, k, v):
        batch_size, seq_len, _ = q.shape

        q = self.w_q(q).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        k = self.w_k(k).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        v = self.w_v(v).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

        # 应用核函数（这里用ELU+1）
        q = F.elu(q) + 1
        k = F.elu(k) + 1

        # 计算分子: Q @ (K^T @ V)
        kv = torch.einsum('bhnd,bhne->bhde', k, v)  # (batch, heads, d_k, d_k)
        q_kv = torch.einsum('bhnd,bhde->bhne', q, kv)  # (batch, heads, seq_len, d_k)

        # 计算分母: Q @ (K^T @ 1)
        k_sum = k.sum(dim=2, keepdim=True)  # (batch, heads, 1, d_k)
        q_k_sum = torch.einsum('bhnd,bhkd->bhnk', q, k_sum)  # (batch, heads, seq_len, 1)

        # 归一化
        output = q_kv / (q_k_sum + 1e-6)

        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.w_o(output)

class PerformerAttention(nn.Module):
    """Performer: 使用随机特征近似softmax"""
    def __init__(self, d_model, num_heads, num_features=256):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_features = num_features
        self.d_k = d_model // num_heads

        # 随机特征投影矩阵
        self.projection_matrix = nn.Parameter(
            torch.randn(num_features, self.d_k) / (self.d_k ** 0.5),
            requires_grad=False
        )

    def kernel(self, x):
        """随机特征近似softmax核"""
        projection = torch.einsum('bhnd,fd->bhnf', x, self.projection_matrix)
        return torch.exp(projection - projection.max(dim=-1, keepdim=True).values)

    def forward(self, q, k, v):
        batch_size, seq_len, _ = q.shape

        q = q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

        # 应用随机特征核
        q_prime = self.kernel(q)
        k_prime = self.kernel(k)

        # 线性注意力计算
        kv = torch.einsum('bhnf,bhne->bhfe', k_prime, v)
        output = torch.einsum('bhnf,bhfe->bhne', q_prime, kv)

        # 归一化
        normalizer = torch.einsum('bhnf,bhnf->bhn', q_prime, k_prime.sum(dim=2))
        output = output / (normalizer.unsqueeze(-1) + 1e-6)

        return output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
```

### 推荐论文

1. **Katharopoulos et al., 2020** - "Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention" - 线性注意力
2. **Choromanski et al., 2021** - "Rethinking Attention with Performers" - Performer
3. **Shen et al., 2021** - "Efficient Attention: Attention with Linear Complexities" - 高效注意力

---

## Multi-Query Attention (MQA) & Grouped Query Attention (GQA)

### 这玩意儿到底是啥？

MQA和GQA是**减少KV Cache**的注意力变体。标准MHA每个头都有独立的K和V，而MQA所有头共享一组K和V，GQA则将头分组共享。

**为什么这很重要？**
- 推理时KV Cache占用大量显存
- MQA可以减少KV Cache到原来的1/num_heads
- 几乎不影响模型质量

### 对比

| 方法 | Q头数 | K头数 | V头数 | KV Cache | 质量 |
|------|-------|-------|-------|----------|------|
| MHA | h | h | h | 100% | 基准 |
| MQA | h | 1 | 1 | 1/h | 略降 |
| GQA | h | g | g | g/h | 接近MHA |

### 核心公式

**MHA：**
$$
\text{head}_i = \text{Attention}(QW_Q^i, KW_K^i, VW_V^i)
$$

**MQA：**
$$
\text{head}_i = \text{Attention}(QW_Q^i, KW_K, VW_V)
$$

所有头共享同一个K和V投影！

**GQA：**
$$
\text{head}_{i} = \text{Attention}(QW_Q^i, KW_K^{i // (h/g)}, VW_V^{i // (h/g)})
$$

g个组，每组h/g个头共享一组KV。

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiQueryAttention(nn.Module):
    """Multi-Query Attention: 所有头共享一组KV"""
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # Q每个头独立
        self.w_q = nn.Linear(d_model, d_model)
        # K和V只有一组（d_k维度，不是d_model）
        self.w_k = nn.Linear(d_model, self.d_k)
        self.w_v = nn.Linear(d_model, self.d_k)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape

        # Q: (batch, num_heads, seq_len, d_k)
        q = self.w_q(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        # K, V: (batch, 1, seq_len, d_k) -> 广播到所有头
        k = self.w_k(x).unsqueeze(1)  # (batch, 1, seq_len, d_k)
        v = self.w_v(x).unsqueeze(1)

        # 注意力计算
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        output = torch.matmul(attn, v)

        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.w_o(output)

class GroupedQueryAttention(nn.Module):
    """Grouped Query Attention: 分组共享KV"""
    def __init__(self, d_model, num_heads, num_kv_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads  # KV头数（组数）
        self.d_k = d_model // num_heads
        self.heads_per_group = num_heads // num_kv_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, num_kv_heads * self.d_k)
        self.w_v = nn.Linear(d_model, num_kv_heads * self.d_k)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape

        # Q: (batch, num_heads, seq_len, d_k)
        q = self.w_q(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        # K, V: (batch, num_kv_heads, seq_len, d_k)
        k = self.w_k(x).view(batch_size, seq_len, self.num_kv_heads, self.d_k).transpose(1, 2)
        v = self.w_v(x).view(batch_size, seq_len, self.num_kv_heads, self.d_k).transpose(1, 2)

        # 扩展KV到匹配Q的头数
        # (batch, num_kv_heads, seq_len, d_k) -> (batch, num_heads, seq_len, d_k)
        k = k.repeat_interleave(self.heads_per_group, dim=1)
        v = v.repeat_interleave(self.heads_per_group, dim=1)

        # 注意力计算
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        output = torch.matmul(attn, v)

        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.w_o(output)

# 使用示例
mqa = MultiQueryAttention(d_model=768, num_heads=12)
gqa = GroupedQueryAttention(d_model=768, num_heads=12, num_kv_heads=4)

x = torch.randn(2, 512, 768)
output_mqa = mqa(x)
output_gqa = gqa(x)

print(f"MQA output: {output_mqa.shape}")
print(f"GQA output: {output_gqa.shape}")
```

### 推荐论文

1. **Shazeer, 2019** - "Fast Transformer Decoding: One Write-Head is All You Need" - MQA原论文
2. **Ainslie et al., 2023** - "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints" - GQA
3. **Pope et al., 2022** - "Efficiently Scaling Transformer Inference" - 推理优化

---

## Sliding Window Attention

### 这玩意儿到底是啥？

滑动窗口注意力让每个位置只关注**固定窗口大小**内的邻居，复杂度从O(n²)降到O(nw)，其中w是窗口大小。

**Mistral的滑动窗口注意力：**
- 窗口大小w = 4096
- 每个token只看前面4096个token
- 通过多层堆叠扩大有效感受野

**感受野扩展：**
```
层1：窗口w，感受野w
层2：窗口w，感受野2w
层3：窗口w，感受野3w
...

实际有效感受野 = 层数 × 窗口大小
```

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SlidingWindowAttention(nn.Module):
    def __init__(self, d_model, num_heads, window_size):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.window_size = window_size
        self.d_k = d_model // num_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, x):
        batch_size, seq_len, _ = x.shape

        q = self.w_q(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        k = self.w_k(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        v = self.w_v(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

        # 创建滑动窗口mask
        mask = torch.ones(seq_len, seq_len, device=x.device).triu(1)
        mask = mask + torch.ones(seq_len, seq_len, device=x.device).tril(-self.window_size - 1)
        mask = mask == 0  # True表示可以attend

        # 计算注意力
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)
        scores = scores.masked_fill(~mask, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        output = torch.matmul(attn, v)

        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.w_o(output)
```

### 推荐论文

1. **Jiang et al., 2023** - "Mistral 7B" - Mistral的滑动窗口注意力
2. **Dai et al., 2019** - "Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context" - 长上下文
3. **Press et al., 2022** - "Train Short, Test Long" - ALiBi

---

## 总结

### 注意力变体对比

| 方法 | 时间复杂度 | 内存复杂度 | 适用场景 |
|------|------------|------------|----------|
| 标准MHA | O(n²d) | O(n² + nd) | 短序列 |
| Flash Attention | O(n²d) | O(nd) | 通用 |
| Sparse Attention | O(nwd) | O(nw) | 长文档 |
| Linear Attention | O(nd²) | O(nd) | 超长序列 |
| MQA/GQA | O(n²d/h) | O(nd/h) | 推理优化 |
| Sliding Window | O(nwd) | O(nw) | 长序列 |

### 选择建议

```
序列长度 < 4K → Flash Attention
序列长度 4K-32K → Longformer/BigBird
序列长度 > 32K → Linear Attention
推理优化 → MQA/GQA
需要精确注意力 → Flash Attention
可以接受近似 → Sparse/Linear
```

---

> 注意力机制是Transformer的核心！从标准MHA到Flash Attention，从稀疏到线性，从MHA到MQA/GQA，每种变体都有其适用场景。理解这些变体，才能为你的任务选择最合适的注意力！