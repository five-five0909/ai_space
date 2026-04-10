# Week 4 参考答案

> 建议完成练习后再查看本答案

---

## P013 手写LSTM cell

### 参考代码

```python
"""
P013 手写LSTM cell
思路：四个gate分别用Linear实现
"""

import torch
import torch.nn as nn

class MyLSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        # 四个gate的Linear层
        self.W_i = nn.Linear(input_size + hidden_size, hidden_size)
        self.W_f = nn.Linear(input_size + hidden_size, hidden_size)
        self.W_o = nn.Linear(input_size + hidden_size, hidden_size)
        self.W_g = nn.Linear(input_size + hidden_size, hidden_size)

    def forward(self, x, h_prev, c_prev):
        """
        Args:
            x: (batch, input_size)
            h_prev: (batch, hidden_size)
            c_prev: (batch, hidden_size)
        Returns:
            h_t, c_t
        """
        # 拼接输入和上一时刻hidden
        combined = torch.cat([x, h_prev], dim=1)

        # 四个gate
        i = torch.sigmoid(self.W_i(combined))  # 输入门
        f = torch.sigmoid(self.W_f(combined))  # 遗忘门
        o = torch.sigmoid(self.W_o(combined))  # 输出门
        g = torch.tanh(self.W_g(combined))     # cell gate

        # 更新cell state
        c_t = f * c_prev + i * g

        # 输出hidden state
        h_t = o * torch.tanh(c_t)

        return h_t, c_t


if __name__ == "__main__":
    # 测试
    batch_size = 4
    input_size = 16
    hidden_size = 32

    my_cell = MyLSTMCell(input_size, hidden_size)
    ref_cell = nn.LSTMCell(input_size, hidden_size)

    x = torch.randn(batch_size, input_size)
    h = torch.randn(batch_size, hidden_size)
    c = torch.randn(batch_size, hidden_size)

    my_h, my_c = my_cell(x, h, c)
    print(f"h shape: {my_h.shape}, c shape: {my_c.shape}")
```

---

## P014 BiLSTM序列标注

### 参考代码

```python
"""
P014 BiLSTM序列标注
"""

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

class BiLSTMRegressor(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size,
                           bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_size * 2, output_size)

    def forward(self, x, lengths):
        """
        Args:
            x: (batch, seq_len, input_size)
            lengths: 每个序列的实际长度
        Returns:
            (batch, seq_len, output_size)
        """
        # Pack
        packed = pack_padded_sequence(x, lengths.cpu(),
                                      batch_first=True, enforce_sorted=False)

        # LSTM
        packed_out, _ = self.lstm(packed)

        # Unpack
        out, _ = pad_packed_sequence(packed_out, batch_first=True)

        # 预测
        out = self.fc(out)

        return out


if __name__ == "__main__":
    model = BiLSTMRegressor(10, 32, 1)
    x = torch.randn(4, 20, 10)
    lengths = torch.tensor([20, 15, 10, 18])

    out = model(x, lengths)
    print(f"Output shape: {out.shape}")
```

---

## P015 Kaggle · Store Sales LSTM

### 解题思路

1. 滑动窗口构造序列数据
2. 特征：store_nbr, family, onpromotion + 日期编码
3. 目标：RMSLE < 0.6

### 关键点

- family类别用embedding
- log1p(sales)预测，expm1还原
- 日期特征：星期几、月份等