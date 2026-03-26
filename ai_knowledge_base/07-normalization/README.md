# 7. 归一化方法

> 嘿，师弟师妹们！今天咱们来聊聊深度学习里的"归一化"（Normalization）。这个东西说白了就是让数据的分布更"规整"，训练起来更快更稳定。你想想，如果一批数据的范围忽大忽小，梯度也会忽大忽小，模型就很难学好。归一化就是为了解决这个问题。

## 7.1 Batch Normalization (BN)

### 直觉理解

Batch Normalization，简称BN，是2015年由Google的大佬们提出来的。它的核心思想很简单：**对于一个batch的数据，在同一个特征维度上，把它们变成均值为0、方差为1的分布**。

想象一下，你有一批学生的考试成绩，有语文、数学、英语三门课。BN的做法是：
- 语文成绩：算这批学生语文成绩的均值和方差，然后标准化
- 数学成绩：算这批学生数学成绩的均值和方差，然后标准化
- 英语成绩：算这批学生英语成绩的均值和方差，然后标准化

### 核心公式推导

假设我们有一个mini-batch的数据 $\mathcal{B} = \{x_1, x_2, ..., x_m\}$，BN的计算过程如下：

**Step 1: 计算mini-batch的均值**

$$\mu_\mathcal{B} = \frac{1}{m} \sum_{i=1}^{m} x_i$$

这个很简单，就是把batch里所有样本在同一特征维度上的值加起来求平均。

**Step 2: 计算mini-batch的方差**

$$\sigma^2_\mathcal{B} = \frac{1}{m} \sum_{i=1}^{m} (x_i - \mu_\mathcal{B})^2$$

就是每个值减去均值，平方，再求平均。

**Step 3: 归一化**

$$\hat{x}_i = \frac{x_i - \mu_\mathcal{B}}{\sqrt{\sigma^2_\mathcal{B} + \epsilon}}$$

这里 $\epsilon$ 是一个小常数（比如 $10^{-5}$），防止除以零。

**Step 4: 缩放和偏移（Scale and Shift）**

$$y_i = \gamma \hat{x}_i + \beta$$

为什么要这一步？因为如果只是简单地把数据变成标准正态分布，可能会丢失一些有用的特征表达能力。$\gamma$ 和 $\beta$ 是可学习的参数，让网络自己决定要不要"还原"回去。

### 均值方差在哪维算？

这是个很重要的问题！BN是在**batch维度**上算均值和方差的。

对于一个4D张量（batch, channels, height, width）：
- 均值和方差是在 (batch, height, width) 这三个维度上算的
- 每个channel有自己独立的 $\gamma$ 和 $\beta$

简单说就是：**同一个channel，不同样本不同位置，算一个均值和方差**。

### 为什么推理时用滑动平均？

训练时我们有batch，可以算均值和方差。但是推理时可能一次只来一个样本，batch_size=1，那均值和方差就没什么意义了。

BN的做法是：训练时维护一个**全局均值和全局方差**的滑动平均（running mean and running var）：

$$\mu_{running} = (1 - \alpha) \cdot \mu_{running} + \alpha \cdot \mu_\mathcal{B}$$
$$\sigma^2_{running} = (1 - \alpha) \cdot \sigma^2_{running} + \alpha \cdot \sigma^2_\mathcal{B}$$

其中 $\alpha$ 是动量参数（通常取0.1或0.01）。推理时直接用这个滑动平均值，保证结果的确定性。

### PyTorch代码示例

```python
import torch
import torch.nn as nn

# BN在PyTorch中的使用
# 对于2D输入 (batch, features)
bn_2d = nn.BatchNorm1d(num_features=64)

# 对于3D输入 (batch, channels, length) - 时序数据
bn_3d = nn.BatchNorm1d(num_features=128)

# 对于4D输入 (batch, channels, height, width) - 图像数据
bn_4d = nn.BatchNorm2d(num_features=64)

# 实际使用示例
x = torch.randn(32, 64, 28, 28)  # batch=32, channels=64, h=w=28
bn_layer = nn.BatchNorm2d(64)
y = bn_layer(x)

# 查看BN层的参数
print(f"gamma (weight): {bn_layer.weight.shape}")  # [64]
print(f"beta (bias): {bn_layer.bias.shape}")       # [64]
print(f"running_mean: {bn_layer.running_mean.shape}")  # [64]
print(f"running_var: {bn_layer.running_var.shape}")    # [64]
```

### 推荐论文

1. **Ioffe & Szegedy, 2015** - "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift" - 这是BN的开山之作，必读！
2. **Santurkar et al., 2018** - "How Does Batch Normalization Help Optimization?" - 分析BN为什么有效，认为不是减少ICS，而是让loss landscape更平滑
3. **Bjorck et al., 2018** - "Understanding Batch Normalization" - 深入分析BN对训练动态的影响

---

## 7.2 Layer Normalization (LN)

### 直觉理解

Layer Normalization，简称LN，是2016年提出的。它和BN的区别在于：**BN是在batch维度上做归一化，LN是在特征维度上做归一化**。

还是用学生考试的例子：
- BN：算每个科目所有学生的平均分，然后标准化
- LN：算每个学生所有科目的平均分，然后标准化

LN不依赖batch size，所以特别适合：
- RNN/Transformer这种变长序列模型
- batch size很小的场景
- 推理时batch size可能变化的场景

### 核心公式推导

假设一个样本的特征向量是 $x = (x_1, x_2, ..., x_H)$，其中 $H$ 是特征维度。

**Step 1: 计算特征维度的均值**

$$\mu = \frac{1}{H} \sum_{i=1}^{H} x_i$$

**Step 2: 计算特征维度的方差**

$$\sigma^2 = \frac{1}{H} \sum_{i=1}^{H} (x_i - \mu)^2$$

**Step 3: 归一化**

$$\hat{x}_i = \frac{x_i - \mu}{\sqrt{\sigma^2 + \epsilon}}$$

**Step 4: 缩放和偏移**

$$y_i = \gamma \hat{x}_i + \beta$$

公式看起来和BN一样，区别在于**在哪里算均值和方差**！

### 为什么Transformer用LN不用BN？

这是个经典问题，原因有几个：

1. **序列长度变化**：NLP任务中每个句子长度不同，BN要对齐位置来算均值方差，这很别扭。LN对每个token单独归一化，不受序列长度影响。

2. **batch size问题**：训练大模型时batch size往往很小（受显存限制），BN在小batch上统计不准。LN不依赖batch size。

3. **推理一致性**：BN推理时用滑动平均，和训练时行为不一致。LN训练和推理时行为完全一样。

4. **自注意力机制**：Transformer的自注意力机制会让不同位置的信息混合，LN在特征维度上归一化更符合这种架构的特点。

### PyTorch代码示例

```python
import torch
import torch.nn as nn

# LN的参数是normalized_shape，即要归一化的特征维度
# 对于 (batch, seq_len, d_model) 的Transformer输入
ln_layer = nn.LayerNorm(normalized_shape=512)  # d_model=512

# 实际使用示例
x = torch.randn(32, 100, 512)  # batch=32, seq_len=100, d_model=512
y = ln_layer(x)

# LN对每个token的512维特征做归一化
# 所以输出的每个位置的均值≈0，方差≈1
print(f"Input shape: {x.shape}")
print(f"Output shape: {y.shape}")

# 验证归一化效果
print(f"Mean of first token after LN: {y[0, 0, :].mean():.6f}")  # ≈0
print(f"Var of first token after LN: {y[0, 0, :].var():.6f}")    # ≈1

# 多维情况：对最后两个维度归一化
ln_2d = nn.LayerNorm(normalized_shape=[64, 64])
x_4d = torch.randn(8, 3, 64, 64)
y_4d = ln_2d(x_4d)
```

### 推荐论文

1. **Ba et al., 2016** - "Layer Normalization" - LN的原始论文
2. **Xiong et al., 2020** - "On Layer Normalization in the Transformer Architecture" - 深入分析Pre-LN和Post-LN
3. **Nguyen & Salazar, 2019** - "Transformers without Tears: Improving the Normalization of Self-Attention" - 分析为什么LN适合Transformer

---

## 7.3 RMSNorm

### 直觉理解

RMSNorm（Root Mean Square Normalization）是2019年提出的，它是LN的一个简化版。**核心思想：去掉均值中心化那一步，只做方差归一化**。

为什么要简化？因为作者发现，中心化（减均值）这一步对模型性能影响不大，去掉可以加速计算。RMSNorm只保留"缩放"操作。

很多现代LLM都用RMSNorm，比如LLaMA、GPT-NeoX等。

### 核心公式推导

**LN的公式（回顾）：**
$$y_i = \frac{x_i - \mu}{\sqrt{\sigma^2 + \epsilon}} \cdot \gamma_i$$

**RMSNorm的公式：**
$$y_i = \frac{x_i}{\text{RMS}(x)} \cdot \gamma_i$$

其中 RMS（Root Mean Square）的定义是：

$$\text{RMS}(x) = \sqrt{\frac{1}{H} \sum_{i=1}^{H} x_i^2 + \epsilon}$$

注意区别：
- LN：减去均值，除以标准差
- RMSNorm：不减均值，除以RMS（均方根）

展开看：
$$y_i = \frac{x_i}{\sqrt{\frac{1}{H} \sum_{j=1}^{H} x_j^2 + \epsilon}} \cdot \gamma_i$$

**为什么这样能work？**

直觉上理解：RMS衡量的是向量的"大小"或"能量"。除以RMS相当于把向量归一化到一个"单位球"附近（但不严格），保持了方向信息，去掉了大小信息。这样不同样本的特征就处于相似的尺度上了。

而且，去掉中心化还有一个好处：**保留了特征的符号信息和相对大小关系**。某些情况下这可能更有用。

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# PyTorch 2.0+ 已经内置了RMSNorm
# 如果你的版本较老，可以自己实现

class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-8):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d_model))
    
    def forward(self, x):
        # 计算RMS: root mean square
        rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
        # 归一化并缩放
        return x / rms * self.weight

# 使用示例
rms_norm = RMSNorm(d_model=512)

x = torch.randn(32, 100, 512)
y = rms_norm(x)

print(f"Input shape: {x.shape}")
print(f"Output shape: {y.shape}")

# 验证：RMS of output ≈ 1（乘以weight之前）
rms_output = torch.sqrt(torch.mean((x / torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + 1e-8)) ** 2, dim=-1))
print(f"RMS before scaling: {rms_output[0, 0]:.6f}")  # ≈1

# PyTorch 2.0+ 内置版本
rms_norm_builtin = nn.RMSNorm(512)
y_builtin = rms_norm_builtin(x)
```

### 推荐论文

1. **Zhang & Sennrich, 2019** - "Root Mean Square Layer Normalization" - RMSNorm原始论文
2. **Touvron et al., 2023** - "LLaMA: Open and Efficient Foundation Language Models" - LLaMA使用RMSNorm
3. **Su et al., 2021** - "RoFormer: Enhanced Transformer with Rotary Position Embedding" - 也使用RMSNorm

---

## 7.4 Group Normalization (GN)

### 直觉理解

Group Normalization，简称GN，是2018年何恺明大神提出的。它的思想是：**把channels分成若干组，在每组内做归一化**。

为什么需要GN？因为BN有个致命问题：**依赖batch size**。当batch size很小时（比如目标检测任务，一张图就很大了，batch只能塞1-2张），BN的效果就不好了。GN不依赖batch size，可以解决这个问题。

直观理解：
- BN：同一个channel，所有样本，做归一化
- LN：同一个样本，所有channel，做归一化  
- GN：同一个样本，同一组channel，做归一化

### 核心公式推导

假设输入是 $(N, C, H, W)$，我们把 $C$ 个channels分成 $G$ 组，每组有 $C/G$ 个channels。

**Step 1: 对每组内的元素计算均值**

$$\mu_{ng} = \frac{1}{(C/G) \cdot H \cdot W} \sum_{c=g \cdot (C/G)}^{(g+1) \cdot (C/G)} \sum_{h=1}^{H} \sum_{w=1}^{W} x_{nchw}$$

其中 $n$ 是样本索引，$g$ 是组索引。

**Step 2: 对每组内的元素计算方差**

$$\sigma^2_{ng} = \frac{1}{(C/G) \cdot H \cdot W} \sum_{c=g \cdot (C/G)}^{(g+1) \cdot (C/G)} \sum_{h=1}^{H} \sum_{w=1}^{W} (x_{nchw} - \mu_{ng})^2$$

**Step 3: 归一化**

$$\hat{x}_{nchw} = \frac{x_{nchw} - \mu_{ng}}{\sqrt{\sigma^2_{ng} + \epsilon}}$$

**Step 4: 缩放和偏移**

每个channel有自己独立的 $\gamma_c$ 和 $\beta_c$：
$$y_{nchw} = \gamma_c \cdot \hat{x}_{nchw} + \beta_c$$

### 几种归一化的对比

| 方法 | 归一化维度 | 计算量 | 适用场景 |
|------|-----------|--------|----------|
| BN | (N, H, W) per C | 小 | CNN，大batch |
| LN | (C, H, W) per N | 中 | Transformer |
| GN | (C/G, H, W) per N | 中 | CNN，小batch |
| IN | (H, W) per N, C | 小 | 风格迁移 |

### PyTorch代码示例

```python
import torch
import torch.nn as nn

# GN的参数是num_groups
# 要求 channels % num_groups == 0
# 常见设置：num_groups=32

# 假设64个channels，分成32组，每组2个channels
gn_layer = nn.GroupNorm(num_groups=32, num_channels=64)

x = torch.randn(4, 64, 28, 28)  # batch=4, channels=64, h=w=28
y = gn_layer(x)

print(f"Input shape: {x.shape}")
print(f"Output shape: {y.shape}")

# 验证：每组内的归一化效果
# 取第一个样本，第一组（channel 0和1）
group0 = y[0, 0:2, :, :]
print(f"Group 0 mean: {group0.mean():.6f}")  # ≈0
print(f"Group 0 var: {group0.var():.6f}")    # ≈1

# 不同的分组方式
# 8 groups, 每组8个channels
gn_8groups = nn.GroupNorm(num_groups=8, num_channels=64)
y_8 = gn_8groups(x)

# 1 group = Layer Norm
gn_1group = nn.GroupNorm(num_groups=1, num_channels=64)
y_ln = gn_1group(x)  # 等价于LN

# C groups = Instance Norm  
gn_cgroups = nn.GroupNorm(num_groups=64, num_channels=64)
y_in = gn_cgroups(x)  # 等价于IN
```

### 推荐论文

1. **Wu & He, 2018** - "Group Normalization" - GN原始论文，何恺明出品
2. **Wu et al., 2018** - "Rethinking "Batch" in BatchNorm" - 讨论BN在小batch下的问题
3. **Kolesnikov et al., 2020** - "Big Transfer (BiT): General Visual Representation Learning" - 在大规模视觉模型中使用GN

---

## 7.5 Instance Normalization (IN)

### 直觉理解

Instance Normalization，简称IN，主要用于图像生成任务（比如风格迁移）。它的思想更极端：**每个样本的每个channel单独做归一化**。

直觉上理解：IN想做的是去掉每个样本的"风格信息"（均值和方差），只保留"内容信息"。在风格迁移中，风格往往体现在图像的整体色调和对比度上，这些正好被均值和方差捕捉了。

### 核心公式推导

假设输入是 $(N, C, H, W)$，对每个样本 $n$ 和每个channel $c$：

**Step 1: 计算该样本该channel的均值**

$$\mu_{nc} = \frac{1}{H \cdot W} \sum_{h=1}^{H} \sum_{w=1}^{W} x_{nchw}$$

**Step 2: 计算方差**

$$\sigma^2_{nc} = \frac{1}{H \cdot W} \sum_{h=1}^{H} \sum_{w=1}^{W} (x_{nchw} - \mu_{nc})^2$$

**Step 3: 归一化**

$$\hat{x}_{nchw} = \frac{x_{nchw} - \mu_{nc}}{\sqrt{\sigma^2_{nc} + \epsilon}}$$

**Step 4: 缩放和偏移**

$$y_{nchw} = \gamma_c \cdot \hat{x}_{nchw} + \beta_c$$

可以看到，IN是最"细粒度"的归一化，只在空间维度 $(H, W)$ 上计算。

### PyTorch代码示例

```python
import torch
import torch.nn as nn

# IN的参数是num_features（即channels数）
# 可选参数affine=True/False，是否学习gamma和beta
in_layer = nn.InstanceNorm2d(num_features=64, affine=True)

x = torch.randn(4, 64, 28, 28)
y = in_layer(x)

print(f"Input shape: {x.shape}")
print(f"Output shape: {y.shape}")

# 验证：第一个样本，第一个channel
channel0 = y[0, 0, :, :]
print(f"Channel 0 mean: {channel0.mean():.6f}")  # ≈0
print(f"Channel 0 var: {channel0.var():.6f}")    # ≈1

# 风格迁移中的典型用法
# IN可以去掉风格信息，保留内容信息
# 配合AdaIN（Adaptive Instance Norm）可以注入目标风格
class AdaIN(nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(self, content, style_mean, style_std):
        # 对content做IN归一化
        mean = content.mean(dim=[2, 3], keepdim=True)
        std = content.std(dim=[2, 3], keepdim=True) + 1e-5
        normalized = (content - mean) / std
        # 用目标风格的均值和方差重新缩放
        return normalized * style_std + style_mean
```

### 推荐论文

1. **Ulyanov et al., 2016** - "Instance Normalization: The Missing Ingredient for Fast Stylization" - IN原始论文
2. **Huang & Belongie, 2017** - "Arbitrary Style Transfer in Real-time with Adaptive Instance Normalization" - AdaIN论文
3. **Karras et al., 2019** - "A Style-Based Generator Architecture for GANs" - StyleGAN使用IN变体

---

## 7.6 Weight Normalization (WN)

### 直觉理解

前面的归一化方法都是对**激活值**（activations）做归一化。Weight Normalization有点不一样，它是对**权重**做归一化！

核心思想：把权重向量 $w$ 分解成**方向**和**大小**两个部分：
$$w = \frac{g}{||v||} \cdot v$$

其中 $v$ 是方向（可学习），$g$ 是大小（可学习标量）。

这样做的好处：
1. 优化更简单，loss landscape更平滑
2. 不依赖batch统计量，推理和训练一致
3. 计算开销小

### 核心公式推导

原始权重 $w$ 用两个参数表示：
- $v$：和 $w$ 同维度的向量，控制方向
- $g$：标量，控制大小

**前向传播公式：**
$$w = \frac{g}{||v||} \cdot v$$

其中 $||v|| = \sqrt{\sum_{i} v_i^2}$ 是 $v$ 的L2范数。

**梯度推导：**

对 $v$ 的梯度：
$$\nabla_v L = \frac{g}{||v||} \left( \nabla_w L - \frac{w \cdot \nabla_w L}{||w||^2} w \right)$$

对 $g$ 的梯度：
$$\nabla_g L = \frac{w \cdot \nabla_w L}{||w||}$$

这个梯度公式看起来复杂，但实际实现时可以用自动微分搞定。

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class WeightNorm(nn.Module):
    """自己实现的Weight Normalization"""
    def __init__(self, module, name='weight'):
        super().__init__()
        self.module = module
        self.name = name
        
        # 获取原始权重
        weight = getattr(module, name)
        
        # 分解成 g 和 v
        self.g = nn.Parameter(torch.norm(weight, dim=1, keepdim=True).detach())
        self.v = nn.Parameter(weight.detach())
        
        # 删除原始权重
        delattr(module, name)
        
    def forward(self, x):
        # 计算归一化后的权重
        norm_v = torch.norm(self.v, dim=1, keepdim=True)
        weight = self.g * self.v / norm_v
        # 应用到模块
        return F.linear(x, weight, self.module.bias)

# PyTorch内置的WeightNorm
linear = nn.Linear(512, 256)
wn_linear = nn.utils.weight_norm(linear, name='weight', dim=0)

# 使用
x = torch.randn(32, 512)
y = wn_linear(x)
print(f"Output shape: {y.shape}")

# 查看分解后的参数
print(f"g (weight_g): {wn_linear.weight_g.shape}")  # [256, 1]
print(f"v (weight_v): {wn_linear.weight_v.shape}")  # [256, 512]

# 移除weight norm
nn.utils.remove_weight_norm(wn_linear)
```

### 推荐论文

1. **Salimans & Kingma, 2016** - "Weight Normalization: A Simple Reparameterization to Accelerate Training of Deep Neural Networks" - WN原始论文
2. **Hoffer et al., 2018** - "Norm matters: efficient and accurate normalization schemes in deep networks" - 比较各种归一化
3. **Gitman & Ginsburg, 2017** - "Comparison of Batch Normalization and Weight Normalization in the Fully-Connected Setting" - BN vs WN的比较

---

## 7.7 Pre-LN vs Post-LN

### 直觉理解

在Transformer中，Layer Normalization的位置很重要！有两种常见配置：

**Post-LN（原始Transformer的做法）：**
```
x → Attention → Add & LN → FFN → Add & LN
```

**Pre-LN（现代LLM的做法）：**
```
x → LN → Attention → Add → LN → FFN → Add
```

区别在于：LN是在子层之前（Pre）还是之后（Post）应用。

### 为什么Pre-LN更稳定？

这个问题很关键，特别是训练深层Transformer时。

**Post-LN的问题：**

在Post-LN中，残差连接之后才做归一化。这意味着：
- 梯度要穿过LN层才能回到残差分支
- 深层网络中，梯度经过多次LN后可能会消失或爆炸
- 需要warmup才能稳定训练，而且学习率不能太大

**Pre-LN的优势：**

在Pre-LN中，先做归一化再进入子层：
- 残差连接直接把梯度传回去，不经过LN
- 每层的梯度都能"直达"输入，不会累积衰减
- 训练更稳定，不需要warmup，可以用更大的学习率

**数学角度理解：**

假设第 $l$ 层的输出是 $x_l$，子层的输出是 $F_l(x)$。

Post-LN: $x_{l+1} = \text{LN}(x_l + F_l(x_l))$

Pre-LN: $x_{l+1} = x_l + F_l(\text{LN}(x_l))$

对Post-LN，梯度要经过LN的雅可比矩阵；对Pre-LN，残差连接提供了"梯度高速公路"。

### PyTorch代码示例

```python
import torch
import torch.nn as nn

class PostLNTransformerBlock(nn.Module):
    """Post-LN: 原始Transformer的做法"""
    def __init__(self, d_model, n_heads, d_ff):
        super().__init__()
        self.attention = nn.MultiheadAttention(d_model, n_heads)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
    
    def forward(self, x):
        # Attention + Add + LN
        attn_out, _ = self.attention(x, x, x)
        x = self.ln1(x + attn_out)
        
        # FFN + Add + LN
        ffn_out = self.ffn(x)
        x = self.ln2(x + ffn_out)
        
        return x

class PreLNTransformerBlock(nn.Module):
    """Pre-LN: 现代LLM的做法"""
    def __init__(self, d_model, n_heads, d_ff):
        super().__init__()
        self.attention = nn.MultiheadAttention(d_model, n_heads)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model)
        )
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
    
    def forward(self, x):
        # LN + Attention + Add
        residual = x
        x = self.ln1(x)
        attn_out, _ = self.attention(x, x, x)
        x = residual + attn_out
        
        # LN + FFN + Add
        residual = x
        x = self.ln2(x)
        ffn_out = self.ffn(x)
        x = residual + ffn_out
        
        return x

# 对比两者的训练稳定性
d_model, n_heads, d_ff = 512, 8, 2048

post_ln = PostLNTransformerBlock(d_model, n_heads, d_ff)
pre_ln = PreLNTransformerBlock(d_model, n_heads, d_ff)

x = torch.randn(10, 32, d_model)  # seq_len=10, batch=32

# 模拟前向传播
out_post = post_ln(x)
out_pre = pre_ln(x)

print(f"Post-LN output mean: {out_post.mean():.4f}, std: {out_post.std():.4f}")
print(f"Pre-LN output mean: {out_pre.mean():.4f}, std: {out_pre.std():.4f}")
```

### 推荐论文

1. **Xiong et al., 2020** - "On Layer Normalization in the Transformer Architecture" - 详细分析Pre-LN和Post-LN
2. **Liu et al., 2020** - "Understanding the Difficulty of Training Transformers" - 分析Transformer训练困难的原因
3. **Wang et al., 2019** - "Learning Deep Transformer Models for Machine Translation" - 提出使用warmup的原因

---

## 7.8 DeepNorm

### 直觉理解

DeepNorm是2022年微软亚洲研究院提出的，专门解决**Post-LN在深层Transformer（比如1000层）中训练不稳定**的问题。

核心思想很巧妙：**修改残差连接中的缩放系数，并对权重矩阵的初始化做调整**。

为什么要这样做？因为深层网络中：
- 残差连接会让梯度累积，深层时梯度会变得很大
- 每层的贡献应该随着深度增加而减小，这样训练才稳定

### 核心公式推导

**原始Post-LN Transformer（第 $l$ 层）：**
$$x_l = \text{LN}(x_{l-1} + F_l(x_{l-1}))$$

**DeepNorm的修改：**
$$x_l = \text{LN}(\alpha \cdot x_{l-1} + F_l(x_{l-1}))$$

其中 $\alpha > 1$ 是一个缩放因子。

**更进一步，DeepNorm还修改了权重初始化：**
$$W \sim \mathcal{N}(0, \frac{2}{\beta \cdot N})$$

其中 $N$ 是层数，$\beta$ 是另一个超参数。

**$\alpha$ 和 $\beta$ 的具体取值：**

对于Encoder-Decoder模型：
- $\alpha = (2N)^{1/4}$，其中 $N$ 是encoder层数
- $\beta = (2M)^{1/4}$，其中 $M$ 是decoder层数

对于Decoder-only模型：
- $\alpha = (2N)^{1/4}$
- $\beta = (8N)^{-1/4}$

**为什么这样设计？**

推导思路（简化版）：

1. 假设每层的输出 $F_l(x)$ 的方差是 $\sigma^2$
2. 经过 $N$ 层后，残差连接会让方差累积到约 $N \sigma^2$
3. 为了让深层时信号不爆炸，需要 $\alpha x_{l-1}$ 的贡献和 $F_l(x_{l-1})$ 平衡
4. 推导可得 $\alpha = \Theta(N^{1/4})$ 时，各层梯度尺度一致

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import math

class DeepNormTransformerBlock(nn.Module):
    """DeepNorm: 支持深层Transformer的归一化方法"""
    def __init__(self, d_model, n_heads, d_ff, alpha, beta):
        super().__init__()
        self.attention = nn.MultiheadAttention(d_model, n_heads)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model)
        )
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.alpha = alpha
        
        # DeepNorm的权重初始化
        self._init_weights(beta)
    
    def _init_weights(self, beta):
        # 按DeepNorm的方式初始化权重
        for module in [self.attention, self.ffn]:
            for name, param in module.named_parameters():
                if 'weight' in name:
                    nn.init.normal_(param, mean=0, std=beta)
                elif 'bias' in name:
                    nn.init.zeros_(param)
    
    def forward(self, x):
        # DeepNorm: alpha * residual + sublayer
        residual = x
        attn_out, _ = self.attention(x, x, x)
        x = self.ln1(self.alpha * residual + attn_out)
        
        residual = x
        ffn_out = self.ffn(x)
        x = self.ln2(self.alpha * residual + ffn_out)
        
        return x

class DeepNormTransformer(nn.Module):
    """完整的DeepNorm Transformer"""
    def __init__(self, d_model=512, n_heads=8, d_ff=2048, n_layers=100):
        super().__init__()
        self.n_layers = n_layers
        
        # 计算alpha和beta
        self.alpha = (2 * n_layers) ** 0.25  # (2N)^(1/4)
        self.beta = (8 * n_layers) ** (-0.25)  # (8N)^(-1/4)
        
        self.layers = nn.ModuleList([
            DeepNormTransformerBlock(d_model, n_heads, d_ff, self.alpha, self.beta)
            for _ in range(n_layers)
        ])
        self.final_ln = nn.LayerNorm(d_model)
    
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return self.final_ln(x)

# 使用DeepNorm训练深层Transformer
model = DeepNormTransformer(d_model=512, n_heads=8, d_ff=2048, n_layers=100)

x = torch.randn(10, 32, 512)
out = model(x)
print(f"Output shape: {out.shape}")
print(f"Alpha: {model.alpha:.4f}")
print(f"Beta: {model.beta:.6f}")
```

### 推荐论文

1. **Wang et al., 2022** - "DeepNet: Scaling Transformers to 1,000 Layers" - DeepNorm原始论文
2. **Liu et al., 2020** - "Understanding the Difficulty of Training Transformers" - Post-LN训练困难的分析
3. **Bachlechner et al., 2021** - "ReZero is All You Need: Fast Convergence at Large Depth" - 类似思路：学习残差缩放因子

---

## 总结

| 方法 | 归一化维度 | 主要优点 | 主要缺点 | 典型应用 |
|------|-----------|---------|---------|---------|
| BN | batch维度 | 加速训练 | 依赖batch size | CNN |
| LN | 特征维度 | 不依赖batch | 计算略慢 | Transformer |
| RMSNorm | 特征维度 | 更快，简化LN | 略损精度 | LLaMA等LLM |
| GN | 分组维度 | 小batch友好 | 需选分组数 | 目标检测 |
| IN | 空间维度 | 风格无关 | 信息损失 | 风格迁移 |
| WN | 权重维度 | 优化友好 | 效果一般 | 特殊场景 |

选择建议：
- **做CV任务**：大batch用BN，小batch用GN
- **做NLP/LLM**：首选RMSNorm或LN
- **做图像生成**：考虑IN或AdaIN
- **训练超深网络**：用DeepNorm或Pre-LN

记住：**归一化不是万能的，但没有归一化是万万不能的！** 好的归一化策略能让你的训练快好几倍，少掉很多头发。
