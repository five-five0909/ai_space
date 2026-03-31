# 5. 序列建模架构（替代Transformer）

## RWKV（Receptance Weighted Key Value）

### 这玩意儿到底是啥？
RWKV 是一种用 RNN 的方式来实现 Transformer 的效果，但它不用注意力机制那种 O(N²) 的计算。它把注意力拆成了类似 RNN 的状态更新，所以训练和推理都能线性扩展，特别适合处理超长序列。你可以把它理解成“能记住重要信息的智能滑动窗口”。

### 核心公式
RWKV 的核心是 WKV（Weighted Key Value）计算，它避免了显式的注意力矩阵：

首先，每个 token 会生成 receptance (r), key (k), value (v), time-decay (w)：
- r_t = sigmoid(W_r x_t + U_r s_{t-1})
- k_t = W_k x_t + U_k s_{t-1}
- v_t = W_v x_t + U_v s_{t-1}
- w_t = exp(-exp(W_w x_t + U_w s_{t-1}))  # 确保在 (0,1) 区间

然后状态更新（核心！）：
- u_t = u_{t-1} + exp(k_t)
- v_t' = v_{t-1} + exp(k_t) * v_t

最后输出：
- WKV_t = (u_t * r_t * v_t - v_t') / (u_t * r_t + ε)

这个公式巧妙地把注意力权重和值的加权平均转换成了递推形式，避免了存储整个注意力矩阵。

### 代码示例
```python
import torch
import torch.nn as nn

class RWKV_TimeMix(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        self.receptance = nn.Linear(dim, dim, bias=False)
        self.key = nn.Linear(dim, dim, bias=False)
        self.value = nn.Linear(dim, dim, bias=False)
        self.output = nn.Linear(dim, dim, bias=False)
        self.time_decay = nn.Parameter(torch.ones(dim))
        self.time_first = nn.Parameter(torch.ones(dim))
        
    def forward(self, x):
        B, T, C = x.size()
        xx = torch.concat((torch.zeros(B, 1, C).to(x.device), x[:, :-1]), dim=1)
        xk = x + xx * (1 - torch.pow(0.5, torch.arange(T, dtype=x.dtype, device=x.device).unsqueeze(0).unsqueeze(-1)))
        
        r = torch.sigmoid(self.receptance(x))
        k = self.key(xk)
        v = self.value(xk)
        
        # 简化版 WKV 计算（实际实现更复杂）
        w = torch.exp(-torch.exp(self.time_decay))
        u = torch.exp(self.time_first)
        
        # 初始化状态
        state = torch.zeros(B, C, 3, device=x.device)
        y = torch.zeros_like(v)
        
        for t in range(T):
            kk = k[:, t:t+1]
            vv = v[:, t:t+1]
            
            # 更新状态
            state[:, :, 0] = state[:, :, 0] * w + torch.exp(kk)
            state[:, :, 1] = state[:, :, 1] * w + torch.exp(kk) * vv
            state[:, :, 2] = state[:, :, 2] * u + torch.exp(kk) * vv
            
            # 计算输出
            a = state[:, :, 0]
            b = state[:, :, 1]
            c = state[:, :, 2]
            ww = u + a
            
            y[:, t:t+1] = (b * r[:, t:t+1] - c) / (ww * r[:, t:t+1] + 1e-8)
            
        return self.output(y)
```

### 推荐论文
1. Peng et al. "RWKV: Reinventing RNNs for the Transformer Era" (2023)
2. Peng et al. "Eagle and Finch: RWKV with Matrix-Valued States and Dynamic Recurrence" (2024)
3. Liu et al. "Parallelizing Linear RNNs for Efficient Long-Sequence Modeling" (2024)

## RetNet（Retention Network）

### 这玩意儿到底是啥？
RetNet 是微软搞的一个既能并行训练又能高效推理的模型。它提出了 retention 机制来替代注意力，通过多尺度衰减来捕获不同长度的依赖关系。简单说，就是给不同距离的 token 分配不同的“记忆衰减率”，近的记得清楚，远的记得模糊但不是完全忘记。

### 核心公式
Retention 的核心是多头 retention，每个头有不同的衰减因子 θ：

对于第 h 个头：
- Q_h = XW_Q^h, K_h = XW_K^h, V_h = XW_V^h
- Retention_h(i, j) = Q_h[i]K_h[j]^T * θ_h^{i-j}  (当 i ≥ j)
- Y_h[i] = Σ_{j≤i} Retention_h(i, j)V_h[j]

其中 θ_h ∈ (0,1) 是可学习的衰减因子，不同头有不同的 θ_h 来捕获不同尺度的依赖。

和标准注意力对比：
- Attention: softmax(QK^T/√d)V → 需要 O(N²) 计算和存储
- Retention: Σ Q[i]K[j]^Tθ^{i-j}V[j] → 可以用递推实现 O(N) 推理

### 代码示例
```python
import torch
import torch.nn as nn
import math

class MultiScaleRetention(nn.Module):
    def __init__(self, dim, num_heads):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        
        self.q_proj = nn.Linear(dim, dim, bias=False)
        self.k_proj = nn.Linear(dim, dim, bias=False)
        self.v_proj = nn.Linear(dim, dim, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        
        # 可学习的衰减因子，每个头一个
        self.theta = nn.Parameter(torch.randn(num_heads))
        
    def forward_parallel(self, q, k, v):
        """并行训练模式"""
        B, H, T, D = q.shape
        
        # 计算相对位置衰减矩阵
        decay_mask = torch.triu(torch.ones(T, T, device=q.device), diagonal=0)
        positions = torch.arange(T, device=q.device).unsqueeze(0) - torch.arange(T, device=q.device).unsqueeze(1)
        decay_mask = decay_mask * positions.clamp(min=0)
        
        # 应用衰减
        theta_expanded = self.theta.view(1, H, 1, 1).expand(B, H, T, T)
        decay_weights = torch.pow(theta_expanded, decay_mask.unsqueeze(1))
        
        # 计算 retention
        retention_scores = torch.matmul(q, k.transpose(-2, -1)) * decay_weights
        retention_output = torch.matmul(retention_scores, v)
        
        return retention_output
    
    def forward_recurrent(self, q, k, v, s_n_1):
        """递推推理模式"""
        B, H, D = q.shape
        theta = self.theta.view(1, H, 1)
        
        # 更新状态
        s_n = theta * s_n_1 + torch.matmul(k.unsqueeze(-1), v.unsqueeze(-2))
        
        # 计算输出
        output = torch.matmul(q.unsqueeze(-2), s_n).squeeze(-2)
        
        return output, s_n
    
    def forward(self, x, mode='parallel', past_state=None):
        B, T, D = x.shape
        
        q = self.q_proj(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        
        if mode == 'parallel':
            output = self.forward_parallel(q, k, v)
        else:
            # 递推模式，一次处理一个token
            outputs = []
            s = past_state if past_state is not None else torch.zeros(B, self.num_heads, self.head_dim, self.head_dim, device=x.device)
            for t in range(T):
                out, s = self.forward_recurrent(q[:, :, t], k[:, :, t], v[:, :, t], s)
                outputs.append(out)
            output = torch.stack(outputs, dim=2)
        
        output = output.transpose(1, 2).contiguous().view(B, T, D)
        return self.out_proj(output)
```

### 推荐论文
1. Sun et al. "Retentive Network: A Successor to Transformer for Large Language Models" (2023)
2. Sun et al. "Efficient Streaming Language Models with Retentive Networks" (2023)
3. Zhang et al. "Retention Is All You Need: Rethinking Attention for Efficient LLM Inference" (2024)

## Hyena

### 这玩意儿到底是啥？
Hyena 是斯坦福搞的一个完全不用注意力的模型，它用长卷积来替代注意力机制。核心思想是：注意力本质上就是在做加权求和，而卷积也能做类似的事情。Hyena 用 FFT（快速傅里叶变换）来加速长卷积计算，这样就能高效处理超长序列，而且参数量还比 Transformer 少。

### 核心公式
Hyena 的核心是长卷积层，输入 x 经过三个投影得到 q, k, v，然后进行逐元素乘法和长卷积：

- q = W_q x, k = W_k x, v = W_v x
- y = σ(q ⊙ (k ∗ v))

其中 ∗ 表示卷积操作，⊙ 表示逐元素乘法，σ 是激活函数。

FFT 加速原理：
时域卷积等价于频域乘法：
- k ∗ v = IFFT(FFT(k) ⊙ FFT(v))

这样就把 O(N²) 的卷积计算降到了 O(N log N)。

### 代码示例
```python
import torch
import torch.nn as nn
import torch.fft as fft

class LongConvolution(nn.Module):
    def __init__(self, d_model, l_max):
        super().__init__()
        self.d_model = d_model
        self.l_max = l_max
        
        # 可学习的卷积核（在频域）
        self.filter = nn.Parameter(torch.randn(d_model, l_max // 2 + 1, dtype=torch.cfloat))
        
    def forward(self, x):
        """
        x: (batch, length, d_model)
        """
        B, L, D = x.shape
        
        # FFT of input
        x_f = fft.rfft(x, n=self.l_max, dim=1)  # (B, L//2+1, D)
        
        # Apply filter in frequency domain
        y_f = x_f * self.filter.transpose(0, 1)  # (B, L//2+1, D)
        
        # Inverse FFT
        y = fft.irfft(y_f, n=self.l_max, dim=1)  # (B, L, D)
        
        return y[:, :L, :]  # Truncate to original length

class HyenaOperator(nn.Module):
    def __init__(self, d_model, l_max, num_projections=2):
        super().__init__()
        self.d_model = d_model
        self.l_max = l_max
        self.num_projections = num_projections
        
        # Projection matrices
        self.projections = nn.ModuleList([
            nn.Linear(d_model, d_model, bias=True) for _ in range(num_projections + 1)
        ])
        
        # Long convolution layers
        self.convolutions = nn.ModuleList([
            LongConvolution(d_model, l_max) for _ in range(num_projections)
        ])
        
        self.activation = nn.GELU()
        
    def forward(self, x):
        """
        x: (batch, length, d_model)
        """
        # First projection (for the gating mechanism)
        gates = [proj(x) for proj in self.projections[:-1]]
        
        # Apply convolutions
        conv_outputs = []
        for gate, conv in zip(gates, self.convolutions):
            conv_out = conv(gate)
            conv_outputs.append(conv_out)
            
        # Element-wise multiplication
        y = conv_outputs[0]
        for conv_out in conv_outputs[1:]:
            y = y * conv_out
            
        # Final projection
        y = self.projections[-1](y)
        y = self.activation(y)
        
        return y
```

### 推荐论文
1. Poli et al. "Hyena Hierarchy: Towards Larger Convolutional Language Models" (2023)
2. Dao et al. "Monarch Mixer: Unifying Structured Matrices with Monarch Matrices for Efficient and Effective Large Language Models" (2024)
3. Fu et al. "Accelerating Hyena Operators with Hardware-Aware Algorithm Design" (2024)

## xLSTM (Extended LSTM)

### 这玩意儿到底是啥？
xLSTM 是对传统 LSTM 的大升级，主要加了两个新东西：指数门控（exponential gating）和残差分支。指数门控让模型能更好地处理长期依赖，残差分支让信息流更顺畅。简单说就是“LSTM 2.0”，既保留了 RNN 的序列处理优势，又加入了类似 Transformer 的门控机制。

### 核心公式
xLSTM 有两种变体：sLSTM（scalar）和 mLSTM（matrix）。mLSTM 更强大：

**mLSTM 核心公式：**
- 输入门：i_t = σ(W_i x_t + R_i h_{t-1})
- 遗忘门：f_t = σ(W_f x_t + R_f h_{t-1})
- 输出门：o_t = σ(W_o x_t + R_o h_{t-1})
- **指数门控（关键创新）：**
  - z_t = exp(W_z x_t + R_z h_{t-1})  # 注意这里是 exp 而不是 sigmoid
- 值：v_t = tanh(W_v x_t + R_v h_{t-1})

**状态更新：**
- C_t = f_t ⊙ C_{t-1} + i_t ⊙ z_t ⊙ v_t
- h_t = o_t ⊙ tanh(C_t)

指数门控的好处是能让重要的信息被放大（z_t > 1），不重要的信息被缩小（z_t < 1），比传统的 sigmoid 门控更灵活。

### 代码示例
```python
import torch
import torch.nn as nn

class mLSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # 输入门
        self.W_i = nn.Linear(input_size, hidden_size, bias=True)
        self.R_i = nn.Linear(hidden_size, hidden_size, bias=False)
        
        # 遗忘门
        self.W_f = nn.Linear(input_size, hidden_size, bias=True)
        self.R_f = nn.Linear(hidden_size, hidden_size, bias=False)
        
        # 输出门
        self.W_o = nn.Linear(input_size, hidden_size, bias=True)
        self.R_o = nn.Linear(hidden_size, hidden_size, bias=False)
        
        # 指数门控
        self.W_z = nn.Linear(input_size, hidden_size, bias=True)
        self.R_z = nn.Linear(hidden_size, hidden_size, bias=False)
        
        # 值
        self.W_v = nn.Linear(input_size, hidden_size, bias=True)
        self.R_v = nn.Linear(hidden_size, hidden_size, bias=False)
        
        self.sigmoid = nn.Sigmoid()
        self.tanh = nn.Tanh()
        
    def forward(self, x, hidden):
        h_prev, c_prev = hidden
        
        # 门控计算
        i = self.sigmoid(self.W_i(x) + self.R_i(h_prev))
        f = self.sigmoid(self.W_f(x) + self.R_f(h_prev))
        o = self.sigmoid(self.W_o(x) + self.R_o(h_prev))
        z = torch.exp(self.W_z(x) + self.R_z(h_prev))  # 指数门控！
        v = self.tanh(self.W_v(x) + self.R_v(h_prev))
        
        # 状态更新
        c = f * c_prev + i * z * v
        h = o * self.tanh(c)
        
        return h, (h, c)

class xLSTMBlock(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.mlstm = mLSTMCell(input_size, hidden_size)
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_size, 4 * hidden_size),
            nn.GELU(),
            nn.Linear(4 * hidden_size, hidden_size)
        )
        
    def forward(self, x):
        B, T, D = x.shape
        h = torch.zeros(B, D, device=x.device)
        c = torch.zeros(B, D, device=x.device)
        
        outputs = []
        for t in range(T):
            h, (h, c) = self.mlstm(x[:, t], (h, c))
            outputs.append(h)
            
        h_seq = torch.stack(outputs, dim=1)
        h_seq = self.ln1(h_seq + x)  # 残差连接
        h_seq = self.ln2(h_seq + self.mlp(h_seq))
        
        return h_seq
```

### 推荐论文
1. Beck et al. "xLSTM: Extended Long Short-Term Memory" (2024)
2. Hochreiter & Schmidhuber. "Long Short-Term Memory" (1997) - 原始 LSTM
3. Grefenstette et al. "Learning to Transduce with Unbounded Memory" (2015)

## Griffin

### 这玩意儿到底是啥？
Griffin 是 Google 提出的一个混合架构，结合了 RNN 和线性注意力的优点。它用 block-wise 的设计，每个 block 里包含 Gated Linear Recurrent Unit (GLRU) 和 MLP。GLRU 是简化版的线性注意力，既能并行训练又能高效推理，特别适合在边缘设备上部署。

### 核心公式
Griffin 的核心是 GLRU（Gated Linear Recurrent Unit）：

- z_t = σ(W_z x_t)
- g_t = σ(W_g x_t)
- a_t = -softplus(W_a x_t)  # 确保负值，用于衰减
- h_t = z_t ⊙ h_{t-1} + (1 - z_t) ⊙ g_t ⊙ x_t
- y_t = h_t ⊙ exp(a_t)

这里的关键是 z_t 控制历史信息的保留比例，g_t 控制当前输入的重要性，a_t 控制输出的衰减。

### 代码示例
```python
import torch
import torch.nn as nn

class GLRU(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        
        # 门控参数
        self.W_z = nn.Linear(dim, dim, bias=True)
        self.W_g = nn.Linear(dim, dim, bias=True)
        self.W_a = nn.Linear(dim, dim, bias=True)
        
        self.sigmoid = nn.Sigmoid()
        self.softplus = nn.Softplus()
        
    def forward(self, x):
        B, T, D = x.shape
        
        # 计算门控
        z = self.sigmoid(self.W_z(x))  # 遗忘门
        g = self.sigmoid(self.W_g(x))  # 输入门
        a = -self.softplus(self.W_a(x))  # 衰减因子（负值）
        
        # 递推计算
        h = torch.zeros(B, D, device=x.device)
        outputs = []
        
        for t in range(T):
            # 更新隐藏状态
            h = z[:, t] * h + (1 - z[:, t]) * g[:, t] * x[:, t]
            # 应用衰减
            y = h * torch.exp(a[:, t])
            outputs.append(y)
            
        return torch.stack(outputs, dim=1)

class GriffinBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.glru = GLRU(dim)
        self.ln1 = nn.LayerNorm(dim)
        self.ln2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, 4 * dim),
            nn.GELU(),
            nn.Linear(4 * dim, dim)
        )
        
    def forward(self, x):
        # GLRU 层
        residual = x
        x = self.glru(x)
        x = self.ln1(x + residual)
        
        # MLP 层
        residual = x
        x = self.mlp(x)
        x = self.ln2(x + residual)
        
        return x
```

### 推荐论文
1. Hua et al. "Griffin: Mixing Gated Linear Recurrences with Local and Global Content for Efficient Language Models" (2024)
2. Anonymous. "Efficient Transformers: A Survey" (2023)
3. Dao et al. "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" (2022)

## TTT (Test-Time Training)

### 这玩意儿到底是啥？
TTT 不是一种模型架构，而是一种推理策略。它的核心思想是在推理的时候也更新模型权重，让模型能适应新的输入分布。比如你用一个在英文上训练的模型去处理中文，TTT 会在处理中文的时候微调权重，让它更好地理解中文。这就像考试的时候还能临时抱佛脚！

### 核心公式
TTT 的核心是在推理时进行梯度更新：

给定测试样本 x_test，模型参数 θ：

1. 前向传播：y = f_θ(x_test)
2. 计算自监督损失 L_self(θ, x_test)  # 比如重建损失、对比损失等
3. **推理时更新：** θ' = θ - α ∇_θ L_self(θ, x_test)
4. 用更新后的参数进行最终预测：y_final = f_θ'(x_test)

关键是要设计合适的自监督任务 L_self，让模型能在没有标签的情况下学习。

### 代码示例
```python
import torch
import torch.nn as nn
import torch.optim as optim

class TTTModel(nn.Module):
    def __init__(self, base_model, learning_rate=1e-4):
        super().__init__()
        self.base_model = base_model
        self.learning_rate = learning_rate
        
    def self_supervised_loss(self, x, reconstructed_x):
        """简单的重建损失作为自监督信号"""
        return torch.mean((x - reconstructed_x) ** 2)
    
    def forward(self, x, enable_ttt=True):
        if not enable_ttt:
            return self.base_model(x)
            
        # 保存原始参数
        original_params = {name: param.clone() for name, param in self.base_model.named_parameters()}
        
        # 设置为训练模式以启用梯度
        self.base_model.train()
        for param in self.base_model.parameters():
            param.requires_grad = True
            
        # 前向传播获取重建
        reconstructed_x = self.base_model(x)
        
        # 计算自监督损失
        loss = self.self_supervised_loss(x, reconstructed_x)
        
        # 计算梯度
        grads = torch.autograd.grad(loss, self.base_model.parameters(), create_graph=False)
        
        # 手动更新参数（推理时训练）
        updated_params = {}
        with torch.no_grad():
            for (name, param), grad in zip(self.base_model.named_parameters(), grads):
                updated_params[name] = param - self.learning_rate * grad
                
        # 用更新后的参数进行前向传播
        self.base_model.eval()
        with torch.no_grad():
            # 临时替换参数
            for name, param in self.base_model.named_parameters():
                param.copy_(updated_params[name])
                
            output = self.base_model(x)
            
            # 恢复原始参数
            for name, param in self.base_model.named_parameters():
                param.copy_(original_params[name])
                
        return output
```

### 推荐论文
1. Sun et al. "Test-Time Training with Self-Supervision for Generalization under Distribution Shifts" (2020)
2. Liu et al. "TTT++: Test-Time Training with Self-Supervision for Robustness to Corruptions" (2023)
3. Wang et al. "Test-Time Adaptation for Long-Context Language Models" (2024)

## Titans

### 这玩意儿到底是啥？
Titans 是 Google 提出的一个长期记忆模块，专门用来处理超长上下文（比如几百万 tokens）。它的核心思想是把记忆分成短期记忆和长期记忆，短期记忆用常规的注意力机制，长期记忆用压缩的向量表示。这样既能保持对近期细节的关注，又能记住很久以前的重要信息。

### 核心公式
Titans 的核心是记忆压缩和检索：

**记忆压缩：**
- 对于长期记忆块 M ∈ R^{L×d}，计算压缩表示：
- C = softmax(Q_compress M^T) M
- 其中 Q_compress 是可学习的查询矩阵

**记忆检索：**
- 在注意力计算时，同时考虑短期和长期记忆：
- Attention(Q, K_short, V_short, K_long, V_long) = 
  - softmax(QK_short^T/√d)V_short + λ * softmax(QK_long^T/√d)V_long

其中 λ 是平衡短期和长期记忆的权重。

### 代码示例
```python
import torch
import torch.nn as nn

class TitansMemory(nn.Module):
    def __init__(self, dim, short_context=2048, long_context=1000000, compression_ratio=100):
        super().__init__()
        self.dim = dim
        self.short_context = short_context
        self.long_context = long_context
        self.compression_ratio = compression_ratio
        
        # 压缩查询矩阵
        self.compress_query = nn.Parameter(torch.randn(compression_ratio, dim))
        
        # 长期记忆键值投影
        self.long_k_proj = nn.Linear(dim, dim, bias=False)
        self.long_v_proj = nn.Linear(dim, dim, bias=False)
        
        # 短期记忆投影
        self.short_q_proj = nn.Linear(dim, dim, bias=False)
        self.short_k_proj = nn.Linear(dim, dim, bias=False)
        self.short_v_proj = nn.Linear(dim, dim, bias=False)
        
        self.lambda_param = nn.Parameter(torch.tensor(0.1))  # 长期记忆权重
        
    def compress_memory(self, memory):
        """压缩长期记忆"""
        B, L, D = memory.shape
        
        # 计算压缩注意力
        Q = self.compress_query.unsqueeze(0).expand(B, -1, -1)  # (B, R, D)
        K = memory  # (B, L, D)
        V = memory  # (B, L, D)
        
        attn = torch.softmax(torch.matmul(Q, K.transpose(-2, -1)) / (D ** 0.5), dim=-1)  # (B, R, L)
        compressed = torch.matmul(attn, V)  # (B, R, D)
        
        return compressed
    
    def forward(self, short_input, long_memory=None):
        """
        short_input: (B, T_short, D) - 当前短期输入
        long_memory: (B, T_long, D) - 长期记忆，如果为None则只用短期
        """
        B, T_short, D = short_input.shape
        
        # 短期注意力
        Q_short = self.short_q_proj(short_input)
        K_short = self.short_k_proj(short_input)
        V_short = self.short_v_proj(short_input)
        
        short_attn = torch.softmax(torch.matmul(Q_short, K_short.transpose(-2, -1)) / (D ** 0.5), dim=-1)
        short_output = torch.matmul(short_attn, V_short)
        
        if long_memory is None:
            return short_output
            
        # 压缩长期记忆
        compressed_long = self.compress_memory(long_memory)  # (B, R, D)
        
        # 长期注意力
        K_long = self.long_k_proj(compressed_long)
        V_long = self.long_v_proj(compressed_long)
        
        long_attn = torch.softmax(torch.matmul(Q_short, K_long.transpose(-2, -1)) / (D ** 0.5), dim=-1)
        long_output = torch.matmul(long_attn, V_long)
        
        # 融合短期和长期
        output = short_output + self.lambda_param * long_output
        
        return output
```

### 推荐论文
1. Anonymous. "Titans: Efficient Long-Context Language Models with Hierarchical Memory" (2024)
2. Borgeaud et al. "Improving Language Models by Retrieving from Trillions of Tokens" (2022)
3. Liu et al. "MemGPT: Leveraging Large Language Models as Main Brains for Autonomous Agents" (2023)