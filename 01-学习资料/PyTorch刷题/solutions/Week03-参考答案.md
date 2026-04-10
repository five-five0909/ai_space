# Week 3 参考答案

> 建议完成练习后再查看本答案

---

## P009 卷积感受野计算器

### 参考代码

```python
"""
P009 卷积感受野计算器
思路：递推公式 RF_new = RF_old + (k-1) * stride_product
"""

def calc_receptive_field(layers: list[dict]) -> int:
    """
    计算最终感受野
    Args:
        layers: [{'k':3,'s':1,'p':1}, ...]
    Returns:
        最终感受野大小
    """
    rf = 1  # 初始感受野（输入层）
    stride_product = 1  # 累计stride乘积

    for layer in layers:
        k = layer['k']
        s = layer['s']

        # 更新感受野
        rf = rf + (k - 1) * stride_product

        # 更新stride乘积
        stride_product *= s

    return rf


if __name__ == "__main__":
    # 测试
    assert calc_receptive_field([{'k':3,'s':1,'p':0}]) == 3
    assert calc_receptive_field([{'k':3,'s':1,'p':0},{'k':3,'s':1,'p':0}]) == 5
    assert calc_receptive_field([{'k':3,'s':2,'p':0},{'k':3,'s':1,'p':0}]) == 7
    print("All tests passed!")
```

---

## P010 手写BatchNorm1d

### 参考代码

```python
"""
P010 手写BatchNorm1d
思路：训练时用batch统计量，eval时用running统计量
"""

import torch
import torch.nn as nn

class MyBN1d(nn.Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum

        # 可学习参数
        self.weight = nn.Parameter(torch.ones(num_features))  # gamma
        self.bias = nn.Parameter(torch.zeros(num_features))   # beta

        # 运行时统计量（不是参数）
        self.register_buffer('running_mean', torch.zeros(num_features))
        self.register_buffer('running_var', torch.ones(num_features))

    def forward(self, x):
        # x shape: (batch, num_features)

        if self.training:
            # 训练模式：用batch统计量
            mean = x.mean(dim=0)
            var = x.var(dim=0, unbiased=False)

            # 更新running统计量
            with torch.no_grad():
                self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
                self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            # 评估模式：用running统计量
            mean = self.running_mean
            var = self.running_var

        # 归一化
        x_norm = (x - mean) / torch.sqrt(var + self.eps)

        # 缩放和平移
        out = self.weight * x_norm + self.bias

        return out


if __name__ == "__main__":
    # 测试
    torch.manual_seed(42)

    my_bn = MyBN1d(10)
    ref_bn = nn.BatchNorm1d(10)

    # 训练模式
    x = torch.randn(4, 10)
    my_bn.train()
    ref_bn.train()

    my_out = my_bn(x)
    ref_out = ref_bn(x)
    print(f"Training mode close: {torch.allclose(my_out, ref_out, atol=1e-4)}")

    # 评估模式
    my_bn.eval()
    ref_bn.eval()

    x2 = torch.randn(4, 10)
    my_out_eval = my_bn(x2)
    ref_out_eval = ref_bn(x2)
    print(f"Eval mode close: {torch.allclose(my_out_eval, ref_out_eval, atol=1e-4)}")
```

---

## P011 Mini-ResNet训练CIFAR-10

### 参考代码

```python
"""
P011 Mini-ResNet
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # shortcut
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

class MiniResNet(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)

        self.layer1 = ResBlock(16, 32, 2)
        self.layer2 = ResBlock(32, 64, 2)
        self.layer3 = ResBlock(64, 128, 2)

        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.adaptive_avg_pool2d(out, 1)
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return out

if __name__ == "__main__":
    model = MiniResNet()
    params = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {params}")
```

---

## P012 Kaggle · Digit Recognizer CNN

### 解题思路

1. 使用LeNet或简单CNN结构
2. 数据增强：RandomRotation + RandomAffine
3. 目标：LB > 0.99

### 提示

- LeNet结构足够达到0.99
- 如果卡在0.98，加Dropout和数据增强
- 在Kaggle Notebook中运行，使用GPU加速