# Week 4 · LSTM / RNN

> 序列建模，门控机制

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P013 | 手写LSTM cell | Hard | LSTM、RNN |
| P014 | BiLSTM序列标注 | Medium | LSTM、双向 |
| P015 | Kaggle · Store Sales LSTM | Medium | LSTM、时序、Kaggle |

---

## P013 手写LSTM cell ⭐⭐⭐

### 题目描述

不用 nn.LSTM，用 nn.Linear 手动实现单步LSTM cell：输入gate、forget gate、output gate、cell gate，返回 (h_t, c_t)。

### 函数签名

```python
class MyLSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size):
        ...

    def forward(self, x, h_prev, c_prev):
        ...
```

### 约束条件

- 所有gate必须用独立的nn.Linear（不合并成一个大Linear）
- 激活：sigmoid for i/f/o，tanh for g和最终h
- 与 nn.LSTMCell 在同权重下输出 atol=1e-5 内一致

### 验收断言（assert）

```python
h_t.shape == (batch, hidden_size)
c_t.shape == (batch, hidden_size)
# 手动copy权重后
torch.allclose(my_cell(x, h, c)[0], ref_cell(x, (h, c))[0], atol=1e-5)
```

### 提示

> i=σ(W_i·x+U_i·h+b_i)，f同理，g=tanh(...)，o同理；c_t=f⊙c+i⊙g；h_t=o⊙tanh(c_t)

---

## P014 BiLSTM序列标注 ⭐⭐

### 题目描述

用 nn.LSTM(bidirectional=True) 实现BiLSTM，输入shape=(seq_len, batch, input_size)，输出每个时间步的预测（回归），验证双向输出维度和信息流。

### 函数签名

```python
class BiLSTMRegressor(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        ...
```

### 约束条件

- 必须用 pack_padded_sequence 处理变长输入
- 输出shape=(batch, seq_len, output_size)
- 打印并注释：为什么forward_output[-1]不等于backward_output[0]

### 验收断言（assert）

```python
output.shape == (batch, seq_len, output_size)
model(x, lengths).shape正确
用pad_packed_sequence还原后与不pad版本结果一致
```

### 提示

> pack→LSTM→pad_packed；注意batch_first参数的影响，双向hidden_size×2

---

## P015 Kaggle · Store Sales LSTM ⭐⭐

### 题目描述

用LSTM做Store Sales时序预测，Kaggle LB RMSLE < 0.6。需要自己设计滑动窗口Dataset。

### 函数签名

```python
# 目标：Kaggle public LB RMSLE < 0.6
```

### 约束条件

- 滑动窗口：用前30天预测后1天
- 特征：至少包含 store_nbr、family、onpromotion + 日期编码
- 提交格式符合Kaggle要求

### 验收断言（assert）

```python
val RMSLE < 0.5  # 本地验证
LSTM hidden_size >= 64
不允许用预训练模型或XGBoost组合
```

### 提示

> 先做EDA，family类别多→embedding；log1p(sales)再预测，最后expm1还原

---

## 本周学习目标

- [ ] 手写LSTM理解门控机制
- [ ] 掌握双向LSTM的输出处理
- [ ] 设计时序滑动窗口Dataset
- [ ] Kaggle时序预测提交

## 参考答案

> 见 `../solutions/Week04-参考答案.md`