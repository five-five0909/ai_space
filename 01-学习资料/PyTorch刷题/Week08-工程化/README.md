# Week 8 · 工程化

> 模型管理、迁移学习、最终项目

## 本章题目

| 题号 | 标题 | 难度 | 核心知识点 |
|------|------|------|-----------|
| P027 | TensorBoard完整监控 | Easy | 工程、TensorBoard |
| P028 | 模型checkpoint续训 | Easy | 工程、模型保存 |
| P029 | 迁移学习微调 | Medium | 迁移学习、工程 |
| P030 | 最终项目 · PISFM论文实验复现 | Hard | PISFM实战、工程、最终项目 |

---

## P027 TensorBoard完整监控 ⭐

### 题目描述

在任意之前的训练循环里接入TensorBoard，监控：loss、accuracy、gradient norm（检测梯度爆炸）、weight histogram（检测死神经元），跑5个epoch。

### 函数签名

```python
def train_with_tensorboard(model, loader, writer, epochs=5):
    ...
```

### 约束条件

- gradient norm用 torch.nn.utils.clip_grad_norm_ 计算（不clip，只记录）
- weight histogram每2个epoch记录一次
- writer.add_scalar的tag命名规范：'train/loss', 'val/acc' 等

### 验收断言（assert）

```python
TensorBoard可打开，有4种metric曲线
gradient norm在前3epoch内不超过10.0  # 否则说明需要clip
weight histogram显示分布随epoch变化
```

### 提示

> norm=torch.nn.utils.clip_grad_norm_(model.parameters(), float('inf'))即不clip只算norm

---

## P028 模型checkpoint续训 ⭐

### 题目描述

实现带checkpoint的训练：每5个epoch保存一次（含model state、optimizer state、epoch、val_loss），支持从任意checkpoint恢复继续训练，最终结果与不中断训练一致。

### 函数签名

```python
def save_checkpoint(state, path):
    ...

def load_checkpoint(path, model, optimizer) -> int:
    ...
```

### 约束条件

- checkpoint必须包含：model_state_dict、optimizer_state_dict、epoch、val_loss
- 恢复后继续训练5个epoch，最终val_loss与连续训练误差 < 0.01
- 不允许保存整个model对象（只保存state_dict）

### 验收断言（assert）

```python
checkpoint文件可用 torch.load 读取并包含4个key
恢复后的epoch编号正确延续
val_loss_resumed ≈ val_loss_continuous（atol=0.01）
```

### 提示

> torch.save({'epoch':e,'model_state_dict':model.state_dict(),...}, path)；加载后model.load_state_dict(ckpt['model_state_dict'])

---

## P029 迁移学习微调 ⭐⭐

### 题目描述

用 torchvision 的 ResNet-18（pretrained），冻结前3层，只微调最后1个ResBlock + 分类头，在CIFAR-10上训练5个epoch，val accuracy > 85%。

### 函数签名

```python
def finetune_resnet(num_classes=10, freeze_layers=3) -> nn.Module:
```

### 约束条件

- 用 param.requires_grad=False 冻结参数
- optimizer只传requires_grad=True的参数
- 打印：可训练参数量 vs 总参数量，可训练比例 < 40%

### 验收断言（assert）

```python
val_acc > 0.85 in 5 epochs
trainable_params / total_params < 0.40
optimizer.param_groups[0]['params']数量 == 可训练参数数量
```

### 提示

> for name,param in model.named_parameters(): 遍历，根据name判断层号决定是否freeze

---

## P030 最终项目 · PISFM论文实验复现 ⭐⭐⭐

### 题目描述

把你PISFM论文的完整实验用PyTorch复现：数据管线 + BiMamba/BiLSTM Encoder + K折 + 对比baseline（MLP、SVR）+ 结果表格，输出可直接放论文附录的markdown表格。

### 函数签名

```python
# 最终输出：
# - experiments/final_results.md（含R²/RMSE/MAE对比表）
# - 所有模型的checkpoint
# - 可复现的run.sh
```

### 约束条件

- 必须包含至少3个baseline对比（MLP、Linear Regression、SVR）
- 表格格式：Model | R²↑ | RMSE↓ | MAE↓
- run.sh一键复现：bash run.sh → 自动跑完所有实验输出results.md

### 验收断言（assert）

```python
BiMamba/BiLSTM的R² > MLP的R²
results.md格式正确，可直接粘贴到论文
run.sh在干净环境下可运行（无硬编码路径）
```

### 提示

> SVR用sklearn；MLP用本课写的；只有BiMamba用PyTorch；结果汇总用pandas to_markdown()

---

## 本周学习目标

- [ ] TensorBoard监控多种指标
- [ ] 实现checkpoint续训机制
- [ ] 掌握迁移学习微调
- [ ] 完成PISFM论文实验复现

## 参考答案

> 见 `../solutions/Week08-参考答案.md`