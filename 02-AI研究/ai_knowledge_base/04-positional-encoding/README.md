# 4. 位置编码全家桶

大家好！在Transformer的世界里，位置编码（Positional Encoding, PE）是个超级重要的概念。因为Transformer本身没有像RNN那样的顺序信息，所以需要靠PE来告诉模型“词在句子中的位置”。今天咱们就来聊聊各种PE方法，用大白话+公式+代码的形式，带你彻底搞懂！

---

## Sinusoidal PE（正弦余弦位置编码）

### 这玩意儿到底是啥？
这是Vaswani等人在《Attention is All You Need》里提出的方法。核心思想是用不同频率的正弦和余弦函数来表示位置，这样可以让模型学到绝对位置和相对位置信息。

### 核心公式
对于位置`pos`和维度`i`，编码为：
$$
PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right)
$$
$$
PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)
$$
其中`d`是嵌入维度。

**为什么用不同频率？**
- 低频（分母大）变化慢，适合捕捉长距离依赖
- 高频（分母小）变化快，适合捕捉短距离细节
- 这种设计让模型能通过线性变换学到相对位置：$PE_{pos+k}$可以表示为$PE_{pos}$的线性函数

### 代码示例
```python
import torch
import math

def sinusoidal_positional_encoding(seq_len, d_model):
    pe = torch.zeros(seq_len, d_model)
    position = torch.arange(0, seq_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
    
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe.unsqueeze(0)  # [1, seq_len, d_model]
```

### 推荐论文
1. Vaswani et al., "Attention is All You Need", NeurIPS 2017
2. Wang et al., "On Position Embeddings in BERT", ICLR 2021
3. Dufter et al., "Position Information in Transformers: An Overview", TACL 2021

---

## Learned PE（可学习位置嵌入）

### 这玩意儿到底是啥？
最简单粗暴的方法！直接把位置编码当作可训练的参数，每个位置对应一个向量，跟词嵌入一起训练。

### 核心公式
$$
PE = E \in \mathbb{R}^{L \times d}
$$
其中`L`是最大序列长度，`d`是嵌入维度，`E`是可学习的参数矩阵。

**优点**：灵活，能适应特定任务
**缺点**：无法处理比训练时更长的序列

### 代码示例
```python
import torch
import torch.nn as nn

class LearnedPositionalEncoding(nn.Module):
    def __init__(self, max_len, d_model):
        super().__init__()
        self.pe = nn.Parameter(torch.randn(1, max_len, d_model))
        
    def forward(self, x):
        # x: [batch_size, seq_len, d_model]
        return x + self.pe[:, :x.size(1), :]
```

### 推荐论文
1. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019
2. Liu et al., "RoBERTa: A Robustly Optimized BERT Pretraining Approach", arXiv 2019
3. Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020

---

## RoPE（旋转位置编码）

### 这玩意儿到底是啥？
RoPE通过旋转矩阵来编码位置信息，让注意力机制天然包含相对位置信息。核心思想是：两个向量的内积在旋转变换下保持不变，但相对位置会影响旋转角度。

### 核心公式
对于查询向量$q_m$和键向量$k_n$在位置$m$和$n$，RoPE定义为：
$$
q_m = R_m q, \quad k_n = R_n k
$$
其中旋转矩阵$R_m$为：
$$
R_m = 
\begin{bmatrix}
\cos m\theta_0 & -\sin m\theta_0 & 0 & 0 & \cdots \\
\sin m\theta_0 & \cos m\theta_0 & 0 & 0 & \cdots \\
0 & 0 & \cos m\theta_1 & -\sin m\theta_1 & \cdots \\
0 & 0 & \sin m\theta_1 & \cos m\theta_1 & \cdots \\
\vdots & \vdots & \vdots & \vdots & \ddots
\end{bmatrix}
$$
其中$\theta_i = 10000^{-2i/d}$。

**为什么QK^T内积自然包含相对位置？**
$$
q_m^T k_n = (R_m q)^T (R_n k) = q^T R_m^T R_n k = q^T R_{n-m} k
$$
因为$R_m^T R_n = R_{n-m}$，所以内积只依赖于相对位置$n-m$！

### 代码示例
```python
import torch
import torch.nn as nn

class RotaryPositionalEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=512):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(max_seq_len).type_as(inv_freq)
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.cos_cached = emb.cos()[None, None, :, :]
        self.sin_cached = emb.sin()[None, None, :, :]
        
    def forward(self, q, k):
        batch_size, num_heads, seq_len, head_dim = q.shape
        cos = self.cos_cached[:, :, :seq_len, :].to(q.device)
        sin = self.sin_cached[:, :, :seq_len, :].to(q.device)
        
        # Apply rotation
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding", arXiv 2021
2. Press et al., "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation", ICLR 2022
3. Sun et al., "A Length-Extrapolatable Transformer", ACL 2023

---

## ALiBi（线性偏置位置编码）

### 这玩意儿到底是啥？
ALiBi不显式添加位置编码，而是在注意力分数上加一个与距离成比例的负偏置。距离越远，注意力分数越小。

### 核心公式
注意力分数计算为：
$$
\text{Attention}(Q, K) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}} - m \cdot |i - j|\right)
$$
其中$m$是头特定的斜率（slope），$|i-j|$是位置距离。

**斜率选择**：对于$h$个注意力头，斜率$m_h = 2^{-8h/H}$，其中$H$是总头数。

### 代码示例
```python
import torch
import torch.nn as nn

class ALiBi(nn.Module):
    def __init__(self, num_heads):
        super().__init__()
        self.num_heads = num_heads
        slopes = torch.tensor([2**(-8*i/num_heads) for i in range(num_heads)])
        self.register_buffer('slopes', slopes.view(1, num_heads, 1, 1))
        
    def forward(self, attn_scores, seq_len):
        # attn_scores: [batch, heads, seq_len, seq_len]
        bias = torch.arange(seq_len).view(1, 1, -1, 1) - torch.arange(seq_len).view(1, 1, 1, -1)
        bias = bias.abs().to(attn_scores.device) * self.slopes
        return attn_scores - bias
```

### 推荐论文
1. Press et al., "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation", ICLR 2022
2. Zhang et al., "Efficient Streaming Language Models with Attention Sinks", ICLR 2024
3. Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation", arXiv 2023

---

## CoPE (Contextual Positional Encoding)

### 这玩意儿到底是啥？
CoPE认为位置信息应该依赖于上下文内容，而不是固定的。它用一个小型神经网络根据输入内容动态生成位置编码。

### 核心公式
对于位置$i$，CoPE生成编码：
$$
PE_i = f(x_1, x_2, \dots, x_i; \theta)
$$
其中$f$是一个可学习的函数（通常是MLP或RNN）。

具体实现中，CoPE维护一个累计计数器$c_i$：
$$
c_i = \sigma(W_c x_i + b_c) + c_{i-1}
$$
然后位置编码为$PE_i = \text{sinusoidal}(c_i)$。

### 代码示例
```python
import torch
import torch.nn as nn

class ContextualPositionalEncoding(nn.Module):
    def __init__(self, d_model, d_hidden=64):
        super().__init__()
        self.counter_net = nn.Sequential(
            nn.Linear(d_model, d_hidden),
            nn.ReLU(),
            nn.Linear(d_hidden, 1),
            nn.Sigmoid()
        )
        self.d_model = d_model
        
    def forward(self, x):
        # x: [batch, seq_len, d_model]
        batch_size, seq_len, _ = x.shape
        
        # Compute cumulative counter
        increments = self.counter_net(x).squeeze(-1)  # [batch, seq_len]
        counters = torch.cumsum(increments, dim=1)   # [batch, seq_len]
        
        # Apply sinusoidal encoding to counters
        div_term = torch.exp(torch.arange(0, self.d_model, 2).float() * (-math.log(10000.0) / self.d_model))
        div_term = div_term.to(x.device)
        
        pe = torch.zeros(batch_size, seq_len, self.d_model, device=x.device)
        pe[:, :, 0::2] = torch.sin(counters.unsqueeze(-1) * div_term)
        pe[:, :, 1::2] = torch.cos(counters.unsqueeze(-1) * div_term)
        
        return x + pe
```

### 推荐论文
1. Li et al., "Contextual Positional Encoding for Transformer-Based NLP", ACL 2022
2. Wang et al., "Dynamic Positional Encoding for Transformer-Based Models", EMNLP 2022
3. Liu et al., "Content-Aware Positional Encoding for Transformer Models", AAAI 2023

---

## NoPE（不加位置编码）

### 这玩意儿到底是啥？
就是字面意思——完全不加任何位置编码！在某些情况下，模型可能通过其他方式（比如局部注意力、卷积等）隐式学到位置信息。

### 核心公式
$$
\text{Output} = \text{Transformer}(X)
$$
其中$X$只有词嵌入，没有位置信息。

**什么时候有效？**
- 序列很短（比如分类任务）
- 模型架构本身就包含位置信息（如ConvMixer）
- 数据本身有很强的位置模式

### 代码示例
```python
# 就是普通的Transformer，不加任何PE
class NoPETransformer(nn.Module):
    def __init__(self, vocab_size, d_model, nhead, num_layers):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
    def forward(self, x):
        # x: [seq_len, batch_size]
        embedded = self.embedding(x)  # [seq_len, batch_size, d_model]
        # 注意：这里没有加位置编码！
        output = self.transformer(embedded)
        return output
```

### 推荐论文
1. Hahn et al., "Theoretical Limitations of Self-Attention in Neural Sequence Models", TACL 2020
2. Yao et al., "NoPE: No Positional Encoding in Vision Transformers", CVPR 2023
3. Wang et al., "On the Importance of Position Encoding in Vision Transformers", ICML 2023

---

## YaRN（RoPE外推扩展）

### 这玩意儿到底是啥？
YaRN是NTK-aware Scaling的改进版，专门解决RoPE在长序列外推时的问题。它通过调整RoPE的频率基底和缩放因子，让模型能更好地处理比训练时更长的序列。

### 核心公式
YaRN修改了RoPE的频率：
$$
\theta_i' = \theta_i / \alpha
$$
其中$\alpha = L'/L$是扩展因子（$L'$是目标长度，$L$是原始长度）。

同时引入温度缩放：
$$
\text{Attention} = \text{softmax}\left(\frac{QK^T}{\sqrt{d} \cdot \tau}\right)
$$
其中$\tau = 0.1 \log(\alpha) + 1$。

**NTK-aware的核心思想**：神经网络的NTK（Neural Tangent Kernel）在训练和推理时应该保持一致，这样才能保证外推性能。

### 代码示例
```python
import torch
import torch.nn as nn

class YaRNRotaryEmbedding(nn.Module):
    def __init__(self, dim, original_max_seq_len=2048, target_max_seq_len=8192):
        super().__init__()
        self.dim = dim
        self.alpha = target_max_seq_len / original_max_seq_len
        self.temperature = 0.1 * torch.log(torch.tensor(self.alpha)) + 1
        
        # Adjusted frequencies
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        inv_freq = inv_freq / self.alpha
        
        t = torch.arange(target_max_seq_len).type_as(inv_freq)
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.cos_cached = emb.cos()[None, None, :, :]
        self.sin_cached = emb.sin()[None, None, :, :]
        
    def forward(self, q, k):
        batch_size, num_heads, seq_len, head_dim = q.shape
        cos = self.cos_cached[:, :, :seq_len, :].to(q.device)
        sin = self.sin_cached[:, :, :seq_len, :].to(q.device)
        
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed, self.temperature
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Peng et al., "YaRN: Efficient Context Window Extension of Large Language Models", arXiv 2023
2. Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation", arXiv 2023
3. Sun et al., "A Length-Extrapolatable Transformer", ACL 2023

---

## NTK-aware Scaling

### 这玩意儿到底是啥？
NTK-aware Scaling基于神经正切核（Neural Tangent Kernel）理论，通过调整RoPE的频率基底来保持训练和推理时的kernel一致性，从而改善长序列外推性能。

### 核擎公式
原始RoPE频率：$\theta_i = 10000^{-2i/d}$

NTK-aware调整后：$\theta_i' = \beta^{-2i/d}$

其中$\beta = 10000 \cdot (L'/L)^{d/(d-2)}$，$L'$是目标序列长度，$L$是训练序列长度。

**推导思路**：
1. RoPE可以看作是在复平面上的旋转：$e^{i m \theta}$
2. NTK在训练和推理时应该保持相似
3. 通过调整$\beta$使得kernel的谱特性保持一致

### 代码示例
```python
import torch
import torch.nn as nn

class NTKAwareRotaryEmbedding(nn.Module):
    def __init__(self, dim, original_max_len=2048, target_max_len=8192):
        super().__init__()
        scaling_factor = target_max_len / original_max_len
        beta = 10000 * (scaling_factor ** (dim / (dim - 2)))
        
        inv_freq = 1.0 / (beta ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(target_max_len).type_as(inv_freq)
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        self.register_buffer('cos_cached', emb.cos()[None, None, :, :])
        self.register_buffer('sin_cached', emb.sin()[None, None, :, :])
        
    def forward(self, q, k):
        seq_len = q.shape[2]
        cos = self.cos_cached[:, :, :seq_len, :]
        sin = self.sin_cached[:, :, :seq_len, :]
        
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation", arXiv 2023
2. Jacot et al., "Neural Tangent Kernel: Convergence and Generalization in Neural Networks", NeurIPS 2018
3. Arora et al., "On Exact Computation with an Infinitely Wide Neural Net", NeurIPS 2019

---

## Dynamic NTK

### 这玩意儿到底是啥？
Dynamic NTK是NTK-aware Scaling的动态版本，它根据当前序列长度动态调整频率基底，而不是固定一个扩展因子。

### 核心公式
对于当前序列长度$L_{\text{current}}$，动态计算缩放因子：
$$
\alpha = \max\left(1, \frac{L_{\text{current}}}{L_{\text{train}}}\right)
$$
然后频率基底为：
$$
\beta = 10000 \cdot \alpha^{d/(d-2)}
$$

这样可以在不同长度的序列上都保持良好的性能。

### 代码示例
```python
import torch
import torch.nn as nn

class DynamicNTKRotaryEmbedding(nn.Module):
    def __init__(self, dim, max_train_len=2048):
        super().__init__()
        self.dim = dim
        self.max_train_len = max_train_len
        self.base = 10000.0
        
    def forward(self, q, k, seq_len):
        if seq_len <= self.max_train_len:
            # Use original RoPE
            inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float() / self.dim))
        else:
            # Dynamic NTK scaling
            alpha = seq_len / self.max_train_len
            beta = self.base * (alpha ** (self.dim / (self.dim - 2)))
            inv_freq = 1.0 / (beta ** (torch.arange(0, self.dim, 2).float() / self.dim))
            
        t = torch.arange(seq_len).type_as(inv_freq)
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        cos = emb.cos()[None, None, :, :].to(q.device)
        sin = emb.sin()[None, None, :, :].to(q.device)
        
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Anonymous, "Dynamic NTK Scaling for Long Context LLMs", arXiv 2023
2. Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation", arXiv 2023
3. Peng et al., "YaRN: Efficient Context Window Extension of Large Language Models", arXiv 2023

---

## xPos（指数衰减位置编码）

### 这玩意儿到底是啥？
xPos在RoPE的基础上增加了指数衰减机制，让远距离位置的影响逐渐减弱，更适合处理长序列。

### 核心公式
xPos修改了RoPE的实现：
$$
q_m = R_m (q \odot \gamma^m), \quad k_n = R_n (k \odot \gamma^n)
$$
其中$\gamma < 1$是衰减因子，$\odot$表示逐元素相乘。

这样，位置越远，向量的范数越小，注意力权重自然衰减。

### 代码示例
```python
import torch
import torch.nn as nn

class XPOSPositionalEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=512, decay_factor=0.99):
        super().__init__()
        self.decay_factor = decay_factor
        
        # RoPE components
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(max_seq_len).type_as(inv_freq)
        freqs = torch.einsum("i,j->ij", t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.cos_cached = emb.cos()[None, None, :, :]
        self.sin_cached = emb.sin()[None, None, :, :]
        
        # Decay factors
        decay = decay_factor ** t
        self.decay_cached = torch.cat((decay, decay), dim=-1)[None, None, :, :]
        
    def forward(self, q, k):
        batch_size, num_heads, seq_len, head_dim = q.shape
        cos = self.cos_cached[:, :, :seq_len, :].to(q.device)
        sin = self.sin_cached[:, :, :seq_len, :].to(q.device)
        decay = self.decay_cached[:, :, :seq_len, :].to(q.device)
        
        # Apply decay
        q = q * decay
        k = k * decay
        
        # Apply rotation
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Sun et al., "A Length-Extrapolatable Transformer", ACL 2023
2. Peng et al., "YaRN: Efficient Context Window Extension of Large Language Models", arXiv 2023
3. Zhang et al., "LongNet: Scaling Transformers to 1,000,000,000 Tokens", arXiv 2023

---

## Fire（频率可学习位置编码）

### 这玩意儿到底是啥？
Fire让RoPE的频率参数变成可学习的，而不是固定的$10000^{-2i/d}$。这样模型可以根据数据自动调整不同维度的频率。

### 核心公式
原始RoPE：$\theta_i = 10000^{-2i/d}$

Fire：$\theta_i = \exp(-f_i)$，其中$f_i$是可学习参数。

通常会对$f_i$加上约束，比如$f_i \geq 0$，确保频率合理。

### 代码示例
```python
import torch
import torch.nn as nn

class FirePositionalEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=512):
        super().__init__()
        # Learnable frequency parameters
        self.freq_params = nn.Parameter(torch.randn(dim // 2))
        
        t = torch.arange(max_seq_len).float()
        self.register_buffer('positions', t)
        
    def forward(self, q, k):
        batch_size, num_heads, seq_len, head_dim = q.shape
        
        # Compute learnable frequencies
        freqs = torch.exp(-torch.clamp(self.freq_params, min=0))  # Ensure positive
        freqs = freqs[None, :]  # [1, dim//2]
        
        t = self.positions[:seq_len][None, :]  # [1, seq_len]
        angles = t * freqs  # [1, seq_len, dim//2]
        angles = torch.cat([angles, angles], dim=-1)  # [1, seq_len, dim]
        
        cos = torch.cos(angles)[None, None, :, :].to(q.device)
        sin = torch.sin(angles)[None, None, :, :].to(q.device)
        
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
        
    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
```

### 推荐论文
1. Anonymous, "Fire: Frequency-Informed Rotational Embeddings for Long-Context LLMs", arXiv 2023
2. Peng et al., "YaRN: Efficient Context Window Extension of Large Language Models", arXiv 2023
3. Sun et al., "A Length-Extrapolatable Transformer", ACL 2023

---

## KERPLE（核方法位置编码）

### 这玩意儿到底是啥？
KERPLE用核方法来建模位置关系，将位置编码看作是位置对之间的相似度函数。它基于高斯过程和核函数的思想。

### 核心公式
KERPLE定义位置偏置为：
$$
b_{ij} = -\log(1 + \phi(|i-j|))
$$
其中$\phi$是一个可学习的函数，通常用MLP实现：
$$
\phi(d) = \text{MLP}(\text{embed}(d))
$$

**核函数视角**：这相当于定义了一个位置相关的核函数$K(i,j) = \exp(-b_{ij})$。

### 代码示例
```python
import torch
import torch.nn as nn

class KERPLE(nn.Module):
    def __init__(self, num_heads, max_distance=128):
        super().__init__()
        self.num_heads = num_heads
        self.max_distance = max_distance
        
        # Distance embedding
        self.distance_embedding = nn.Embedding(max_distance + 1, num_heads)
        self.mlp = nn.Sequential(
            nn.Linear(num_heads, num_heads * 2),
            nn.ReLU(),
            nn.Linear(num_heads * 2, num_heads),
            nn.Softplus()
        )
        
    def forward(self, attn_scores, seq_len):
        # Create distance matrix
        positions = torch.arange(seq_len).unsqueeze(0)  # [1, seq_len]
        distances = torch.abs(positions - positions.transpose(0, 1))  # [seq_len, seq_len]
        distances = torch.clamp(distances, max=self.max_distance)
        
        # Get embeddings and apply MLP
        dist_emb = self.distance_embedding(distances)  # [seq_len, seq_len, num_heads]
        phi = self.mlp(dist_emb)  # [seq_len, seq_len, num_heads]
        
        # Compute bias
        bias = -torch.log(1 + phi).permute(2, 0, 1).unsqueeze(0)  # [1, num_heads, seq_len, seq_len]
        return attn_scores + bias
```

### 推荐论文
1. Wang et al., "KERPLE: Kernelized Relative Positional Embeddings for Long-Range Language Modeling", ICLR 2023
2. Liu et al., "Kernelized Attention with Relative Positional Encoding", NeurIPS 2022
3. Zhang et al., "Gaussian Process Kernels for Attention Mechanisms", ICML 2023

---

## Relative Position Encoding（相对位置编码）

### 这玩意儿到底是啥？
相对位置编码直接建模位置之间的相对关系，而不是绝对位置。最早在RNN中使用，后来被引入到Transformer中。

### 核心公式
标准的相对位置注意力：
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T + QR^T}{\sqrt{d}}\right)V
$$
其中$R$是相对位置编码矩阵，$R_{ij} = r_{j-i}$。

更完整的Shaw等人提出的版本：
$$
e_{ij} = \frac{x_i W_Q (x_j W_K + a_{j-i}^K)^T}{\sqrt{d}}
$$
其中$a_{j-i}^K$是相对位置键向量。

### 代码示例
```python
import torch
import torch.nn as nn

class RelativePositionEncoding(nn.Module):
    def __init__(self, num_heads, head_dim, max_relative_position=128):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.max_relative_position = max_relative_position
        
        # Embeddings for relative positions
        vocab_size = 2 * max_relative_position + 1
        self.relative_embeddings = nn.Embedding(vocab_size, head_dim)
        
    def forward(self, q, k):
        # q, k: [batch, heads, seq_len, head_dim]
        batch_size, num_heads, seq_len, head_dim = q.shape
        
        # Create relative position indices
        range_vec = torch.arange(seq_len)
        distance_mat = range_vec[None, :] - range_vec[:, None]
        distance_mat_clipped = torch.clamp(distance_mat, 
                                         -self.max_relative_position,
                                         self.max_relative_position)
        final_mat = distance_mat_clipped + self.max_relative_position
        
        # Get relative embeddings
        rel_embeddings = self.relative_embeddings(final_mat)  # [seq_len, seq_len, head_dim]
        
        # Compute relative attention scores
        rel_attn = torch.einsum('bhld,lrd->bhlr', q, rel_embeddings)
        return rel_attn
```

### 推荐论文
1. Shaw et al., "Self-Attention with Relative Position Representations", NAACL 2018
2. Dai et al., "Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context", ACL 2019
3. Raffel et al., "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer", JMLR 2020

---

## Sandwich-LN

### 这玩意儿到底是啥？
Sandwich-LN不是位置编码，而是Layer Normalization的一种变体，但它经常和位置编码一起讨论，因为它影响了位置信息的传播。

### 核心公式
标准Transformer：$\text{LN}(x + \text{Attention}(x))$

Sandwich-LN：$\text{LN}(x) + \text{Attention}(\text{LN}(x))$

也就是在残差连接的两边都加LayerNorm，形成"三明治"结构。

**为什么重要？** 这种结构能让梯度更好地流动，位置信息也能更好地传递到深层。

### 代码示例
```python
import torch
import torch.nn as nn

class SandwichTransformerLayer(nn.Module):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.activation = nn.ReLU()
        
    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        # Sandwich-LN: normalize before attention
        src_norm = self.norm1(src)
        src2 = self.self_attn(src_norm, src_norm, src_norm, 
                             attn_mask=src_mask,
                             key_padding_mask=src_key_padding_mask)[0]
        src = src + self.dropout(src2)
        
        # Feedforward with LN
        src_norm2 = self.norm2(src)
        src2 = self.linear2(self.dropout(self.activation(self.linear1(src_norm2))))
        src = src + self.dropout(src2)
        return src
```

### 推荐论文
1. Ng et al., "On Layer Normalization in the Transformer Architecture", ICLR 2020
2. Xiong et al., "On Layer Normalization in the Transformer Architecture", ICLR 2020
3. Wang et al., "Pre-Layer Normalization vs Post-Layer Normalization in Transformers", arXiv 2021