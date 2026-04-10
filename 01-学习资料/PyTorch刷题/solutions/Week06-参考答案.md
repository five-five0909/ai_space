# Week 6 参考答案

> 建议完成练习后再查看本答案

---

## P019 学习率调度对比实验

### 参考代码

```python
"""
P019 学习率调度对比实验
"""

import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import copy

def compare_schedulers(model_fn, train_loader, val_loader, epochs=15):
    """对比三种学习率调度策略"""

    # 初始化模型并保存初始状态
    initial_model = model_fn()
    initial_state = copy.deepcopy(initial_model.state_dict())

    results = {'step': [], 'cosine': [], 'plateau': []}

    # StepLR
    model = model_fn()
    model.load_state_dict(initial_state)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    results['step'] = train_and_record(model, optimizer, scheduler, train_loader, val_loader, epochs)

    # CosineAnnealingLR
    model = model_fn()
    model.load_state_dict(initial_state)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    results['cosine'] = train_and_record(model, optimizer, scheduler, train_loader, val_loader, epochs)

    # ReduceLROnPlateau
    model = model_fn()
    model.load_state_dict(initial_state)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5)
    results['plateau'] = train_and_record_plateau(model, optimizer, scheduler, train_loader, val_loader, epochs)

    # 绘图
    plt.figure(figsize=(10, 6))
    for name, losses in results.items():
        plt.plot(losses, label=name)
    plt.xlabel('Epoch')
    plt.ylabel('Validation Loss')
    plt.legend()
    plt.title('LR Scheduler Comparison')
    plt.savefig('scheduler_compare.png')
    plt.close()

    return results

def train_and_record(model, optimizer, scheduler, train_loader, val_loader, epochs):
    """训练并记录val loss"""
    val_losses = []
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        # Train
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        # Validate
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for x, y in val_loader:
                out = model(x)
                val_loss += criterion(out, y).item()
        val_losses.append(val_loss / len(val_loader))

        scheduler.step()

    return val_losses

def train_and_record_plateau(model, optimizer, scheduler, train_loader, val_loader, epochs):
    """ReduceLROnPlateau需要传入val_loss"""
    val_losses = []
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        # Train
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        # Validate
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for x, y in val_loader:
                out = model(x)
                val_loss += criterion(out, y).item()
        avg_val_loss = val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        scheduler.step(avg_val_loss)

    return val_losses
```

---

## P020 K折交叉验证框架

### 参考代码

```python
"""
P020 K折交叉验证框架
"""

import torch
from torch.utils.data import DataLoader, SubsetRandomSampler
from sklearn.model_selection import KFold

def kfold_cv(model_fn, dataset, k=5, epochs=30, patience=10, **train_kwargs):
    """
    K折交叉验证
    Args:
        model_fn: 返回新模型的函数
        dataset: 完整数据集
        k: 折数
        epochs: 每折训练轮数
        patience: 早停耐心值
    Returns:
        {'fold_losses': list, 'mean': float, 'std': float}
    """
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    fold_losses = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(range(len(dataset)))):
        print(f"\n=== Fold {fold+1}/{k} ===")

        # 创建DataLoader
        train_sampler = SubsetRandomSampler(train_idx)
        val_sampler = SubsetRandomSampler(val_idx)

        train_loader = DataLoader(dataset, sampler=train_sampler, **train_kwargs)
        val_loader = DataLoader(dataset, sampler=val_sampler, **train_kwargs)

        # 初始化模型
        model = model_fn()

        # 训练（带早停）
        best_loss = float('inf')
        patience_counter = 0
        fold_val_losses = []

        for epoch in range(epochs):
            # ... 训练代码 ...

            # 早停检查
            if val_loss < best_loss:
                best_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch}")
                    break

        fold_losses.append(best_loss)

    return {
        'fold_losses': fold_losses,
        'mean': torch.tensor(fold_losses).mean().item(),
        'std': torch.tensor(fold_losses).std().item()
    }
```

---

## P021 混合精度训练加速

### 参考代码

```python
"""
P021 混合精度训练加速
"""

import torch
import time

def train_with_amp(model, loader, epochs=5, use_amp=True):
    """训练并返回时间和最终精度"""
    if not torch.cuda.is_available():
        return {'time': 0, 'final_acc': 0}

    device = torch.device('cuda')
    model = model.to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = torch.nn.CrossEntropyLoss()

    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    start_time = time.time()

    for epoch in range(epochs):
        model.train()
        for x, y in loader:
            x, y = x.to(device), y.to(device)

            optimizer.zero_grad()

            # 混合精度
            with torch.cuda.amp.autocast(enabled=use_amp):
                out = model(x)
                loss = criterion(out, y)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

    elapsed = time.time() - start_time

    # 计算精度
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            pred = out.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    return {
        'time': elapsed,
        'final_acc': correct / total
    }

def compare_amp_vs_fp32(model_fn, loader, epochs=5):
    """对比AMP和FP32"""
    # FP32
    model_fp32 = model_fn()
    result_fp32 = train_with_amp(model_fp32, loader, epochs, use_amp=False)

    # AMP
    model_amp = model_fn()
    result_amp = train_with_amp(model_amp, loader, epochs, use_amp=True)

    speedup = result_fp32['time'] / result_amp['time']
    print(f"Speedup: {speedup:.2f}x")
    print(f"FP32 acc: {result_fp32['final_acc']:.4f}")
    print(f"AMP acc: {result_amp['final_acc']:.4f}")

    return result_fp32, result_amp
```