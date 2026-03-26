# 11. 正则化/防过拟合

## Dropout（随机丢弃）

**核心思想**：训练时随机将神经元输出置零，防止神经元过度依赖。

**训练和推理的区别**：
- 训练：$y_i = x_i \cdot m_i$，其中$m_i \sim \text{Bernoulli}(1-p)$
- 推理：$y_i = x_i \cdot (1-p)$（期望保持一致）

**Inverted Dropout**：训练时除以$(1-p)$，推理时不处理，更常用。

**公式**：
$$\text{Dropout}(x) = \frac{x \cdot m}{1-p}, \quad m \sim \text{Bernoulli}(1-p)$$

**为什么有效**：强制网络学习冗余表示，提高泛化能力。

**PyTorch代码**：
```python
import torch.nn as nn

# Inverted Dropout（PyTorch默认）
dropout = nn.Dropout(p=0.5)
x = torch.randn(10, 20)
output = dropout(x)  # 训练时自动启用
# model.eval()后自动禁用
```

**推荐论文**：
1. Srivastava, N., et al. (2014). Dropout: A simple way to prevent neural networks from overfitting.
2. Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian approximation.
3. Wan, L., et al. (2013). Regularization of neural networks using dropconnect.

## DropPath / Stochastic Depth

**核心思想**：随机删除整个残差块（ResNet）或Transformer层。

**公式**：
$$y = \begin{cases}
x + F(x) & \text{with probability } p \\
x & \text{with probability } 1-p
\end{cases}$$

**与Dropout区别**：Dropout作用于神经元，DropPath作用于整个模块。

**为什么有效**：强制网络学习浅层和深层的鲁棒性。

**PyTorch代码**：
```python
class DropPath(nn.Module):
    def __init__(self, drop_prob=0.):
        super().__init__()
        self.drop_prob = drop_prob
    
    def forward(self, x):
        if self.drop_prob == 0. or not self.training:
            return x
        keep_prob = 1 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        random_tensor.floor_()  # binarize
        output = x.div(keep_prob) * random_tensor
        return output

# 使用
drop_path = DropPath(drop_prob=0.1)
residual = drop_path(block_output)
```

**推荐论文**：
1. Huang, G., et al. (2016). Deep networks with stochastic depth.
2. Fan, A., et al. (2020). Reducing transformer depth on demand with structured dropout.
3. Han, X., et al. (2022). DP-Transformer: Better generalization by differential privacy.

## Label Smoothing（软化标签）

**核心思想**：将硬标签（one-hot）转换为软标签，减少过拟合。

**公式**：
$$y_i^{smooth} = \begin{cases}
1 - \epsilon & \text{if } i = \text{true class} \\
\epsilon / (K-1) & \text{otherwise}
\end{cases}$$

其中$\epsilon$是平滑因子，$K$是类别数。

**为什么有效**：防止模型对正确类别过于自信，提高校准性。

**PyTorch代码**：
```python
class LabelSmoothingLoss(nn.Module):
    def __init__(self, smoothing=0.1, dim=-1):
        super().__init__()
        self.smoothing = smoothing
        self.dim = dim
    
    def forward(self, pred, target):
        pred = pred.log_softmax(dim=self.dim)
        with torch.no_grad():
            true_dist = torch.zeros_like(pred)
            true_dist.fill_(self.smoothing / (pred.size(1) - 1))
            true_dist.scatter_(1, target.data.unsqueeze(1), 1 - self.smoothing)
        return torch.mean(torch.sum(-true_dist * pred, dim=self.dim))

# 使用
criterion = LabelSmoothingLoss(smoothing=0.1)
loss = criterion(outputs, targets)
```

**推荐论文**：
1. Szegedy, C., et al. (2016). Rethinking the inception architecture for computer vision.
2. Müller, R., et al. (2019). When does label smoothing help?
3. Pereyra, G., et al. (2017). Regularizing neural networks by penalizing confident output distributions.

## Weight Decay（权重衰减）

**核心思想**：在损失函数中添加L2正则项，惩罚大权重。

**公式**：
$$\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda \sum_i \theta_i^2$$

**与L2正则化关系**：在SGD中等价，在Adam中需要解耦（见AdamW）。

**为什么有效**：鼓励小权重，简化模型复杂度。

**PyTorch代码**：
```python
# SGD中的weight_decay等价于L2正则化
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)

# AdamW中的weight_decay是解耦的
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

**推荐论文**：
1. Krogh, A., & Hertz, J. A. (1992). A simple weight decay can improve generalization.
2. Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization.
3. Zhang, C., et al. (2017). Understanding deep learning requires rethinking generalization.

## Data Augmentation

**核心思想**：通过对输入数据进行变换生成新样本，增加数据多样性。

**常见方法**：
- 图像：旋转、裁剪、翻转、色彩抖动
- 文本：同义词替换、随机删除、回译
- 音频：加噪、变速、变调

**为什么有效**：增加训练数据的多样性，提高模型鲁棒性。

**PyTorch代码**：
```python
# 图像增强示例
from torchvision import transforms

train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor()
])

# 文本增强需要自定义
def synonym_replacement(text, n=1):
    # 实现同义词替换
    pass
```

**推荐论文**：
1. Shorten, C., & Khoshgoftaar, T. M. (2019). A survey on image data augmentation.
2. Wei, J., & Zou, K. (2019). EDA: Easy data augmentation techniques for boosting performance.
3. Cubuk, E. D., et al. (2020). Randaugment: Practical automated data augmentation.

## Mixup（混合样本）

**核心思想**：线性插值两个样本及其标签。

**公式**：
$$\tilde{x} = \lambda x_i + (1-\lambda) x_j$$
$$\tilde{y} = \lambda y_i + (1-\lambda) y_j$$

其中$\lambda \sim \text{Beta}(\alpha, \alpha)$。

**为什么有效**：鼓励模型在样本间线性插值，提高泛化能力。

**PyTorch代码**：
```python
def mixup_data(x, y, alpha=1.0):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size()[0]
    index = torch.randperm(batch_size)
    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

def mixup_criterion(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

# 使用
inputs, targets_a, targets_b, lam = mixup_data(inputs, targets)
outputs = model(inputs)
loss = mixup_criterion(criterion, outputs, targets_a, targets_b, lam)
```

**推荐论文**：
1. Zhang, H., et al. (2018). mixup: Beyond empirical risk minimization.
2. Verma, V., et al. (2019). Manifold mixup: Better representations by interpolating hidden states.
3. Yun, S., et al. (2019). CutMix: Regularization strategy to train strong classifiers.

## CutMix（剪贴区域混合）

**核心思想**：从一个图像中裁剪区域，粘贴到另一个图像上，标签按面积比例混合。

**公式**：
$$\tilde{x} = M \odot x_i + (1-M) \odot x_j$$
$$\tilde{y} = \frac{|M|}{HW} y_i + (1 - \frac{|M|}{HW}) y_j$$

其中$M$是二值掩码，$|M|$是掩码面积。

**为什么有效**：结合了区域dropout和mixup的优点，定位能力更强。

**PyTorch代码**：
```python
def cutmix_data(x, y, beta=1.0):
    lam = np.random.beta(beta, beta)
    rand_index = torch.randperm(x.size()[0])
    target_a = y
    target_b = y[rand_index]
    
    bbx1, bby1, bbx2, bby2 = rand_bbox(x.size(), lam)
    x[:, :, bbx1:bbx2, bby1:bby2] = x[rand_index, :, bbx1:bbx2, bby1:bby2]
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size()[-1] * x.size()[-2]))
    return x, target_a, target_b, lam

def rand_bbox(size, lam):
    W = size[2]
    H = size[3]
    cut_rat = np.sqrt(1. - lam)
    cut_w = np.int(W * cut_rat)
    cut_h = np.int(H * cut_rat)
    cx = np.random.randint(W)
    cy = np.random.randint(H)
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)
    return bbx1, bby1, bbx2, bby2
```

**推荐论文**：
1. Yun, S., et al. (2019). CutMix: Regularization strategy to train strong classifiers.
2. Singh, R. R., et al. (2022). Puzzle Mix: Exploiting saliency and local statistics for optimal mixup.
3. Uddin, M. Z., et al. (2021). Saliency CutMix for object localization.

## R-Drop（两次前向+KL散度）

**核心思想**：同一输入做两次前向传播，用KL散度约束输出分布一致性。

**公式**：
$$\mathcal{L}_{R-drop} = \mathcal{L}_{CE}(y, p_1) + \mathcal{L}_{CE}(y, p_2) + \alpha \cdot \text{KL}(p_1 \| p_2)$$

其中$p_1, p_2$是两次dropout后的输出分布。

**为什么有效**：减少模型预测的方差，提高稳定性。

**PyTorch代码**：
```python
def rdrop_loss(logits1, logits2, targets, alpha=1.0):
    ce_loss = F.cross_entropy(logits1, targets) + F.cross_entropy(logits2, targets)
    p1 = F.log_softmax(logits1, dim=-1)
    p2 = F.log_softmax(logits2, dim=-1)
    kl_loss = F.kl_div(p1, p2, reduction='batchmean') + F.kl_div(p2, p1, reduction='batchmean')
    return ce_loss + alpha * kl_loss

# 使用
logits1 = model(inputs)
logits2 = model(inputs)  # 第二次前向
loss = rdrop_loss(logits1, logits2, targets)
```

**推荐论文**：
1. Li, X., et al. (2021). R-Drop: Regularized dropout for neural networks.
2. Wen, Y., et al. (2019). Interpolation consistency training for semi-supervised learning.
3. Xie, Q., et al. (2020). Self-training with noisy student improves imagenet classification.

## Early Stopping

**核心思想**：当验证集性能不再提升时，提前停止训练。

**判断标准**：连续`patience`个epoch验证损失没有改善。

**为什么有效**：防止过拟合，节省训练时间。

**PyTorch代码**：
```python
class EarlyStopping:
    def __init__(self, patience=7, verbose=False, delta=0):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
    
    def __call__(self, val_loss, model):
        score = -val_loss
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0
    
    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            print(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}). Saving model...')
        torch.save(model.state_dict(), 'checkpoint.pt')
        self.val_loss_min = val_loss

# 使用
early_stopping = EarlyStopping(patience=10)
for epoch in range(100):
    train_loss = train(...)
    val_loss = validate(...)
    early_stopping(val_loss, model)
    if early_stopping.early_stop:
        print("Early stopping")
        break
```

**推荐论文**：
1. Prechelt, L. (1998). Early stopping - but when?
2. Goodfellow, I., et al. (2016). Deep learning.
3. Caruana, R., et al. (2001). Overfitting in neural nets: Backpropagation, conjugate gradient, and early stopping.

## Gradient Clipping（梯度裁剪）

**核心思想**：限制梯度范数，防止梯度爆炸。

**公式**：
$$g = \begin{cases}
g & \text{if } \|g\| \leq \text{max\_norm} \\
\frac{\text{max\_norm}}{\|g\|} g & \text{otherwise}
\end{cases}$$

**为什么有效**：稳定训练过程，尤其对RNN和Transformer重要。

**PyTorch代码**：
```python
# 梯度裁剪
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 或者在optimizer.step()前
optimizer.zero_grad()
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
optimizer.step()
```

**推荐论文**：
1. Pascanu, R., et al. (2013). On the difficulty of training recurrent neural networks.
2. Zhang, H., et al. (2020). Gradient clipping can mitigate catastrophic forgetting.
3. Gehring, J., et al. (2017). Convolutional sequence to sequence learning.

## EMA (Exponential Moving Average)

**核心思想**：维护参数的指数滑动平均，用于推理时获得更稳定的模型。

**公式**：
$$\theta_{\text{ema}} = \beta \cdot \theta_{\text{ema}} + (1-\beta) \cdot \theta$$

其中$\beta$是衰减率（如0.999）。

**为什么有效**：平滑参数更新，减少训练噪声的影响。

**PyTorch代码**：
```python
class EMA:
    def __init__(self, model, decay=0.999):
        self.model = model
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        self.register()
    
    def register(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()
    
    def update(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                new_average = (1.0 - self.decay) * param.data + self.decay * self.shadow[name]
                self.shadow[name] = new_average.clone()
    
    def apply_shadow(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                self.backup[name] = param.data
                param.data = self.shadow[name]
    
    def restore(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.backup
                param.data = self.backup[name]
        self.backup = {}

# 使用
ema = EMA(model, decay=0.999)
for epoch in range(100):
    train(...)
    ema.update()  # 每个step或epoch后更新

# 推理时
ema.apply_shadow()
evaluate(model)
ema.restore()
```

**推荐论文**：
1. Polyak, B. T., & Juditsky, A. B. (1992). Acceleration of stochastic approximation by averaging.
2. Izmailov, P., et al. (2018). Averaging weights leads to wider optima and better generalization.
3. Tarvainen, A., & Valpola, S. (2017). Mean teachers are better role models.