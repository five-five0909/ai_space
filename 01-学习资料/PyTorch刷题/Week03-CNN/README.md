# Week 3 · CNN

> 卷积神经网络，感受野与归一化

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P009 | 卷积感受野计算器 | Easy | CNN、Conv2d |
| P010 | 手写BatchNorm1d | Hard | CNN、BatchNorm |
| P011 | Mini-ResNet训练CIFAR-10 | Medium | CNN、ResNet、训练循环 |
| P012 | Kaggle · Digit Recognizer CNN | Medium | CNN、Kaggle |

---

## P009 卷积感受野计算器 ⭐

### 题目描述

给定一系列Conv2d层的参数(kernel, stride, padding)，计算最终的感受野大小，不能直接跑网络，用公式推导。

### 函数签名

```python
def calc_receptive_field(layers: list[dict]) -> int:
    # layers = [{'k':3,'s':1,'p':1}, ...]
```

### 约束条件

- 纯Python计算，不实例化任何nn.Module
- 支持任意层数
- 返回最终感受野（整数）

### 验收断言（assert）

```python
calc_receptive_field([{'k':3,'s':1,'p':0}]) == 3
calc_receptive_field([{'k':3,'s':1,'p':0},{'k':3,'s':1,'p':0}]) == 5
calc_receptive_field([{'k':3,'s':2,'p':0},{'k':3,'s':1,'p':0}]) == 7
```

### 提示

> RF_new = RF_old + (k-1)*stride_product，stride_product是前面所有层stride的乘积

---

## P010 手写BatchNorm1d ⭐⭐⭐

### 题目描述

不用 nn.BatchNorm1d，手动实现：训练时用batch统计量，eval时用running mean/var，通过 self.training 标志切换。

### 函数签名

```python
class MyBN1d(nn.Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        ...
```

### 约束条件

- 必须有 self.weight(gamma) 和 self.bias(beta) 作为可学习参数
- running_mean / running_var 用 register_buffer 注册（不是Parameter）
- model.eval() 后输出与 nn.BatchNorm1d 在 atol=1e-4 内一致

### 验收断言（assert）

```python
my_bn.training == True时用batch统计量
my_bn.eval()
torch.allclose(my_bn(x), ref_bn(x), atol=1e-4)
my_bn.running_mean 在每个batch后更新
```

### 提示

> training: out=(x-x.mean(0))/sqrt(x.var(0)+eps)；eval: out=(x-running_mean)/sqrt(running_var+eps)，然后乘gamma加beta

---

## P011 Mini-ResNet训练CIFAR-10 ⭐⭐

### 题目描述

搭一个3层残差Block的ResNet（约40万参数），在CIFAR-10上训练10个epoch，验证集accuracy > 70%。

### 函数签名

```python
class ResBlock(nn.Module):
    ...

class MiniResNet(nn.Module):
    ...
```

### 约束条件

- 总参数量在350k~500k之间
- 必须包含：Conv→BN→ReLU→Conv→BN + shortcut
- 10个epoch内val acc > 70%（lr=0.01, SGD+momentum=0.9）

### 验收断言（assert）

```python
350000 <= sum(p.numel() for p in model.parameters()) <= 500000
val_acc_epoch10 > 0.70
loss曲线单调下降（允许小波动）
```

### 提示

> shortcut用1×1 Conv调整通道数；第一个block后加MaxPool(2)降分辨率

---

## P012 Kaggle · Digit Recognizer CNN ⭐⭐

### 题目描述

用Mini-ResNet或自定义CNN做MNIST Digit Recognizer，Kaggle LB > 0.99。这是第一个有明确分数目标的Kaggle题。

### 函数签名

```python
# 目标：Kaggle public LB accuracy > 0.99
```

### 约束条件

- 网络用PyTorch nn.Module搭建
- 必须有数据增强（RandomRotation + RandomAffine至少一种）
- Notebook在Kaggle上可运行（非本地跑完上传）

### 验收断言（assert）

```python
Kaggle LB > 0.990
参数量 < 2M
训练时间 < 30min（Kaggle T4 GPU）
```

### 提示

> LeNet结构就能过0.99；如果卡在0.98，加Dropout(0.5)和数据增强一般能推上去

---

## 本周学习目标

- [ ] 理解感受野的计算公式
- [ ] 手写BatchNorm理解train/eval模式
- [ ] 实现残差连接
- [ ] Kaggle LB > 0.99

## 参考答案

> 见 `../solutions/Week03-参考答案.md`