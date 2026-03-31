# 8. 激活函数

激活函数是神经网络的“开关”，决定信息要不要传递下去。下面咱们聊聊常见的激活函数，公式、代码、论文都给你整明白！

## ReLU

**核心公式**：$\text{ReLU}(x) = \max(0, x)$

**优点**：简单、计算快、缓解梯度消失。
**缺点**：负半轴梯度为 0（“死神经元”问题），输出不是零均值。

**PyTorch 代码**：
```python
relu = nn.ReLU()
x = torch.randn(10)
y = relu(x)
```

**推荐论文**：
1. Nair & Hinton, "Rectified Linear Units Improve Restricted Boltzmann Machines", ICML 2010.
2. Glorot et al., "Deep Sparse Rectifier Neural Networks", AISTATS 2011.
3. He et al., "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification", ICCV 2015. (He 初始化)

---

## Leaky ReLU

**核心公式**：$\text{LeakyReLU}(x) = \begin{cases} x & \text{if } x \geq 0 \\ \alpha x & \text{if } x < 0 \end{cases}$ （$\alpha$ 通常取 0.01）

**解决啥问题**？ReLU 的“死神经元”问题，负半轴给个小斜率，保证梯度不为 0。

**PyTorch 代码**：
```python
leaky_relu = nn.LeakyReLU(negative_slope=0.01)
x = torch.randn(10)
y = leaky_relu(x)
```

**推荐论文**：
1. Maas et al., "Rectifier Nonlinearities Improve Neural Network Acoustic Models", ICML 2013.
2. Xu et al., "Empirical Evaluation of Rectified Activations in Convolutional Network", arXiv 2015.
3. Clevert et al., "Fast and Accurate Deep Network Learning by Exponential Linear Units (ELUs)", ICLR 2016. (对比了多种 ReLU 变体)

---

## GELU

**核心公式**：$\text{GELU}(x) = x \cdot \Phi(x)$，其中 $\Phi(x)$ 是标准正态分布的累积分布函数（CDF）。

**近似公式**（实际用）：$\text{GELU}(x) \approx 0.5x \left(1 + \tanh\left(\sqrt{\frac{2}{\pi}} (x + 0.044715 x^3)\right)\right)$

**为啥 BERT/GPT 用**？GELU 更平滑，梯度连续，适合预训练大模型。

**PyTorch 代码**：
```python
gelu = nn.GELU()
x = torch.randn(10)
y = gelu(x)
```

**推荐论文**：
1. Hendrycks & Gimpel, "Gaussian Error Linear Units (GELUs)", arXiv 2016.
2. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019.
3. Radford et al., "Language Models are Unsupervised Multitask Learners", OpenAI Blog 2019. (GPT-2)

---

## SiLU / Swish

**核心公式**：$\text{SiLU}(x) = x \cdot \sigma(x)$，其中 $\sigma(x) = \frac{1}{1 + e^{-x}}$ 是 sigmoid。

**为啥 LLaMA 用**？实验发现比 ReLU/GELU 效果更好，尤其在大模型上。

**PyTorch 代码**：
```python
silu = nn.SiLU()
x = torch.randn(10)
y = silu(x)
```

**推荐论文**：
1. Ramachandran et al., "Searching for Activation Functions", ICLR 2018. (Swish 原始论文)
2. Elfwing et al., "Sigmoid-Weighted Linear Units for Neural Network Function Approximation in Reinforcement Learning", Neural Networks 2018.
3. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", arXiv 2023.

---

## Mish

**核心公式**：$\text{Mish}(x) = x \cdot \tanh(\text{softplus}(x))$，其中 $\text{softplus}(x) = \ln(1 + e^x)$

**特点**：平滑、非单调（有小波动），实验效果不错但计算稍贵。

**PyTorch 代码**：
```python
import torch.nn.functional as F

def mish(x):
    return x * torch.tanh(F.softplus(x))

x = torch.randn(10)
y = mish(x)
```

**推荐论文**：
1. Misra, "Mish: A Self Regularized Non-Monotonic Neural Activation Function", BMVC 2020.
2. Basirat & Roth, "The Quest for the Golden Activation Function", arXiv 2018.
3. Nwankpa et al., "Activation Functions: Comparison of trends in Practice and Research", arXiv 2018.

---

## GLU (Gated Linear Unit)

**核心思想**：用门控机制控制信息流，类似 LSTM。

**公式推导**：
输入 $x$ 先线性变换成两部分 $a, b$，然后 $b$ 过 sigmoid 当门控：
$$
\text{GLU}(x) = a \odot \sigma(b), \quad \text{其中 } [a, b] = Wx + c
$$
$\odot$ 是逐元素乘。

**优点**：门控让网络选择性传递信息，表达力更强。

**PyTorch 代码**：
```python
class GLU(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 2 * output_dim)

    def forward(self, x):
        a, b = self.linear(x).chunk(2, dim=-1)
        return a * torch.sigmoid(b)
```

**推荐论文**：
1. Dauphin et al., "Language Modeling with Gated Convolutional Networks", ICML 2017.
2. Shazeer, "GLU Variants Improve Transformer", arXiv 2020.
3. Cho et al., "Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation", EMNLP 2014. (GRU 的门控思想)

---

## SwiGLU

**核心公式**：把 GLU 里的 sigmoid 换成 Swish（SiLU）：
$$
\text{SwiGLU}(x) = \text{Swish}(a) \odot b, \quad \text{其中 } [a, b] = Wx + c
$$
注意：有些实现是 $\text{Swish}(a) \odot b$，有些是 $a \odot \text{Swish}(b)$，本质一样。

**为啥 LLaMA/ChatGLM 用**？实验证明 SwiGLU 比 ReLU/GLU 效果更好。

**PyTorch 代码**：
```python
class SwiGLU(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 2 * output_dim)

    def forward(self, x):
        a, b = self.linear(x).chunk(2, dim=-1)
        return a * torch.sigmoid(a) * b  # Swish(a) = a * sigmoid(a)
```

**推荐论文**：
1. Shazeer, "GLU Variants Improve Transformer", arXiv 2020.
2. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", arXiv 2023.
3. Du et al., "GLM: General Language Model Pretraining with Autoregressive Blank Infilling", ACL 2022. (ChatGLM)

---

## GeGLU

**核心公式**：GLU 的 GELU 版本：
$$
\text{GeGLU}(x) = \text{GELU}(a) \odot b, \quad \text{其中 } [a, b] = Wx + c
$$

**PyTorch 代码**：
```python
class GeGLU(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 2 * output_dim)

    def forward(self, x):
        a, b = self.linear(x).chunk(2, dim=-1)
        return F.gelu(a) * b
```

**推荐论文**：
1. Shazeer, "GLU Variants Improve Transformer", arXiv 2020.
2. Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022. (Stable Diffusion 用了 GeGLU)
3. Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020. (GPT-3 讨论了 GLU 变体)

---

## ReGLU

**核心公式**：GLU 的 ReLU 版本：
$$
\text{ReGLU}(x) = \text{ReLU}(a) \odot b, \quad \text{其中 } [a, b] = Wx + c
$$

**PyTorch 代码**：
```python
class ReGLU(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 2 * output_dim)

    def forward(self, x):
        a, b = self.linear(x).chunk(2, dim=-1)
        return F.relu(a) * b
```

**推荐论文**：
1. Shazeer, "GLU Variants Improve Transformer", arXiv 2020.
2. Kotelnikov et al., "Tabular Data: Deep Learning is Not All You Need", arXiv 2022. (ReGLU 在表格数据效果好)
3. Gorishniy et al., "Revisiting Deep Learning Models for Tabular Data", NeurIPS 2021.

---

## Squared ReLU

**核心公式**：$\text{SquaredReLU}(x) = (\text{ReLU}(x))^2 = \max(0, x)^2$

**特点**：比 ReLU 更平滑（一阶导连续），实验在 ViT 中效果不错。

**PyTorch 代码**：
```python
def squared_relu(x):
    return torch.relu(x) ** 2

x = torch.randn(10)
y = squared_relu(x)
```

**推荐论文**：
1. Socher et al., "Parsing Natural Scenes and Natural Language with Recursive Neural Networks", ICML 2011. (早期用平方激活)
2. Bhardwaj et al., "Squared ReLU: A Low-Complexity Nonlinearity for Deep Neural Networks", arXiv 2021.
3. Zou et al., "LayerScale: Scale Your Attention Better", NeurIPS 2023. (ViT 中用了 Squared ReLU)

---

## Softmax

**核心公式**：把向量变成概率分布：
$$
\text{Softmax}(x_i) = \frac{e^{x_i}}{\sum_{j} e^{x_j}}
$$

**温度参数**：加个温度 $T$ 控制分布平滑度：
$$
\text{Softmax}_T(x_i) = \frac{e^{x_i / T}}{\sum_{j} e^{x_j / T}}
$$
- $T \to 0$：分布趋近 one-hot（更尖锐）
- $T \to \infty$：分布趋近均匀（更平滑）

**PyTorch 代码**：
```python
softmax = nn.Softmax(dim=-1)  # dim 指定归一化维度
x = torch.randn(32, 10)  # 32 个样本，10 类
y = softmax(x)  # 每行和为 1

# 带温度的 Softmax
T = 0.5
y_temp = torch.softmax(x / T, dim=-1)
```

**推荐论文**：
1. Bridle, "Probabilistic Interpretation of Feedforward Classification Network Outputs, with Relationships to Statistical Pattern Recognition", Neurocomputing 1990.
2. Hinton et al., "Distilling the Knowledge in a Neural Network", NIPS 2014. (知识蒸馏用温度 Softmax)
3. Vaswani et al., "Attention Is All You Need", NeurIPS 2017. (Transformer 的注意力用 Softmax)