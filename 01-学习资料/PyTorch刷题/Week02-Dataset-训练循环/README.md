# Week 2 · Dataset + 训练循环

> 数据管线搭建，从零实现核心组件

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P005 | 自定义高光谱Dataset | Medium | Dataset、DataLoader |
| P006 | DataLoader碰撞检测 | Easy | DataLoader |
| P007 | 从零实现Linear层 | Hard | nn.Module、Parameter |
| P008 | Kaggle · Titanic纯Tensor基线 | Medium | Tensor、Kaggle |

---

## P005 自定义高光谱Dataset ⭐⭐

### 题目描述

把你的PISFM CSV数据（前n-1列为光谱特征，最后1列为SOC标签）包装成 PyTorch Dataset，支持 train/val 分割，实现 __len__ 和 __getitem__。

### 函数签名

```python
class SpectralDataset(Dataset):
    def __init__(self, csv_path, split='train', val_ratio=0.2, seed=42):
        ...
```

### 约束条件

- __getitem__ 返回 (features: FloatTensor, label: FloatTensor)
- features需z-score标准化（用训练集统计量，val集用同一套mean/std）
- 不允许在__getitem__里读文件（必须在__init__里一次性加载）

### 验收断言（assert）

```python
len(train_ds) + len(val_ds) == total_samples
train_ds[0][0].dtype == torch.float32
val_ds均值/std与train_ds的 .mean_ 和 .std_ 属性一致
```

### 提示

> 在__init__里split好indices，存self.X和self.y；用训练集fit的mean/std同时transform val集

---

## P006 DataLoader碰撞检测 ⭐

### 题目描述

用MNIST构建DataLoader(batch_size=64, shuffle=True)，验证：两个epoch里同一位置的batch不完全相同（shuffle生效），且所有epoch合计样本数=60000。

### 函数签名

```python
def verify_dataloader(loader) -> dict:
```

### 约束条件

- 必须跑满2个epoch
- 返回 {'total_samples': int, 'shuffle_works': bool}
- 不允许设置 generator/seed（要真随机）

### 验收断言（assert）

```python
result['total_samples'] == 60000
result['shuffle_works'] == True
```

### 提示

> 记录第一个epoch第一个batch的indices，第二个epoch再取，用 torch.equal 比较

---

## P007 从零实现Linear层 ⭐⭐⭐

### 题目描述

不用 nn.Linear，用 nn.Parameter 手动创建 weight(out,in) 和 bias(out)，实现 forward，验证与 nn.Linear 结果在 atol=1e-5 内一致，且反向传播可以正常更新参数。

### 函数签名

```python
class MyLinear(nn.Module):
    def __init__(self, in_features, out_features):
        ...
```

### 约束条件

- weight初始化：kaiming_uniform_；bias初始化：zeros_
- 必须实现 extra_repr() 返回 'in_features=X, out_features=Y'
- forward输出shape=(batch, out_features)

### 验收断言（assert）

```python
torch.allclose(my_linear(x), ref_linear(x), atol=1e-5)  # 在同权重下成立
len(list(my_linear.parameters())) == 2
my_linear.extra_repr() == 'in_features=8, out_features=4'
```

### 提示

> F.linear(input, self.weight, self.bias) 就是nn.Linear的forward，但你要手写成 input @ self.weight.T + self.bias

---

## P008 Kaggle · Titanic纯Tensor基线 ⭐⭐

### 题目描述

用纯Tensor（不用nn.Module）实现Titanic生存预测：手动梯度下降100步，提交到Kaggle，要求 accuracy > 0.75。

### 函数签名

```python
# 输入: train.csv / test.csv
# 输出: submission.csv
```

### 约束条件

- 只允许用 torch.Tensor 和 autograd，不能用 nn / optim
- 特征工程：至少处理 Pclass、Sex、Age（fillna）、Fare
- 二分类：sigmoid + BCELoss手动实现

### 验收断言（assert）

```python
train accuracy > 0.78  # 过拟合没关系，先跑通
submission.csv格式正确：PassengerId,Survived
Kaggle public LB > 0.75
```

### 提示

> 把Sex映射成0/1，Age用中位数填充，然后拼成(N,4)的feature矩阵

---

## 本周学习目标

- [ ] 掌握自定义Dataset的写法
- [ ] 理解DataLoader的shuffle机制
- [ ] 从零实现nn.Linear（理解Parameter）
- [ ] 完成第一个Kaggle提交

## 参考答案

> 见 `../solutions/Week02-参考答案.md`