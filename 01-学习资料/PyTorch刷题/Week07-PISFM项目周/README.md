# Week 7 · PISFM项目周

> 论文代码迁移，完整实验复现

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P023 | PISFM数据管线PyTorch化 | Medium | Dataset、PISFM实战 |
| P024 | BiMamba Encoder迁移 | Hard | PISFM实战、架构迁移 |
| P025 | 完整PISFM训练实验 | Hard | PISFM实战、K折、TensorBoard |
| P026 | Kaggle · 高光谱回归开放赛 | Medium | PISFM实战、Kaggle |

---

## P023 PISFM数据管线PyTorch化 ⭐⭐

### 题目描述

把你现有的PISFM Keras数据管线完整迁移到PyTorch：CSV读取→归一化→K折split→DataLoader，输出与Keras版本在同数据下的统计量一致。

### 函数签名

```python
class PISFMDataModule:
    def __init__(self, csv_path, k=5, batch_size=32):
        ...

    def get_fold(self, fold_idx) -> tuple[DataLoader, DataLoader]:
        ...
```

### 约束条件

- 归一化参数必须从训练折计算，不能用全量数据
- 返回的DataLoader pin_memory=True（如果有GPU）
- 验证：同数据下PyTorch和Keras的train_mean在 ±1e-4 内一致

### 验收断言（assert）

```python
get_fold(0)[0] 和 get_fold(0)[1] 无样本重叠
train_mean_pytorch ≈ train_mean_keras（atol=1e-4）
DataLoader每个batch shape=(batch_size, num_features)
```

### 提示

> 用pandas读CSV，转numpy再转tensor；注意keras默认float32和PyTorch一致

---

## P024 BiMamba Encoder迁移 ⭐⭐⭐

### 题目描述

把你PISFM论文里的BiMamba Encoder用PyTorch重写（如果没有现成Mamba库，用BiLSTM近似实现），输出与Keras版本在同权重下atol=1e-3内一致。

### 函数签名

```python
class BiMambaEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers=2):
        ...
```

### 约束条件

- 如用BiLSTM近似：必须是双向，num_layers可配置
- 权重迁移：写一个 load_keras_weights(keras_model) 工具函数
- forward输出shape=(batch, seq_len, hidden_dim*2)

### 验收断言（assert）

```python
输出shape正确
在同随机输入下，torch版和keras版输出cosine_similarity > 0.99
model.eval()下输出确定性（无dropout影响）
```

### 提示

> Keras Dense→PyTorch Linear，注意权重需要转置；Keras LSTM权重拆分顺序是[i,f,c,o]，PyTorch是[i,f,g,o]

---

## P025 完整PISFM训练实验 ⭐⭐⭐

### 题目描述

用PyTorch跑完整PISFM实验：BiMamba Encoder + K折CV + 早停 + TensorBoard记录，最终输出5折的R²和RMSE均值，与你论文Keras版本对比。

### 函数签名

```python
# 输出：experiments/pisfm_pytorch/
#   ├── tensorboard/
#   ├── checkpoints/fold_*.pth
#   └── results.json
```

### 约束条件

- 必须用TensorBoard记录：train loss、val loss、val R²（每epoch）
- 早停patience=20
- results.json格式：{'fold_r2':[...],'mean_r2':float,'mean_rmse':float}

### 验收断言（assert）

```python
mean_r2 > 0.85  # 合理的SOC预测水平
tensorboard日志可打开（运行 tensorboard --logdir experiments/）
checkpoints目录有5个.pth文件
```

### 提示

> from torch.utils.tensorboard import SummaryWriter；writer.add_scalar('val/r2', r2, epoch)

---

## P026 Kaggle · 高光谱回归开放赛 ⭐⭐

### 题目描述

在Kaggle上找一个光谱/回归相关的开放数据集（推荐：Soil Properties Prediction Challenge 或 Hyperspectral Imaging相关），用PISFM的思路参赛，提交结果。

### 函数签名

```python
# 目标：Kaggle LB RMSE进入前40%
```

### 约束条件

- 必须用本次重写的PyTorch PISFM代码
- 在Notebook里写清楚：哪些地方和PISFM论文的设计不同
- 提交后截图LB排名

### 验收断言（assert）

```python
进入前40%排名
Notebook有完整EDA（至少3张图）
代码可在Kaggle GPU上独立复现
```

### 提示

> 先baseline（Ridge/RF）定上界，再用神经网络往上推；光谱数据通常需要导数预处理（SNV/MSC）

---

## 本周学习目标

- [ ] 迁移PISFM数据管线到PyTorch
- [ ] 重写BiMamba/BiLSTM Encoder
- [ ] 完整K折实验 + TensorBoard监控
- [ ] Kaggle高光谱比赛提交

## 参考答案

> 见 `../solutions/Week07-参考答案.md`