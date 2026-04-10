# Week 8 参考答案

> 建议完成练习后再查看本答案

---

## P027 TensorBoard完整监控

### 参考代码

```python
"""
P027 TensorBoard完整监控
"""

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter

def train_with_tensorboard(model, loader, writer, epochs=5):
    """
    训练并记录多种指标到TensorBoard
    """
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for batch_idx, (x, y) in enumerate(loader):
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()

            # 记录gradient norm
            grad_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), float('inf')
            )

            optimizer.step()

            # 记录loss
            global_step = epoch * len(loader) + batch_idx
            writer.add_scalar('train/loss', loss.item(), global_step)
            writer.add_scalar('train/grad_norm', grad_norm, global_step)

        # 记录weight histogram
        if epoch % 2 == 0:
            for name, param in model.named_parameters():
                writer.add_histogram(f'weights/{name}', param, epoch)

        # 验证
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in loader:
                out = model(x)
                pred = out.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        acc = correct / total
        writer.add_scalar('val/accuracy', acc, epoch)

    writer.close()

if __name__ == "__main__":
    # 使用示例
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader

    # MNIST
    transform = transforms.Compose([transforms.ToTensor()])
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    # 简单MLP
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10)
    )

    writer = SummaryWriter('runs/experiment_1')
    train_with_tensorboard(model, loader, writer, epochs=5)

    # 启动TensorBoard: tensorboard --logdir=runs
```

---

## P028 模型checkpoint续训

### 参考代码

```python
"""
P028 模型checkpoint续训
"""

import torch

def save_checkpoint(state, path):
    """
    保存checkpoint
    Args:
        state: 包含model_state_dict, optimizer_state_dict, epoch, val_loss的字典
        path: 保存路径
    """
    torch.save(state, path)

def load_checkpoint(path, model, optimizer):
    """
    加载checkpoint
    Returns:
        epoch: 下一个epoch的编号
    """
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'] + 1

def train_with_checkpoint(model, optimizer, train_loader, val_loader,
                          checkpoint_path=None, epochs=10, save_every=5):
    """
    带checkpoint的训练
    """
    start_epoch = 0

    # 尝试加载checkpoint
    if checkpoint_path and os.path.exists(checkpoint_path):
        start_epoch = load_checkpoint(checkpoint_path, model, optimizer)
        print(f"Resumed from epoch {start_epoch}")

    for epoch in range(start_epoch, epochs):
        # 训练
        train_loss = train_one_epoch(model, optimizer, train_loader)
        val_loss = validate(model, val_loader)

        print(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")

        # 定期保存
        if (epoch + 1) % save_every == 0:
            save_checkpoint({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss
            }, f'checkpoint_epoch_{epoch}.pth')

    # 最终保存
    save_checkpoint({
        'epoch': epochs - 1,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'val_loss': val_loss
    }, 'checkpoint_final.pth')
```

---

## P029 迁移学习微调

### 参考代码

```python
"""
P029 迁移学习微调
"""

import torch
import torch.nn as nn
from torchvision import models

def finetune_resnet(num_classes=10, freeze_layers=3):
    """
    微调ResNet-18
    Args:
        num_classes: 分类数
        freeze_layers: 冻结前几层
    """
    # 加载预训练模型
    model = models.resnet18(pretrained=True)

    # 冻结前几层
    layers_to_freeze = list(model.children())[:freeze_layers]
    for layer in layers_to_freeze:
        for param in layer.parameters():
            param.requires_grad = False

    # 修改分类头
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    # 统计参数
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Total params: {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")
    print(f"Trainable ratio: {trainable_params/total_params:.2%}")

    return model

def train_finetune(model, train_loader, val_loader, epochs=5):
    """微调训练"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    # 只优化requires_grad=True的参数
    optimizer = torch.optim.SGD(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=0.01, momentum=0.9
    )
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        # 验证
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                pred = out.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        acc = correct / total
        print(f"Epoch {epoch}: val_acc={acc:.4f}")

    return model
```

---

## P030 最终项目 · PISFM论文实验复现

### 项目结构

```
experiments/
├── final_results.md       # 结果表格
├── checkpoints/
│   ├── bilstm_fold_0.pth
│   ├── bilstm_fold_1.pth
│   └── ...
├── results.json
└── run.sh                 # 一键复现脚本
```

### run.sh 示例

```bash
#!/bin/bash

# 运行所有实验
echo "Running PISFM experiments..."

# 数据预处理
python preprocess.py

# 训练各个模型
python train_baseline_mlp.py
python train_baseline_svr.py
python train_bilstm.py

# 汇总结果
python summarize_results.py

echo "Experiments completed!"
```

### results.md 格式

```markdown
# PISFM实验结果

| Model | R²↑ | RMSE↓ | MAE↓ |
|-------|-----|-------|------|
| Linear Regression | 0.72 | 0.85 | 0.62 |
| SVR | 0.78 | 0.76 | 0.55 |
| MLP | 0.82 | 0.68 | 0.48 |
| BiLSTM (ours) | 0.87 | 0.58 | 0.42 |
```