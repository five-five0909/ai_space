# Week 5 · Transformer

> 注意力机制，从零实现

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P016 | Scaled Dot-Product Attention | Medium | Attention、Transformer |
| P017 | 多头注意力可视化 | Medium | Attention、可视化 |
| P018 | Kaggle · NLP Disaster Tweets Transformer | Hard | Transformer、NLP、Kaggle |

---

## P016 Scaled Dot-Product Attention ⭐⭐

### 题目描述

不用 nn.MultiheadAttention，从零实现 Scaled Dot-Product Attention，支持 mask（padding mask + causal mask）。

### 函数签名

```python
def scaled_dot_product_attention(
    Q, K, V,
    mask=None,
    dropout_p=0.0
) -> tuple[torch.Tensor, torch.Tensor]:
```

### 约束条件

- 返回 (output, attention_weights)
- mask为True的位置填充 -inf（softmax后趋近0）
- causal mask时：位置i不能attend到位置j>i

### 验收断言（assert）

```python
output.shape == Q.shape
attn_weights.sum(dim=-1) 全为 1.0  # softmax归一化
causal mask后，attn_weights上三角全为0
```

### 提示

> scores = Q@K.T/sqrt(d_k)；mask位置用 scores.masked_fill(mask, float('-inf'))；然后softmax

---

## P017 多头注意力可视化 ⭐⭐

### 题目描述

搭一个2层Transformer Encoder，输入一批高光谱序列（把波段当token），可视化第1层所有head的attention权重热力图，观察哪些波段互相关注。

### 函数签名

```python
class SpectralTransformer(nn.Module):
    def __init__(self, num_bands, d_model, nhead, num_layers):
        ...
```

### 约束条件

- 用 nn.TransformerEncoder + nn.TransformerEncoderLayer
- 必须hook出attention weights（用 need_weights=True）
- 用matplotlib画出 nhead×seq_len×seq_len 的热力图，保存为PNG

### 验收断言（assert）

```python
attn_weights.shape == (nhead, seq_len, seq_len)
每个head的权重行和为1
PNG输出分辨率 >= 150dpi
```

### 提示

> TransformerEncoderLayer的self_attn是MultiheadAttention，forward时传need_weights=True可拿到attn_output_weights

---

## P018 Kaggle · NLP Disaster Tweets Transformer ⭐⭐⭐

### 题目描述

用自己实现的Mini Transformer Encoder（不用HuggingFace）做Disaster Tweets二分类，Kaggle LB F1 > 0.78。

### 函数签名

```python
# 目标：Kaggle public LB F1 > 0.78
```

### 约束条件

- Tokenizer：自己实现字符级或词级，vocab_size <= 10000
- 不允许用预训练embedding（从零训练）
- Transformer Encoder层数 >= 2，d_model >= 64

### 验收断言（assert）

```python
val F1 > 0.75
模型参数量 < 5M
Kaggle提交格式正确：id,target
```

### 提示

> 字符级tokenizer简单但效果一般；词级：Counter取top8000词加UNK；位置编码用sin/cos

---

## 本周学习目标

- [ ] 手写Scaled Dot-Product Attention
- [ ] 理解mask机制（padding + causal）
- [ ] 可视化注意力权重
- [ ] 从零训练Transformer做NLP

## 参考答案

> 见 `../solutions/Week05-参考答案.md`