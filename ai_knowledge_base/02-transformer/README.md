# 2. Transformer 系列

> 一句话：Transformer就是用self-attention搞序列建模，GPT是单向的，BERT是双向的，后面所有LLM都是在这基础上改的。

---

## Transformer

### 这玩意儿到底是啥？

Transformer是2017年Vaswani等人提出的**纯注意力模型**，彻底干掉了RNN和CNN。核心思想就一个：**每个位置都能直接看到其他所有位置**，不用像RNN那样一步步算。

### 核心公式，手把手推导

**第一步：输入embedding**

```
X = [x_1, x_2, ..., x_n]  # n个token，每个d维
```

**第二步：QKV投影（多头）**

```
Q = XW_Q  # (n, d_k)
K = XW_K  # (n, d_k)  
V = XW_V  # (n, d_v)
```

**第三步：自注意力计算**

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

**为什么要除以√d_k？**
- QK^T的每个元素是d_k个随机数的点积
- 方差是d_k，所以除以√d_k让方差变成1
- 不然softmax会饱和，梯度消失

**第四步：多头注意力**

```
head_i = Attention(XW_Q^i, XW_K^i, XW_V^i)
MultiHead = Concat(head_1, ..., head_h)W_O
```

**第五步：前馈网络FFN**

```
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
```

**第六步：残差连接 + LayerNorm**

```
x' = LayerNorm(x + MultiHead(x))
x'' = LayerNorm(x' + FFN(x'))
```

### 编码器-解码器架构

- **编码器**：6层，每层Self-Attention + FFN
- **解码器**：6层，每层Masked Self-Attention + Cross-Attention + FFN
- **Masked Self-Attention**：只能看前面的token，不能偷看后面的
- **Cross-Attention**：Query来自解码器，Key/Value来自编码器

### PyTorch代码示例

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, q, k, v, mask=None):
        # q, k, v: (batch_size, seq_len, d_model)
        batch_size = q.size(0)
        
        # 线性投影
        Q = self.W_q(q)  # (batch, seq_len, d_model)
        K = self.W_k(k)
        V = self.W_v(v)
        
        # 分头: (batch, seq_len, num_heads, d_k)
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k)
        K = K.view(batch_size, -1, self.num_heads, self.d_k)
        V = V.view(batch_size, -1, self.num_heads, self.d_k)
        
        # 转置: (batch, num_heads, seq_len, d_k)
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn = torch.softmax(scores, dim=-1)
        context = torch.matmul(attn, V)
        
        # 合并头
        context = context.transpose(1, 2).contiguous()
        context = context.view(batch_size, -1, self.d_model)
        
        output = self.W_o(context)
        return output

class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # 自注意力 + 残差
        attn_out = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        # FFN + 残差
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))
        return x
```

### 推荐论文

1. **Vaswani, A., et al. (2017).** "Attention Is All You Need." *NeurIPS 2017.*
   - 原始论文，必读经典

2. **Devlin, J., et al. (2019).** "BERT: Pre-training of Deep Bidirectional Transformers." *NAACL 2019.*
   - BERT怎么用Transformer做双向预训练

3. **Radford, A., et al. (2018).** "Improving Language Understanding by Generative Pre-Training (GPT-1)." *OpenAI.*
   - GPT怎么用Transformer做自回归

---

## GPT系列

### 这玩意儿到底是啥？

GPT就是**纯解码器的Transformer**，只能从左往右生成，不能回头看。GPT-1/2/3/4就是不断堆参数、堆数据、堆工程优化。

### 核心公式：自回归语言建模

```
P(x) = ∏_{t=1}^n P(x_t | x_1, ..., x_{t-1})
```

**训练目标：** 给定前面的token，预测下一个token

**损失函数：** 交叉熵损失

```
L = -∑_{t=1}^n log P(x_t | x_{<t})
```

### GPT演进路线

- **GPT-1 (2018)**：1.17亿参数，在BooksCorpus上预训练
- **GPT-2 (2019)**：15亿参数，零样本能力
- **GPT-3 (2020)**：1750亿参数，少样本学习
- **GPT-4 (2023)**：多模态，更强推理
- **GPT-4o (2024)**：原生多模态，实时对话

### Scaling Law（缩放定律）

```
L(N, D) = (N_c / N)^α_N + (D_c / D)^α_D + L_0
```

- N：参数量，D：训练数据量
- 性能随N和D的幂律提升
- GPT-3验证了这个规律

### PyTorch伪代码

```python
class GPT(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, max_seq_len):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)
        self.layers = nn.ModuleList([
            TransformerDecoderLayer(d_model, num_heads) 
            for _ in range(num_layers)
        ])
        self.lm_head = nn.Linear(d_model, vocab_size)
    
    def forward(self, x):
        # x: (batch, seq_len)
        batch_size, seq_len = x.shape
        positions = torch.arange(0, seq_len, device=x.device).unsqueeze(0)
        
        # Embedding
        x = self.token_embedding(x) + self.position_embedding(positions)
        
        # Decoder layers
        for layer in self.layers:
            x = layer(x)
        
        # Language modeling head
        logits = self.lm_head(x)
        return logits
```

### 推荐论文

1. **Radford, A., et al. (2018).** "Improving Language Understanding by Generative Pre-Training." *OpenAI.*
   - GPT-1原始论文

2. **Brown, T., et al. (2020).** "Language Models are Few-Shot Learners (GPT-3)." *NeurIPS 2020.*
   - GPT-3，涌现能力

3. **OpenAI (2023).** "GPT-4 Technical Report." *arXiv:2303.08774.*
   - GPT-4技术报告

---

## BERT系列

### 这玩意儿到底是啥？

BERT（Bidirectional Encoder Representations from Transformers）是Google 2018年提出的**双向Transformer编码器**。它最大的创新是：**同时看左右两边的上下文**，而不是像GPT那样只能从左往右看。

**核心思想：**
- 用Transformer编码器（不是解码器）
- 用两种预训练任务：MLM和NSP
- 下游任务只需要微调，不用改架构

### 核心公式推导

**1. Masked Language Model (MLM)**

随机遮住15%的token，让模型预测：

$$
\mathcal{L}_{MLM} = -\sum_{i \in M} \log P(x_i | x_{\setminus M})
$$

其中$M$是被遮住的token集合，$x_{\setminus M}$是未被遮住的token。

**遮住策略（15%中的）：**
- 80%换成`[MASK]`
- 10%换成随机token
- 10%保持不变

**为什么这样设计？**
- 纯MASK会让预训练和微调有gap（微调时没有MASK）
- 随机替换让模型学习纠错
- 保持不变让模型学习原样输出

**2. Next Sentence Prediction (NSP)**

判断两个句子是否连续：

$$
\mathcal{L}_{NSP} = -\log P(\text{IsNext} | \text{SentA}, \text{SentB})
$$

**训练数据构造：**
- 50%是真正的连续句子（IsNext）
- 50%是随机配对的句子（NotNext）

**3. 总损失**

$$
\mathcal{L}_{BERT} = \mathcal{L}_{MLM} + \mathcal{L}_{NSP}
$$

### BERT架构

```
BERT输入：
[CLS] Token1 Token2 ... TokenN [SEP] TokenA TokenB ... [SEP]

特殊Token：
- [CLS]：分类任务用，对应的输出向量用于分类
- [SEP]：句子分隔符
- [MASK]：MLM任务用

位置编码：可学习的绝对位置编码

Segment Embedding：区分两个句子（句子A用0，句子B用1）
```

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BertEmbeddings(nn.Module):
    def __init__(self, vocab_size, hidden_size, max_position_embeddings, type_vocab_size):
        super().__init__()
        self.word_embeddings = nn.Embedding(vocab_size, hidden_size)
        self.position_embeddings = nn.Embedding(max_position_embeddings, hidden_size)
        self.token_type_embeddings = nn.Embedding(type_vocab_size, hidden_size)
        self.LayerNorm = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids, token_type_ids=None):
        seq_length = input_ids.size(1)
        position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
        position_ids = position_ids.unsqueeze(0).expand_as(input_ids)

        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)

        word_embeds = self.word_embeddings(input_ids)
        position_embeds = self.position_embeddings(position_ids)
        token_type_embeds = self.token_type_embeddings(token_type_ids)

        embeddings = word_embeds + position_embeds + token_type_embeds
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings

class BertOnlyMLMHead(nn.Module):
    """MLM预测头"""
    def __init__(self, hidden_size, vocab_size):
        super().__init__()
        self.dense = nn.Linear(hidden_size, hidden_size)
        self.transform_act_fn = F.gelu
        self.LayerNorm = nn.LayerNorm(hidden_size)
        self.decoder = nn.Linear(hidden_size, vocab_size)

    def forward(self, hidden_states):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        hidden_states = self.decoder(hidden_states)
        return hidden_states

class BertForMaskedLM(nn.Module):
    """BERT MLM模型"""
    def __init__(self, vocab_size=30522, hidden_size=768,
                 num_hidden_layers=12, num_attention_heads=12,
                 max_position_embeddings=512):
        super().__init__()
        self.embeddings = BertEmbeddings(vocab_size, hidden_size,
                                          max_position_embeddings, 2)
        # 这里简化，实际用TransformerEncoder
        self.encoder = nn.ModuleList([
            TransformerEncoderLayer(hidden_size, num_attention_heads, hidden_size * 4)
            for _ in range(num_hidden_layers)
        ])
        self.cls = BertOnlyMLMHead(hidden_size, vocab_size)

    def forward(self, input_ids, attention_mask=None, token_type_ids=None, labels=None):
        embeddings = self.embeddings(input_ids, token_type_ids)
        hidden_states = embeddings
        for layer in self.encoder:
            hidden_states = layer(hidden_states, attention_mask)

        prediction_scores = self.cls(hidden_states)

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(
                prediction_scores.view(-1, prediction_scores.size(-1)),
                labels.view(-1)
            )

        return {"loss": loss, "logits": prediction_scores}

# 使用HuggingFace Transformers
from transformers import BertForMaskedLM, BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')

# MLM预测
text = "The capital of France is [MASK]."
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

# 获取预测的token
predicted_token_id = outputs.logits[0, 5].argmax().item()
predicted_token = tokenizer.decode([predicted_token_id])
print(f"Predicted: {predicted_token}")  # 应该预测出 "paris"
```

### BERT变体

| 模型 | 大小 | 参数量 | 特点 |
|------|------|--------|------|
| BERT-base | 12层 | 110M | 原始版本 |
| BERT-large | 24层 | 340M | 更大更强 |
| RoBERTa | 12层 | 125M | 更多数据，去掉NSP |
| ALBERT | 12层 | 12M | 参数共享，更小 |
| DistilBERT | 6层 | 66M | 蒸馏压缩 |
| ELECTRA | 12层 | 110M | 替换检测，更高效 |

### 推荐论文

1. **Devlin et al., 2019** - "BERT: Pre-training of Deep Bidirectional Transformers" - BERT原论文
2. **Liu et al., 2019** - "RoBERTa: A Robustly Optimized BERT Pretraining Approach" - 改进版
3. **Lan et al., 2020** - "ALBERT: A Lite BERT for Self-supervised Learning" - 轻量版

---

## GPT系列详解

### GPT-1 (2018)

**核心贡献：**
- 首次提出"预训练+微调"范式
- 在无标注数据上预训练，在下游任务上微调
- 证明生成式预训练可以学到通用语言表示

**架构：** 12层Transformer解码器，117M参数

### GPT-2 (2019)

**核心贡献：**
- 零样本学习（Zero-shot Learning）
- 更大的模型和数据（1.5B参数，WebText数据集）
- 发现"任务条件化"：用提示词指定任务

**关键洞察：**
```
传统方式：训练专门的分类器
GPT-2方式：
Input: "Translate English to French: Hello world"
Output: "Bonjour le monde"
```

### GPT-3 (2020)

**核心贡献：**
- 少样本学习（Few-shot Learning）
- 175B参数，涌现能力
- In-context Learning：无需梯度更新，仅通过上下文学习

**涌现能力示例：**
```
Zero-shot: 问答能力一般
Few-shot: 给几个例子后，能力大幅提升

Example:
Q: What is the capital of Germany?
A: Berlin

Q: What is the capital of France?
A: [模型预测] Paris
```

### GPT-4 (2023)

**核心贡献：**
- 多模态输入（图像+文本）
- 更强的推理能力
- 更长的上下文（32K tokens）

**能力提升：**
- 模拟律师考试：前10%
- 生物学奥赛：前1%
- 编程能力：显著提升

### GPT-4o (2024)

**核心贡献：**
- 原生多模态（统一处理文本、图像、音频）
- 实时语音对话
- 更快的推理速度

---

## LLaMA系列

### 这玩意儿到底是啥？

LLaMA是Meta开源的大语言模型系列，核心特色是**开源、高效、可商用**。它证明了用更多数据训练更小的模型，可以达到甚至超越更大模型的效果。

### LLaMA架构特点

**1. Pre-normalization (GPT-2风格)：**
```
x' = x + Attention(LayerNorm(x))
x'' = x' + FFN(LayerNorm(x'))
```
使用RMSNorm替代LayerNorm

**2. SwiGLU激活函数：**
```
FFN(x) = SwiGLU(x) = (xW_1) ⊙ Swish(xW_2)
```
比ReLU效果更好

**3. RoPE位置编码：**
使用旋转位置编码，支持更长上下文

### 模型规格

| 模型 | 参数量 | 层数 | 隐藏维度 | 头数 |
|------|--------|------|----------|------|
| LLaMA-7B | 7B | 32 | 4096 | 32 |
| LLaMA-13B | 13B | 40 | 5120 | 40 |
| LLaMA-33B | 33B | 60 | 6656 | 52 |
| LLaMA-65B | 65B | 80 | 8192 | 64 |
| LLaMA-2-7B | 7B | 32 | 4096 | 32 |
| LLaMA-2-70B | 70B | 80 | 8192 | 64 |
| LLaMA-3-8B | 8B | 32 | 4096 | 32 |
| LLaMA-3-70B | 70B | 80 | 8192 | 64 |

### PyTorch代码示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization"""
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm = x.float().pow(2).mean(-1, keepdim=True).add(self.eps).rsqrt()
        return (x.float() * norm).type_as(x) * self.weight

class RotaryEmbedding(nn.Module):
    """旋转位置编码"""
    def __init__(self, dim, max_seq_len=2048, base=10000):
        super().__init__()
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self.max_seq_len = max_seq_len

    def forward(self, x, seq_len):
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        return emb.cos(), emb.sin()

def rotate_half(x):
    x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary_pos_emb(q, k, cos, sin):
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed

class LLaMAMLP(nn.Module):
    """SwiGLU MLP"""
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

class LLaMABlock(nn.Module):
    def __init__(self, dim, n_heads, hidden_dim):
        super().__init__()
        self.attention = MultiHeadAttention(dim, n_heads)
        self.feed_forward = LLaMAMLP(dim, hidden_dim)
        self.attention_norm = RMSNorm(dim)
        self.ffn_norm = RMSNorm(dim)

    def forward(self, x, cos, sin):
        h = x + self.attention(self.attention_norm(x), cos, sin)
        out = h + self.feed_forward(self.ffn_norm(h))
        return out

# 使用HuggingFace Transformers
from transformers import LlamaForCausalLM, LlamaTokenizer

model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

prompt = "The capital of France is"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0]))
```

### 推荐论文

1. **Touvron et al., 2023** - "LLaMA: Open and Efficient Foundation Language Models" - LLaMA原论文
2. **Touvron et al., 2023** - "LLaMA 2: Open Foundation and Fine-Tuned Chat Models" - LLaMA 2
3. **Meta, 2024** - "The Llama 3 Herd of Models" - LLaMA 3

---

## 总结

### 架构对比

| 模型 | 架构 | 预训练任务 | 主要用途 |
|------|------|------------|----------|
| Transformer | 编码器+解码器 | Seq2Seq | 机器翻译 |
| BERT | 编码器 | MLM + NSP | 理解任务 |
| GPT | 解码器 | 自回归 | 生成任务 |
| LLaMA | 解码器 | 自回归 | 通用LLM |

### 选择建议

```
文本理解任务 → BERT系列
文本生成任务 → GPT/LLaMA系列
开源可商用 → LLaMA系列
最强闭源 → GPT-4
```

---

> Transformer是现代NLP的基石！BERT用双向编码做理解，GPT用单向解码做生成，LLaMA开源引领潮流。理解这三者，就理解了大模型的本质！