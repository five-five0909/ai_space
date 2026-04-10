# Week 2 参考答案

> 建议完成练习后再查看本答案

---

## P005 自定义高光谱Dataset

### 参考代码

```python
"""
P005 自定义高光谱Dataset
思路：继承Dataset，实现__len__和__getitem__
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np

class SpectralDataset(Dataset):
    def __init__(self, csv_path, split='train', val_ratio=0.2, seed=42):
        """初始化数据集"""
        # 读取CSV
        df = pd.read_csv(csv_path)

        # 分离特征和标签（假设最后一列是标签）
        X = df.iloc[:, :-1].values  # 光谱特征
        y = df.iloc[:, -1].values   # SOC标签

        # 划分训练/验证集
        n_samples = len(X)
        n_val = int(n_samples * val_ratio)

        np.random.seed(seed)
        indices = np.random.permutation(n_samples)

        if split == 'train':
            self.indices = indices[n_val:]
        else:
            self.indices = indices[:n_val]

        # 存储数据
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

        # 计算训练集的归一化参数
        if split == 'train':
            self.mean_ = self.X[self.indices].mean(dim=0)
            self.std_ = self.X[self.indices].std(dim=0)
        # 验证集使用训练集的统计量（需要外部设置）
        else:
            self.mean_ = None
            self.std_ = None

    def set_normalize_params(self, mean, std):
        """设置归一化参数（用于验证集）"""
        self.mean_ = mean
        self.std_ = std

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        actual_idx = self.indices[idx]

        # 获取特征和标签
        features = self.X[actual_idx]
        label = self.y[actual_idx]

        # Z-score归一化
        if self.mean_ is not None and self.std_ is not None:
            features = (features - self.mean_) / (self.std_ + 1e-8)

        return features, label


# 使用示例
if __name__ == "__main__":
    # 创建训练集和验证集
    train_ds = SpectralDataset('data.csv', split='train')
    val_ds = SpectralDataset('data.csv', split='val')

    # 验证集使用训练集的归一化参数
    val_ds.set_normalize_params(train_ds.mean_, train_ds.std_)

    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}")
```

---

## P006 DataLoader碰撞检测

### 参考代码

```python
"""
P006 DataLoader碰撞检测
思路：比较两个epoch的batch是否不同
"""

import torch
from torch.utils.data import DataLoader, TensorDataset

def verify_dataloader(loader) -> dict:
    """验证DataLoader的shuffle功能"""
    total_samples = 0
    first_epoch_batches = []
    second_epoch_batches = []

    # 第一个epoch
    for batch_idx, (data, _) in enumerate(loader):
        total_samples += data.shape[0]
        if batch_idx < 3:  # 只记录前3个batch
            first_epoch_batches.append(data.clone())

    # 第二个epoch
    for batch_idx, (data, _) in enumerate(loader):
        if batch_idx < 3:
            second_epoch_batches.append(data.clone())

    # 检查shuffle是否生效
    shuffle_works = False
    for b1, b2 in zip(first_epoch_batches, second_epoch_batches):
        if not torch.equal(b1, b2):
            shuffle_works = True
            break

    return {
        'total_samples': total_samples,
        'shuffle_works': shuffle_works
    }


if __name__ == "__main__":
    # MNIST测试
    from torchvision import datasets, transforms

    dataset = datasets.MNIST(
        './data', train=True, download=True,
        transform=transforms.ToTensor()
    )

    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    result = verify_dataloader(loader)

    print(f"Total samples: {result['total_samples']}")
    print(f"Shuffle works: {result['shuffle_works']}")

    assert result['total_samples'] == 60000
    assert result['shuffle_works'] == True
```

---

## P007 从零实现Linear层

### 参考代码

```python
"""
P007 从零实现Linear层
思路：用nn.Parameter创建权重，手动实现forward
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class MyLinear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        # 创建可学习参数
        # weight shape: (out_features, in_features)
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))

        # 初始化权重（Kaiming uniform）
        nn.init.kaiming_uniform_(self.weight, a=5**0.5)

    def forward(self, x):
        # x @ weight.T + bias
        return F.linear(x, self.weight, self.bias)

    def extra_repr(self):
        return f'in_features={self.in_features}, out_features={self.out_features}'


if __name__ == "__main__":
    # 测试
    torch.manual_seed(42)

    my_linear = MyLinear(8, 4)
    ref_linear = nn.Linear(8, 4)

    # 复制权重
    with torch.no_grad():
        ref_linear.weight.copy_(my_linear.weight)
        ref_linear.bias.copy_(my_linear.bias)

    # 测试输出
    x = torch.randn(2, 8)
    my_out = my_linear(x)
    ref_out = ref_linear(x)

    print(f"Close: {torch.allclose(my_out, ref_out, atol=1e-5)}")
    print(f"Parameters: {len(list(my_linear.parameters()))}")
    print(f"extra_repr: {my_linear.extra_repr()}")
```

---

## P008 Kaggle · Titanic纯Tensor基线

### 参考代码

```python
"""
P008 Titanic生存预测
思路：纯Tensor实现逻辑回归
"""

import torch
import pandas as pd
import numpy as np

def load_titanic_data(train_path, test_path):
    """加载和预处理数据"""
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)

    def preprocess(df):
        # 特征工程
        df = df.copy()
        df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
        df['Age'] = df['Age'].fillna(df['Age'].median())
        df['Fare'] = df['Fare'].fillna(df['Fare'].median())

        features = ['Pclass', 'Sex', 'Age', 'Fare']
        return df[features].values

    X_train = preprocess(train)
    y_train = train['Survived'].values.reshape(-1, 1)
    X_test = preprocess(test)

    return (
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
        torch.tensor(X_test, dtype=torch.float32)
    )

def sigmoid(x):
    return 1 / (1 + torch.exp(-x))

def bce_loss(y_pred, y_true):
    return -(y_true * torch.log(y_pred + 1e-8) +
             (1 - y_true) * torch.log(1 - y_pred + 1e-8)).mean()

def train_titanic(X, y, lr=0.01, steps=100):
    """训练逻辑回归"""
    n_features = X.shape[1]

    # 初始化参数
    w = torch.randn(n_features, 1, requires_grad=True)
    b = torch.randn(1, requires_grad=True)

    # 标准化特征
    X_mean = X.mean(dim=0)
    X_std = X.std(dim=0)
    X_norm = (X - X_mean) / (X_std + 1e-8)

    for step in range(steps):
        # 前向传播
        logits = X_norm @ w + b
        y_pred = sigmoid(logits)

        # 计算损失
        loss = bce_loss(y_pred, y)

        # 反向传播
        loss.backward()

        # 更新参数
        with torch.no_grad():
            w -= lr * w.grad
            b -= lr * b.grad
            w.grad.zero_()
            b.grad.zero_()

        if step % 20 == 0:
            acc = ((y_pred > 0.5).float() == y).float().mean()
            print(f"Step {step}: Loss={loss.item():.4f}, Acc={acc.item():.4f}")

    return w, b, X_mean, X_std

if __name__ == "__main__":
    X_train, y_train, X_test = load_titanic_data('train.csv', 'test.csv')
    w, b, X_mean, X_std = train_titanic(X_train, y_train, lr=0.1, steps=100)
```