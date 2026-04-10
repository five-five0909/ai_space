# Week 7 参考答案

> 建议完成练习后再查看本答案

---

## P023 PISFM数据管线PyTorch化

### 参考代码

```python
"""
P023 PISFM数据管线PyTorch化
"""

import torch
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

class PISFMDataModule:
    def __init__(self, csv_path, k=5, batch_size=32):
        """
        PISFM数据模块
        Args:
            csv_path: CSV文件路径
            k: K折交叉验证折数
            batch_size: 批大小
        """
        self.csv_path = csv_path
        self.k = k
        self.batch_size = batch_size

        # 读取数据
        df = pd.read_csv(csv_path)
        self.X = df.iloc[:, :-1].values  # 光谱特征
        self.y = df.iloc[:, -1].values   # SOC标签
        self.n_samples = len(self.X)

        # K折划分
        self.kf = KFold(n_splits=k, shuffle=True, random_state=42)
        self.fold_indices = list(self.kf.split(range(self.n_samples)))

    def get_fold(self, fold_idx):
        """
        获取指定折的DataLoader
        Returns:
            (train_loader, val_loader)
        """
        train_idx, val_idx = self.fold_indices[fold_idx]

        # 计算训练集归一化参数
        X_train = self.X[train_idx]
        mean = X_train.mean(axis=0)
        std = X_train.std(axis=0)

        # 创建Dataset
        train_ds = PISFMDataset(self.X[train_idx], self.y[train_idx], mean, std)
        val_ds = PISFMDataset(self.X[val_idx], self.y[val_idx], mean, std)

        # 创建DataLoader
        train_loader = DataLoader(
            train_ds, batch_size=self.batch_size,
            shuffle=True, pin_memory=torch.cuda.is_available()
        )
        val_loader = DataLoader(
            val_ds, batch_size=self.batch_size,
            shuffle=False, pin_memory=torch.cuda.is_available()
        )

        return train_loader, val_loader

class PISFMDataset(Dataset):
    def __init__(self, X, y, mean, std):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        self.mean = torch.tensor(mean, dtype=torch.float32)
        self.std = torch.tensor(std, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = (self.X[idx] - self.mean) / (self.std + 1e-8)
        return x, self.y[idx]
```

---

## P024 BiMamba Encoder迁移

### 参考代码

```python
"""
P024 BiMamba/BiLSTM Encoder
"""

import torch
import torch.nn as nn

class BiLSTMEncoder(nn.Module):
    """
    用BiLSTM近似BiMamba
    """
    def __init__(self, input_dim, hidden_dim, num_layers=2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # 输入投影
        self.input_proj = nn.Linear(input_dim, hidden_dim)

        # BiLSTM
        self.lstm = nn.LSTM(
            hidden_dim, hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True
        )

    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, input_dim)
        Returns:
            (batch, seq_len, hidden_dim*2)
        """
        # 输入投影
        x = self.input_proj(x)

        # BiLSTM
        out, _ = self.lstm(x)

        return out

    def load_keras_weights(self, keras_model):
        """
        从Keras模型加载权重
        注意：Keras LSTM权重顺序是[i,f,c,o]，PyTorch是[i,f,g,o]
        """
        # 这里需要根据具体Keras模型结构调整
        pass
```

---

## P025 完整PISFM训练实验

### 解题思路

1. 数据管线：使用P023的PISFMDataModule
2. 模型：使用P024的BiLSTMEncoder
3. 训练：K折CV + 早停 + TensorBoard
4. 输出：results.json + checkpoints

### 关键代码结构

```python
from torch.utils.tensorboard import SummaryWriter

def train_pisfm_fold(model, train_loader, val_loader, fold_idx, epochs, patience):
    """训练单折"""
    writer = SummaryWriter(f'experiments/pisfm_pytorch/tensorboard/fold_{fold_idx}')

    best_loss = float('inf')
    patience_counter = 0

    for epoch in range(epochs):
        # ... 训练代码 ...

        # TensorBoard记录
        writer.add_scalar('train/loss', train_loss, epoch)
        writer.add_scalar('val/loss', val_loss, epoch)
        writer.add_scalar('val/r2', val_r2, epoch)

        # 早停检查
        if val_loss < best_loss:
            best_loss = val_loss
            patience_counter = 0
            # 保存最佳模型
            torch.save(model.state_dict(), f'experiments/pisfm_pytorch/checkpoints/fold_{fold_idx}.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    writer.close()
    return best_r2, best_rmse
```

---

## P026 Kaggle · 高光谱回归开放赛

### 解题思路

1. 找一个光谱/回归相关的Kaggle数据集
2. 使用PISFM思路：BiLSTM + K折
3. 数据预处理：SNV/MSC
4. 目标：前40%