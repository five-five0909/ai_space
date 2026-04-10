# Week 6 · 调优技巧

> 学习率调度、K折验证、混合精度

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P019 | 学习率调度对比实验 | Easy | 调优、LR Scheduler |
| P020 | K折交叉验证框架 | Medium | 调优、K折 |
| P021 | 混合精度训练加速 | Medium | 调优、AMP |
| P022 | Kaggle · 任选一题调优提分 | Medium | 调优、Kaggle |

---

## P019 学习率调度对比实验 ⭐

### 题目描述

在同一个MLP+MNIST设置下，对比3种学习率策略（StepLR、CosineAnnealingLR、ReduceLROnPlateau），用matplotlib画出3条val loss曲线在同一图上。

### 函数签名

```python
def compare_schedulers(model_fn, train_loader, val_loader, epochs=15) -> dict:
```

### 约束条件

- 3个模型必须完全相同初始化（同seed）
- 返回 {'step': [val_losses], 'cosine': [...], 'plateau': [...]}
- 最终图保存为 scheduler_compare.png

### 验收断言（assert）

```python
所有3条曲线的初始val_loss在 ±0.05 范围内  # 验证同初始化
cosine的最终val_loss <= step的最终val_loss  # 通常如此
图中有图例和xlabel/ylabel
```

### 提示

> 用 copy.deepcopy(initial_state_dict) 保证3个模型同初始化

---

## P020 K折交叉验证框架 ⭐⭐

### 题目描述

实现一个通用K折CV框架，接受任意 nn.Module 和 Dataset，返回每折的val loss和mean±std，适配你的PISFM高光谱数据。

### 函数签名

```python
def kfold_cv(
    model_fn: Callable,
    dataset: Dataset,
    k: int = 5,
    epochs: int = 30,
    **train_kwargs
) -> dict:
```

### 约束条件

- 每折重新初始化模型（调用 model_fn()）
- 返回 {'fold_losses': list, 'mean': float, 'std': float}
- 支持 early_stopping（patience参数）

### 验收断言（assert）

```python
len(result['fold_losses']) == k
各折的 train/val 不重叠  # 用KFold indices验证
result['std'] < result['mean'] * 0.5  # std不超过均值一半
```

### 提示

> from sklearn.model_selection import KFold；split dataset indices，再用SubsetRandomSampler构造DataLoader

---

## P021 混合精度训练加速 ⭐⭐

### 题目描述

在Mini-ResNet+CIFAR-10上对比 FP32 vs AMP(torch.cuda.amp) 的训练速度（time.time），验证AMP加速比 > 1.3x，且精度损失 < 1%。

### 函数签名

```python
def train_with_amp(model, loader, epochs=5) -> dict:
    # 返回 {'time': float, 'final_acc': float}
```

### 约束条件

- 必须用 GradScaler + autocast
- 对比时用同一个seed初始化模型
- 只在有CUDA GPU时运行（有guard：if not torch.cuda.is_available(): skip）

### 验收断言（assert）

```python
time_amp < time_fp32 * 0.77  # 即加速比>1.3x
abs(acc_amp - acc_fp32) < 0.01
GradScaler的scale在训练中保持 > 1.0
```

### 提示

> with torch.cuda.amp.autocast(): output=model(x); loss=criterion(output,y); scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()

---

## P022 Kaggle · 任选一题调优提分 ⭐⭐

### 题目描述

回到Week 3–5任意一题的Kaggle，应用本周学到的技巧（LR scheduler + K折 + AMP），提交新版本，成绩必须高于上次。

### 函数签名

```python
# 目标：Kaggle LB比第一次提交提升 >= 0.005
```

### 约束条件

- 必须应用至少2项本周新技巧
- 在Notebook里记录：哪个改动带来了多少提升
- 提交history里要有前后两次记录

### 验收断言（assert）

```python
新提交score > 旧提交score
Notebook有ablation记录（去掉某技巧后的分数对比）
```

### 提示

> 最容易提分的顺序：数据增强 > LR scheduler > K折ensemble > AMP（AMP主要省时间）

---

## 本周学习目标

- [ ] 对比三种学习率调度策略
- [ ] 实现通用K折交叉验证框架
- [ ] 掌握混合精度训练
- [ ] Kaggle提分实战

## 参考答案

> 见 `../solutions/Week06-参考答案.md`