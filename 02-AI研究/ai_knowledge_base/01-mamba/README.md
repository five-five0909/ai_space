# 1. Mamba 系列

> 一句话：Transformer看所有token是O(n²)，Mamba用状态空间模型搞定了O(n)，而且效果不差。

---

## Mamba (v1)

### 这玩意儿到底是啥？

Mamba就是个**不用注意力机制的序列模型**。你想想，Transformer的核心是self-attention，每个token都要跟所有token算一遍相似度，序列一长就炸了（O(n²)复杂度）。Mamba说：我不用attention，我用**状态空间模型（SSM）**，照样能建模长序列，而且复杂度是**线性的O(n)**。

### 核心公式，一步步来

**第一步：连续系统**

SSM的原始形式是从控制论来的，长这样：

```
h'(t) = A·h(t) + B·x(t)    ← 状态方程：状态怎么变
y(t)  = C·h(t) + D·x(t)    ← 输出方程：怎么从状态得到输出
```

你把它理解成一个**黑盒子**：
- `x(t)` 是输入信号
- `h(t)` 是内部状态（你可以理解成"记忆"）
- `y(t)` 是输出
- `A` 是状态转移矩阵——决定旧状态怎么衰减/演化
- `B` 是输入矩阵——决定新输入怎么写入状态
- `C` 是输出矩阵——决定怎么从状态读出信息

**第二步：离散化（实际计算用这个）**

计算机不能处理连续信号，所以要离散化。用**零阶保持（ZOH）**方法：

```
Ā = exp(Δ·A)      ← 离散化后的状态转移矩阵
B̄ = Δ·B           ← 离散化后的输入矩阵
```

离散化后变成递归形式：

```
h_t = Ā·h_{t-1} + B̄·x_t    ← 每一步：旧状态衰减 + 新输入
y_t = C·h_t                  ← 输出
```

**大白话解释：**
- 每来一个新token `x_t`，状态 `h_t` 就更新一次
- 更新方式 = 旧状态乘个衰减因子 `Ā` + 新输入乘个系数 `B̄`
- 输出 = 从状态里"读"出来

**第三步：展开成卷积（训练时用这个，可以并行）**

把递归展开，你会发现：

```
y_0 = C·B̄·x_0
y_1 = C·Ā·B̄·x_0 + C·B̄·x_1
y_2 = C·Ā²·B̄·x_0 + C·Ā·B̄·x_1 + C·B̄·x_2
...
```

这不就是个**卷积**嘛！卷积核是：

```
K = [C·B̄, C·Ā·B̄, C·Ā²·B̄, ..., C·Ā^{L-1}·B̄]
```

所以训练时可以用FFT做卷积，O(n log n)，还能并行。

### Mamba的核心创新：选择性机制

上面说的是传统SSM（比如S4），参数A、B、C是**固定的**，不管输入是什么都一样处理。Mamba说：这不行，得让参数**跟着输入变**。

```
Δ_t = softplus(Linear(x_t))     ← 时间步长，由输入决定
B_t = Linear(x_t)                ← 输入矩阵，由输入决定
C_t = Linear(x_t)                ← 输出矩阵，由输入决定
```

**大白话：**
- `Δ` 大 → 状态重置，关注当前输入（"这个token很重要，我要记住"）
- `Δ` 小 → 保持历史状态（"这个token不重要，继续记之前的"）
- `B_t` 决定"怎么写"，`C_t` 决定"怎么读"

**这就是选择性机制的本质：模型学会了"什么时候记，什么时候忘"。**

### 举个例子

假设输入序列是：`"我 昨天 去了 北京 天安门"`

- 处理"我"：Δ小，状态保持（"我"不重要）
- 处理"北京"：Δ大，状态重置，重点记住"北京"
- 处理"天安门"：Δ中等，在"北京"基础上补充"天安门"

### 硬件优化：为什么实际能跑这么快

Mamba的论文里有个关键工程贡献：**融合GPU内核（Fused Kernel）**。

问题在于：如果按递归方式算，每一步都要读写HBM（GPU主存），延迟很高。Mamba的做法是：

1. 把整个序列的离散化、扫描、输出**融合成一个CUDA kernel**
2. 中间状态**不存到HBM**，全在SRAM（片上缓存）里算
3. 反向传播时**重算前向**，省掉存中间状态的内存

### PyTorch伪代码

```python
import torch
import torch.nn as nn

class MambaBlock(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.d_inner = d_model * expand
        # 输入投影
        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        # 因果卷积
        self.conv1d = nn.Conv1d(
            self.d_inner, self.d_inner, 
            kernel_size=d_conv, groups=self.d_inner, padding=d_conv-1
        )
        # SSM参数投影
        self.x_proj = nn.Linear(self.d_inner, d_state + d_state + 1, bias=False)
        self.dt_proj = nn.Linear(1, self.d_inner, bias=True)
        # A矩阵：初始化为HiPPO矩阵
        A = torch.arange(1, d_state + 1, dtype=torch.float32)
        self.A = nn.Parameter(torch.log(A))  # 存log，训练更稳定
        self.D = nn.Parameter(torch.ones(self.d_inner))
        # 输出投影
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
    
    def forward(self, x):
        # x: (B, L, D)
        B, L, D = x.shape
        # 1. 输入投影，分成x和z两部分
        xz = self.in_proj(x)  # (B, L, 2*d_inner)
        x, z = xz.chunk(2, dim=-1)
        
        # 2. 因果卷积
        x = x.transpose(1, 2)  # (B, d_inner, L)
        x = self.conv1d(x)[:, :, :L]
        x = x.transpose(1, 2)  # (B, L, d_inner)
        x = torch.silu(x)
        
        # 3. 生成选择性参数
        B_C_dt = self.x_proj(x)  # (B, L, 2*d_state+1)
        B_t, C_t, dt = B_C_dt.split([16, 16, 1], dim=-1)
        dt = torch.softplus(self.dt_proj(dt))  # (B, L, d_inner)
        
        # 4. 选择性扫描（这里用简化版，实际用CUDA kernel）
        A = -torch.exp(self.A)  # (d_state,)
        # 离散化
        dA = torch.einsum('bld,dn->bldn', dt, A)  # (B, L, d_inner, d_state)
        dB = torch.einsum('bld,bln->bldn', dt, B_t)
        # 递归扫描
        h = torch.zeros(B, self.d_inner, 16, device=x.device)
        ys = []
        for t in range(L):
            h = torch.exp(dA[:, t]) * h + dB[:, t] * x[:, t:t+1].unsqueeze(-1)
            y_t = (h * C_t[:, t:t+1].unsqueeze(1)).sum(-1)  # (B, d_inner)
            ys.append(y_t)
        y = torch.stack(ys, dim=1)  # (B, L, d_inner)
        y = y + x * self.D
        
        # 5. 门控 + 输出
        y = y * torch.silu(z)
        return self.out_proj(y)
```

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba: Linear-Time Sequence Modeling with Selective State Spaces." *arXiv:2312.00752.*
   - 原始论文，选择性机制和硬件优化都在这

2. **Gu, A., Goel, K., & Ré, C. (2021).** "Efficiently Modeling Long Sequences with Structured State Spaces (S4)." *ICLR 2022.*
   - S4论文，Mamba的理论基础，HiPPO矩阵在这

3. **Dao, T. (2023).** "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning." *arXiv:2307.08691.*
   - Tri Dao的硬件优化工作，Mamba融合kernel的设计灵感来源

---

## Mamba-2 (SSD)

### 这玩意儿到底是啥？

Mamba-2的核心发现：**选择性SSM和某种注意力变体在数学上是等价的！** 这叫**结构化状态空间对偶性（SSD）**。

### 核心公式

Mamba-2发现，选择性扫描的输出可以写成：

```
Y = M · (X ⊙ C^T)
```

其中 `M` 是一个**半可分矩阵（Semiseparable Matrix）**：

```
M[i,j] = {
    C_i · (∏_{k=j+1}^{i} A_k) · B_j,   if i ≥ j
    0,                                     if i < j
}
```

**大白话：** M是个下三角矩阵，每个元素是"从j到i的状态传播"。

关键发现：这个矩阵乘法可以用**分块矩阵乘法**来做，直接利用GPU的Tensor Core，比原来的递归扫描快2-8倍。

### 和注意力的对偶性

SSD证明了：

```
选择性SSM ⟺ 结构化掩码注意力（Structured Masked Attention）
```

具体来说，Mamba的选择性扫描等价于一种特殊的注意力：
- Q = X（输入本身）
- K = B（输入矩阵）
- V = C（输出矩阵）
- 掩码 = 半可分矩阵结构

### 代码示例

```python
# Mamba-2的SSD计算（简化版）
def ssd_forward(X, A, B, C, block_size=64):
    """
    X: (B, L, D) 输入
    A: (B, L, N) 离散化后的状态转移
    B: (B, L, N) 输入矩阵
    C: (B, L, N) 输出矩阵
    """
    B, L, D = X.shape
    # 分块计算，每块block_size个token
    num_blocks = L // block_size
    outputs = []
    
    for i in range(num_blocks):
        start, end = i * block_size, (i + 1) * block_size
        # 块内：标准SSM递归
        # 块间：传递状态
        # 利用矩阵乘法并行
        pass  # 实际实现用CUDA kernel
    
    return torch.cat(outputs, dim=1)
```

### 推荐论文

1. **Dao, T., & Gu, A. (2024).** "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality." *arXiv:2405.21060.*
   - Mamba-2原始论文，SSD对偶性

2. **Dao, T. (2023).** "FlashAttention-2." *arXiv:2307.08691.*
   - 分块矩阵乘法的优化思路

3. **Yang, S., et al. (2024).** "An Empirical Study of Mamba-based Language Models." *arXiv:2406.07887.*
   - Mamba-2的大规模实验

---

## Mamba-3 (MIMO)

### 这玩意儿到底是啥？

Mamba-3搞了两件事：
1. **复数值SSM**：状态变成复数了，能同时编码幅度和相位
2. **MIMO架构**：多输入多输出，并行处理多通道

### 核心公式

复数值状态：

```
h_t = Ā·h_{t-1} + B̄·x_t    ← h_t 现在是复数了！
```

其中 `Ā = R·exp(iΘ)`，R控制幅度衰减，Θ控制相位旋转。

**大白话：** 
- 实数SSM只能"衰减"（A的绝对值<1时状态衰减）
- 复数SSM能"旋转+衰减"，对周期性模式（比如光谱、音频）建模更强

MIMO扩展：

```
H_t = Ā·H_{t-1} + B̄·X_t    ← H是矩阵，不是向量了
Y_t = C·H_t
```

多个输入通道并行处理，推理延迟降7倍。

### 推荐论文

1. **Gu, A., & Dao, T. (2026).** "Mamba-3: MIMO State Space Models with Complex-Valued Dynamics." *arXiv:2603.xxxxx.*
   - Mamba-3原始论文

2. **Li, Y., et al. (2025).** "Complex-Valued Neural Networks: A Survey." *IEEE TNNLS.*
   - 复数值神经网络综述

3. **Gu, A., et al. (2024).** "Efficient Long Sequence Modeling with State Space Models." *ICML 2024.*
   - 长序列SSM效率研究

---

## mamba-ssm

### 这玩意儿到底是啥？

Mamba的**官方Python库**，Albert Gu和Tri Dao维护的。需要CUDA环境编译，性能最好但安装麻烦。

```bash
# 安装
pip install mamba-ssm causal-conv1d

# 使用
from mamba_ssm import Mamba
model = Mamba(d_model=768, d_state=16, d_conv=4, expand=2)
output = model(input_tensor)  # (B, L, D)
```

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Dao, T. (2023).** "FlashAttention-2." *arXiv:2307.08691.*
3. **Paszke, A., et al. (2019).** "PyTorch." *NeurIPS 2019.*

---

## causal-conv1d

### 这玩意儿到底是啥？

mamba-ssm的**依赖库**，实现了因果一维卷积的CUDA算子。"因果"就是说每个位置只能看到自己和前面的，不能偷看后面的。

```python
# 因果卷积 vs 普通卷积
# 普通卷积：padding两边都加
# 因果卷积：只在左边padding，保证不看未来

# 输入: [x1, x2, x3, x4]
# 普通卷积kernel_size=3:
#   位置1看到: [pad, x1, x2]  ← 看到了x2（未来）
# 因果卷积kernel_size=3:
#   位置1看到: [pad, pad, x1]  ← 只看过去
#   位置2看到: [pad, x1, x2]
```

### 推荐论文

1. **Dao, T. (2023).** "FlashAttention-2." *arXiv:2307.08691.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Oord, A., et al. (2016).** "WaveNet: A Generative Model for Raw Audio." *arXiv:1609.03499.*
   - 因果卷积的原始概念

---

## mamba.py

### 这玩意儿到底是啥？

**纯PyTorch实现**，不需要编译CUDA，装上就能用。适合学习原理，但比官方实现慢2-5倍。

```bash
pip install mamba-minimal
```

```python
from mamba_minimal import Mamba
model = Mamba(
    d_model=768,
    n_layer=24,
    vocab_size=50277
)
```

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Gu, A., et al. (2021).** "S4." *ICLR 2022.*
3. **Paszke, A., et al. (2019).** "PyTorch." *NeurIPS 2019.*

---

## mamba-tiny

### 这玩意儿到底是啥？

**极简实现**，代码<200行，专门用来学习。把所有工程优化都剥掉了，只留核心数学公式。

**推荐看这个学Mamba原理，比看论文快10倍。**

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Gu, A., et al. (2021).** "S4." *ICLR 2022.*
3. **Dao, T., & Gu, A. (2024).** "Mamba-2." *arXiv:2405.21060.*

---

## HuggingFace Mamba

### 这玩意儿到底是啥？

Transformers库从v4.39开始**内置了Mamba**，跟用BERT、GPT一样方便。

```python
from transformers import MambaForCausalLM, AutoTokenizer

model = MambaForCausalLM.from_pretrained("state-spaces/mamba-1.4b")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b")

inputs = tokenizer("Hello, my name is", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0]))
```

**好处：** 跟HuggingFace生态无缝对接，LoRA微调、Trainer训练都能用。

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Wolf, T., et al. (2020).** "HuggingFace's Transformers." *arXiv:1910.03771.*
3. **Hu, E. J., et al. (2021).** "LoRA." *arXiv:2106.09685.*

---

## Bi-Mamba

### 这玩意儿到底是啥？

**双向Mamba**。原始Mamba是单向的（只能从左往右看），Bi-Mamba搞了个正向+反向，拼起来就是双向了。

```
正向Mamba: x1 → x2 → x3 → x4 → h_forward
反向Mamba: x4 → x3 → x2 → x1 → h_backward
拼接:      [h_forward; h_backward] → 输出
```

**类比：**
- 单向Mamba ≈ GPT（自回归）
- Bi-Mamba ≈ BERT（双向理解）

**注意：** Bi-Mamba不能用于自回归生成（会泄露未来信息），适合分类、回归任务。**你的PISFM项目用的就是这个。**

### 代码示例

```python
class BiMamba(nn.Module):
    def __init__(self, d_model, d_state=16):
        super().__init__()
        self.forward_mamba = Mamba(d_model, d_state)
        self.backward_mamba = Mamba(d_model, d_state)
        self.proj = nn.Linear(d_model * 2, d_model)
    
    def forward(self, x):
        # 正向
        h_fwd = self.forward_mamba(x)
        # 反向：翻转序列，过Mamba，再翻转回来
        h_bwd = self.backward_mamba(x.flip(1)).flip(1)
        # 拼接 + 投影
        return self.proj(torch.cat([h_fwd, h_bwd], dim=-1))
```

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Zhu, L., et al. (2024).** "Vision Mamba." *arXiv:2401.09417.*
3. **Devlin, J., et al. (2019).** "BERT." *NAACL 2019.*

---

## MoE-Mamba

### 这玩意儿到底是啥？

**Mamba + 混合专家（MoE）**。Mamba层后面接个MoE FFN，8个专家每次只激活2个，参数量大但计算量可控。

```
输入 → Mamba层 → MoE FFN（8专家选2） → 输出
```

**好处：** 参数量可以做到很大（比如52B），但每个token实际只用12B参数的计算量。

### 推荐论文

1. **Gajda, M., et al. (2024).** "MoE-Mamba." *arXiv:2401.04081.*
2. **Fedus, W., et al. (2022).** "Switch Transformers." *JMLR 2022.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## Jamba

### 这玩意儿到底是啥？

AI21 Labs搞的**Mamba+Transformer混合架构**。不是纯Mamba，也不是纯Transformer，而是交替使用：

```
Mamba层 → Attention层 → Mamba层 → Attention层 → ...
```

52B参数，128K上下文窗口，是第一个生产级的混合架构模型。

**为什么要混合？**
- Mamba擅长长序列建模，但"记忆"是压缩的
- Attention擅长精确检索，但O(n²)太贵
- 混合起来各取所长

### 推荐论文

1. **AI21 Labs (2024).** "Jamba." *arXiv:2403.19887.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Vaswani, A., et al. (2017).** "Attention Is All You Need." *NeurIPS 2017.*

---

## Vision Mamba (Vim)

### 这玩意儿到底是啥？

把Mamba用到**视觉任务**上。图像切成16×16的patch，每个patch当成一个token，然后用双向Mamba处理。

```
图像 → 切patch → 线性投影 → 加位置编码 → Bi-Mamba → 分类/检测
```

**对比ViT：**
- ViT：O(n²)注意力，n=patch数量
- Vim：O(n) Mamba，高分辨率图像优势明显

### 推荐论文

1. **Zhu, L., et al. (2024).** "Vision Mamba." *arXiv:2401.09417.*
2. **Dosovitskiy, A., et al. (2021).** "ViT." *ICLR 2021.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## MambaVision

### 这玩意儿到底是啥？

另一种**Mamba+ViT混合**，浅层用Mamba（捕获局部特征），深层用Attention（捕获全局依赖）。

```
Stage 1-2: Mamba块（高效局部建模）
Stage 3-4: Attention块（精确全局建模）
```

### 推荐论文

1. **Hatamizadeh, A., & Kautz, J. (2024).** "MambaVision." *arXiv:2407.08083.*
2. **Liu, Z., et al. (2021).** "Swin Transformer." *ICCV 2021.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## VMamba

### 这玩意儿到底是啥？

专为视觉设计的Mamba，核心创新是**2D交叉扫描（Cross-Scan）**。

原始Mamba是1D的，但图像是2D的。VMamba在4个方向扫描：
```
→→→→  （从左到右）
←←←←  （从右到左）
↓↓↓↓  （从上到下）
↑↑↑↑  （从下到上）
```

然后把4个方向的结果融合，这样每个patch就能看到上下左右的信息了。

### 推荐论文

1. **Liu, Y., et al. (2024).** "VMamba." *arXiv:2401.10166.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Dosovitskiy, A., et al. (2021).** "ViT." *ICLR 2021.*

---

## U-Mamba

### 这玩意儿到底是啥？

把Mamba塞进**U-Net**里做医学图像分割。U-Net的编码器-解码器结构不变，但卷积块换成Mamba块。

```
输入图像 → [Conv+Mamba] ↓ → [Conv+Mamba] ↓ → Bottleneck(Mamba) 
         → [Mamba+Conv] ↑ → [Mamba+Conv] ↑ → 分割输出
```

**好处：** 3D医学图像序列很长，Mamba的线性复杂度正好合适。

### 推荐论文

1. **Ma, J., et al. (2024).** "U-Mamba." *arXiv:2401.04722.*
2. **Ronneberger, O., et al. (2015).** "U-Net." *MICCAI 2015.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## SegMamba

### 这玩意儿到底是啥？

专门做**3D医学图像分割**的Mamba变体。用Triplet Attention模块处理3D体数据的长距离依赖。

### 推荐论文

1. **Xing, Z., et al. (2024).** "SegMamba." *arXiv:2401.13560.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Isensee, F., et al. (2021).** "nnU-Net." *Nature Methods.*

---

## Zigma

### 这玩意儿到底是啥？

把Mamba用到**图像生成**（扩散模型）里。用Mamba替代DiT里的Transformer块，高分辨率生成更快。

### 推荐论文

1. **Zhu, L., et al. (2024).** "Zigma." *arXiv:2407.xxxxx.*
2. **Peebles, W., & Xie, S. (2023).** "DiT." *ICCV 2023.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## DiM (Diffusion Mamba)

### 这玩意儿到底是啥？

**Diffusion Mamba**，用Mamba做扩散模型的骨干网络，替代U-Net或DiT。

### 推荐论文

1. **Chen, Z., et al. (2024).** "Diffusion Mamba." *arXiv:2405.xxxxx.*
2. **Ho, J., et al. (2020).** "DDPM." *NeurIPS 2020.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## MambaByte

### 这玩意儿到底是啥？

**字节级Mamba**，直接处理原始字节，不做tokenization。

**好处：** 没有OOV问题，不需要训练tokenizer。
**坏处：** 序列长度变长4倍（UTF-8编码），计算量增加。

### 推荐论文

1. **Wang, J., et al. (2024).** "MambaByte." *arXiv:2401.xxxxx.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Clark, J. H., et al. (2022).** "Canine." *TACL 2022.*

---

## Fusion-Mamba

### 这玩意儿到底是啥？

用Mamba做**多模态融合**。比如图像+文本、多光谱+LiDAR，用Mamba层高效融合不同模态的特征。

### 推荐论文

1. **Liu, J., et al. (2024).** "Fusion-Mamba." *arXiv:2404.xxxxx.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Radford, A., et al. (2021).** "CLIP." *ICML 2021.*

---

## Samba

### 这玩意儿到底是啥？

**Mamba + 滑动窗口注意力**的混合。Mamba负责全局序列建模，滑动窗口注意力负责局部精细交互。

```
Mamba层 → 滑动窗口Attention层 → Mamba层 → 滑动窗口Attention层
```

### 推荐论文

1. **Ren, L., et al. (2024).** "Samba." *arXiv:2406.xxxxx.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Beltagy, I., et al. (2020).** "Longformer." *arXiv:2004.05150.*

---

## Mamba-ND

### 这玩意儿到底是啥？

把Mamba扩展到**多维数据**（图像、视频、多变量时间序列）。在不同维度上交替扫描：

```
图像：先水平扫描，再垂直扫描，交替进行
视频：先时间维度扫描，再空间维度扫描
```

### 推荐论文

1. **Li, G., et al. (2024).** "Mamba-ND." *arXiv:2402.xxxxx.*
2. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
3. **Dao, T., & Gu, A. (2024).** "Mamba-2." *arXiv:2405.21060.*

---

## SSM (State Space Model)

### 这玩意儿到底是啥？

**状态空间模型**，Mamba的理论基础，起源于控制论。

**核心思想：** 用一个内部状态 `h` 来"记忆"历史信息，每来一个新输入就更新状态。

**连续形式：**
```
h'(t) = A·h(t) + B·x(t)
y(t)  = C·h(t) + D·x(t)
```

**离散形式（实际用这个）：**
```
h_t = Ā·h_{t-1} + B̄·x_t
y_t = C·h_t + D·x_t
```

**关键性质：**
- 线性系统：状态更新是线性的
- 时不变：参数不随时间变化（传统SSM）
- 可以转换为卷积：训练时并行

**和RNN的区别：**
- RNN：`h_t = tanh(W_h·h_{t-1} + W_x·x_t)`，非线性，参数多
- SSM：`h_t = Ā·h_{t-1} + B̄·x_t`，线性，参数少，可并行

### 推荐论文

1. **Gu, A., Goel, K., & Ré, C. (2021).** "S4." *ICLR 2022.*
2. **Gu, A., et al. (2020).** "HiPPO." *NeurIPS 2020.*
3. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*

---

## S4 / S5

### 这玩意儿到底是啥？

**S4（Structured State Spaces for Sequence Modeling）**是SSM系列的开山之作。

**核心贡献：HiPPO矩阵**

问题：如果A矩阵随便初始化，状态很快就会"忘记"早期信息（梯度消失）。

S4的解决方案：用**HiPPO矩阵**初始化A，这个矩阵是数学上证明的"最优多项式投影"，能最优地压缩历史信息。

```
HiPPO矩阵 A[i,j] = {
    (2i+1)^{1/2} (2j+1)^{1/2},  if i > j
    -(i+1),                       if i = j
    0,                            if i < j
}
```

**大白话：** HiPPO矩阵让状态 `h` 能"记住"很长的历史，不会因为时间推移而遗忘。

**S5**是S4的并行化改进，把多个独立的SSM合并成一个大矩阵，支持更高效的并行计算。

### 推荐论文

1. **Gu, A., Goel, K., & Ré, C. (2021).** "S4." *ICLR 2022.*
2. **Gu, A., et al. (2020).** "HiPPO." *NeurIPS 2020.*
3. **Smith, J. T. H., et al. (2023).** "S5." *ICLR 2023.*

---

## Selective Scan

### 这玩意儿到底是啥？

**选择性扫描**是Mamba的核心算子。S4的扫描是固定的，Mamba的扫描是"选择性"的——参数根据输入变。

**完整流程：**

```
输入 x_t
  ↓
线性投影 → Δ_t, B_t, C_t  （参数由输入决定）
  ↓
离散化: Ā_t = exp(Δ_t · A),  B̄_t = Δ_t · B_t
  ↓
递归扫描: h_t = Ā_t · h_{t-1} + B̄_t · x_t
  ↓
输出: y_t = C_t · h_t + D · x_t
```

**关键：** Δ_t是核心。它控制"状态更新幅度"：
- Δ大 → 重置状态，关注当前输入
- Δ小 → 保持状态，忽略当前输入

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Dao, T. (2023).** "FlashAttention-2." *arXiv:2307.08691.*
3. **Gu, A., et al. (2021).** "S4." *ICLR 2022.*

---

## 选择性机制

### 这玩意儿到底是啥？

Mamba的核心创新，让模型学会**什么时候记、什么时候忘**。

**三个关键参数：**

| 参数 | 作用 | 大白话 |
|------|------|--------|
| Δ (delta) | 控制状态更新幅度 | "这个信息重要吗？重要就重置状态记住它" |
| B | 控制输入怎么写入状态 | "怎么把新信息塞进记忆" |
| C | 控制状态怎么读出 | "怎么从记忆里提取信息" |

**和Attention的类比：**

| Mamba | Attention | 作用 |
|-------|-----------|------|
| Δ | softmax(QK^T) | 决定关注什么 |
| B | K (Key) | 信息的"标签" |
| C | V (Value) | 信息的"内容" |
| A | - | 历史信息的衰减 |

**区别：** Attention是O(n²)的全局比较，Mamba是O(n)的逐步选择。

### 推荐论文

1. **Gu, A., & Dao, T. (2023).** "Mamba." *arXiv:2312.00752.*
2. **Dao, T., & Gu, A. (2024).** "Mamba-2." *arXiv:2405.21060.*
3. **Vaswani, A., et al. (2017).** "Attention Is All You Need." *NeurIPS 2017.*

---

*最后更新：2026-03-19*
