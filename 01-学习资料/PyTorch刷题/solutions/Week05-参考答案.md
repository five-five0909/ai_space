# Week 5 参考答案

> 建议完成练习后再查看本答案

---

## P016 Scaled Dot-Product Attention

### 参考代码

```python
"""
P016 Scaled Dot-Product Attention
"""

import torch
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None, dropout_p=0.0):
    """
    Args:
        Q: (batch, seq_len, d_k)
        K: (batch, seq_len, d_k)
        V: (batch, seq_len, d_v)
        mask: (batch, seq_len, seq_len) True表示要mask的位置
    Returns:
        output, attention_weights
    """
    d_k = Q.size(-1)

    # 计算注意力分数
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)

    # 应用mask
    if mask is not None:
        scores = scores.masked_fill(mask, float('-inf'))

    # Softmax
    attn_weights = F.softmax(scores, dim=-1)

    # Dropout
    if dropout_p > 0:
        attn_weights = F.dropout(attn_weights, p=dropout_p)

    # 加权求和
    output = attn_weights @ V

    return output, attn_weights


if __name__ == "__main__":
    batch, seq_len, d_k = 2, 5, 8
    Q = torch.randn(batch, seq_len, d_k)
    K = torch.randn(batch, seq_len, d_k)
    V = torch.randn(batch, seq_len, d_k)

    # 无mask
    out, attn = scaled_dot_product_attention(Q, K, V)
    print(f"Output shape: {out.shape}")
    print(f"Attention sum: {attn.sum(dim=-1)}")  # 应该全为1

    # Causal mask
    causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    out_masked, attn_masked = scaled_dot_product_attention(Q, K, V, mask=causal_mask)
    print(f"Causal attention upper triangle: {attn_masked[0][0].triu(1)}")  # 应该全为0
```

---

## P017 多头注意力可视化

### 参考代码

```python
"""
P017 多头注意力可视化
"""

import torch
import torch.nn as nn
import matplotlib.pyplot as plt

class SpectralTransformer(nn.Module):
    def __init__(self, num_bands, d_model, nhead, num_layers):
        super().__init__()
        self.embedding = nn.Linear(num_bands, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

    def forward(self, x):
        return self.transformer(self.embedding(x))

def visualize_attention(model, x, save_path='attention.png'):
    """可视化第一层attention权重"""
    model.eval()

    # Hook来获取attention weights
    attn_weights = []

    def hook_fn(module, input, output):
        # output是(attn_output, attn_weights)元组
        if isinstance(output, tuple) and len(output) > 1:
            attn_weights.append(output[1].detach())

    # 注册hook（需要找到MultiheadAttention层）
    # 注意：TransformerEncoderLayer的self_attn是MultiheadAttention

    with torch.no_grad():
        _ = model(x)

    # 绘制热力图
    if attn_weights:
        attn = attn_weights[0][0]  # (nhead, seq_len, seq_len)
        nhead = attn.shape[0]

        fig, axes = plt.subplots(1, nhead, figsize=(4*nhead, 4))
        for i in range(nhead):
            if nhead > 1:
                ax = axes[i]
            else:
                ax = axes
            im = ax.imshow(attn[i].cpu().numpy(), cmap='viridis')
            ax.set_title(f'Head {i+1}')
            plt.colorbar(im, ax=ax)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"Saved to {save_path}")

if __name__ == "__main__":
    model = SpectralTransformer(num_bands=100, d_model=64, nhead=4, num_layers=2)
    x = torch.randn(1, 100, 100)  # (batch, seq_len, num_bands)

    # 注意：实际运行需要正确设置hook
    print("Model created successfully")
```

---

## P018 Kaggle · NLP Disaster Tweets Transformer

### 解题思路

1. 自己实现Tokenizer（字符级或词级）
2. 从零训练Transformer Encoder
3. 目标：F1 > 0.78

### 关键点

- 词级tokenizer：Counter取top8000词
- 位置编码：sin/cos
- 不用预训练embedding