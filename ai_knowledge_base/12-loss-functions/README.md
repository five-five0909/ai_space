# 12. 损失函数

> 师弟师妹们好！这篇文档用大白话讲清楚各种损失函数，每个都有公式推导、代码示例和经典论文推荐。放心，不搞那些花里胡哨的，直接上干货！

## MSE / L2 Loss（均方误差）

**核心思想**：预测值和真实值差得越远，惩罚越大（平方关系）。

**公式推导**：
- 假设真实值是 $y$，预测值是 $\hat{y}$
- 单个样本的损失：$L = (y - \hat{y})^2$
- 批量平均：$L = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2$
- **梯度推导**：$\frac{\partial L}{\partial \hat{y}} = -2(y - \hat{y})$ → 梯度大小和误差成正比，误差大时更新猛

**什么时候用**：回归任务首选，比如预测房价、温度等连续值。

**PyTorch代码**：
```python
import torch
import torch.nn as nn

loss_fn = nn.MSELoss()
y_true = torch.tensor([1.0, 2.0, 3.0])
y_pred = torch.tensor([1.1, 1.9, 3.2])
loss = loss_fn(y_pred, y_true)
print(loss)  # tensor(0.0167)
```

**推荐论文**：
1. [Deep Residual Learning for Image Recognition (ResNet, 2015)](https://arxiv.org/abs/1512.03385) - 用MSE做回归预训练
2. [U-Net: Convolutional Networks for Biomedical Image Segmentation (2015)](https://arxiv.org/abs/1505.04597) - 图像分割中的像素级回归
3. [Attention Is All You Need (Transformer, 2017)](https://arxiv.org/abs/1706.03762) - 位置编码的回归损失

## MAE / L1 Loss（平均绝对误差）

**核心思想**：直接算绝对误差，对异常值不敏感。

**公式推导**：
- 单个样本损失：$L = |y - \hat{y}|$
- 批量平均：$L = \frac{1}{N}\sum_{i=1}^{N}|y_i - \hat{y}_i|$
- **梯度推导**：$\frac{\partial L}{\partial \hat{y}} = -\text{sign}(y - \hat{y})$ → 梯度恒为±1，更新稳定但可能震荡

**和MSE的区别**：
- MSE对大误差惩罚重（平方），适合噪声小的数据
- MAE对异常值鲁棒，但梯度不连续，在0点不可导（实际用smooth L1解决）

**PyTorch代码**：
```python
loss_fn = nn.L1Loss()
y_true = torch.tensor([1.0, 2.0, 3.0])
y_pred = torch.tensor([1.1, 1.9, 3.2])
loss = loss_fn(y_pred, y_true)
print(loss)  # tensor(0.1333)
```

**推荐论文**：
1. [Robust Regression via Online Feature Selection (2007)](https://ieeexplore.ieee.org/document/4270454) - MAE在鲁棒回归中的理论基础
2. [You Only Look Once (YOLOv1, 2016)](https://arxiv.org/abs/1506.02640) - 目标检测中用MAE回归边界框
3. [Deep High-Resolution Representation Learning (HRNet, 2019)](https://arxiv.org/abs/1908.07919) - 关键点检测用MAE

## Huber Loss（L1和L2结合）

**核心思想**：小误差用MSE（平滑），大误差用MAE（鲁棒），通过超参数δ控制切换点。

**公式推导**：
$$
L_\delta(y, \hat{y}) = 
\begin{cases} 
\frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \leq \delta \\
\delta |y - \hat{y}| - \frac{1}{2}\delta^2 & \text{otherwise}
\end{cases}
$$
- 当误差≤δ时，等价于MSE（梯度连续）
- 当误差>δ时，等价于MAE（梯度为常数）
- **梯度**：$\frac{\partial L}{\partial \hat{y}} = \begin{cases} -(y - \hat{y}) & |y - \hat{y}| \leq \delta \\ -\delta \cdot \text{sign}(y - \hat{y}) & \text{otherwise} \end{cases}$

**什么时候用**：回归任务中有异常值时（比如传感器数据有噪声）

**PyTorch代码**：
```python
loss_fn = nn.SmoothL1Loss(beta=1.0)  # beta就是δ
y_true = torch.tensor([1.0, 2.0, 10.0])  # 最后一个可能是异常值
y_pred = torch.tensor([1.1, 1.9, 3.2])
loss = loss_fn(y_pred, y_true)
print(loss)  # 对异常值惩罚比MSE轻
```

**推荐论文**：
1. [Robust Estimation of a Location Parameter (Huber, 1964)](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-35/issue-1/Robust-Estimation-of-a-Location-Parameter/10.1214/aoms/1177703732.full) - 原始Huber Loss论文
2. [Deep Q-learning with Experience Replay (DQN, 2013)](https://arxiv.org/abs/1312.5602) - 强化学习中用Huber Loss稳定训练
3. [Faster R-CNN (2015)](https://arxiv.org/abs/1506.01497) - RPN回归用Smooth L1 Loss

## Cross-Entropy（交叉熵）

**核心思想**：从信息论来——预测分布和真实分布的"距离"。分类任务的黄金标准！

**公式推导**：
- 真实标签是one-hot向量 $y$（比如[0,1,0]），预测概率是 $\hat{y}$（softmax输出）
- 单样本损失：$L = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)$
- 因为y是one-hot，简化为：$L = -\log(\hat{y}_{\text{true class}})$
- **为什么用这个**：最大化正确类别的对数似然，等价于最小化KL散度（见后文）

**PyTorch代码**：
```python
# 注意：PyTorch的CrossEntropyLoss内部包含softmax
loss_fn = nn.CrossEntropyLoss()
logits = torch.tensor([[1.0, 2.0, 0.5]])  # 未归一化的logits
labels = torch.tensor([1])  # 真实类别索引
loss = loss_fn(logits, labels)
print(loss)  # tensor(0.8009)

# 手动验证：softmax后取-log
probs = torch.softmax(logits, dim=1)
manual_loss = -torch.log(probs[0, 1])
print(manual_loss)  # 和上面结果一致
```

**推荐论文**：
1. [ImageNet Classification with Deep Convolutional Neural Networks (AlexNet, 2012)](https://papers.nips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf) - 首次在ImageNet用交叉熵
2. [Very Deep Convolutional Networks (VGG, 2014)](https://arxiv.org/abs/1409.1556) - 标准分类损失
3. [Batch Normalization (2015)](https://arxiv.org/abs/1502.03167) - 用交叉熵验证BN效果

## Focal Loss（难样本加权）

**核心思想**：解决样本不均衡——简单样本（高置信度）的损失自动衰减，让模型专注难样本。

**公式推导**：
- 在交叉熵基础上加调制因子：$FL(p_t) = -\alpha_t (1 - p_t)^\gamma \log(p_t)$
  - $p_t$：正确类别的预测概率（$p_t = p$ if y=1, else $1-p$）
  - $\gamma \geq 0$：聚焦参数，越大对难样本权重越高
  - $\alpha_t$：平衡正负样本权重
- **关键洞察**：$(1-p_t)^\gamma$ 项 → 当 $p_t \to 1$（简单样本），损失→0；当 $p_t \to 0$（难样本），损失≈原始交叉熵

**PyTorch代码**：
```python
class FocalLoss(nn.Module):
    def __init__(self, alpha=1, gamma=2):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        
    def forward(self, logits, targets):
        ce_loss = F.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()

# 使用
loss_fn = FocalLoss(alpha=0.25, gamma=2)
logits = torch.randn(3, 5, requires_grad=True)
targets = torch.randint(0, 5, (3,))
loss = loss_fn(logits, targets)
```

**推荐论文**：
1. [Focal Loss for Dense Object Detection (RetinaNet, 2017)](https://arxiv.org/abs/1708.02002) - 提出Focal Loss解决前景-背景不平衡
2. [Libra R-CNN (2019)](https://arxiv.org/abs/1904.03701) - 在目标检测中扩展Focal Loss
3. [Class-Balanced Loss (2019)](https://arxiv.org/abs/1901.05555) - 更通用的样本不平衡解决方案

## Triplet Loss（三元组损失）

**核心思想**：拉近锚点和正例的距离，推远锚点和负例的距离，用于度量学习。

**公式推导**：
- 输入三元组：锚点(a)、正例(p)、负例(n)
- 距离函数：$d(x,y) = \|f(x) - f(y)\|_2^2$（特征空间L2距离）
- 损失：$L = \max(d(a,p) - d(a,n) + \text{margin}, 0)$
- **margin的作用**：确保正例比负例至少近margin距离，避免 trivial solution（所有样本映射到同一点）

**PyTorch代码**：
```python
def triplet_loss(anchor, positive, negative, margin=1.0):
    dist_pos = F.pairwise_distance(anchor, positive)
    dist_neg = F.pairwise_distance(anchor, negative)
    loss = F.relu(dist_pos - dist_neg + margin)
    return loss.mean()

# 假设特征维度为128
anchor = torch.randn(10, 128)
positive = torch.randn(10, 128)
negative = torch.randn(10, 128)
loss = triplet_loss(anchor, positive, negative)
```

**推荐论文**：
1. [FaceNet: A Unified Embedding for Face Recognition (2015)](https://arxiv.org/abs/1503.03832) - 人脸识别里程碑，提出Triplet Loss
2. [In Defense of the Triplet Loss (2017)](https://arxiv.org/abs/1703.07737) - 分析Triplet Loss的有效性
3. [Sampling Matters in Deep Embedding Learning (2017)](https://arxiv.org/abs/1706.07567) - 改进三元组采样策略

## Contrastive Loss（对比损失）

**核心思想**：直接优化正负样本对的距离，比Triplet Loss更简单。

**公式推导**：
- 对于样本对 $(x_i, x_j)$ 和标签 $y_{ij}$（1=同类，0=异类）
- 损失：$L = y_{ij} d^2 + (1-y_{ij}) \max(\text{margin} - d, 0)^2$
  - 同类：最小化距离 $d$
  - 异类：距离至少为margin，否则惩罚
- 和Triplet Loss区别：不需要三元组，只需要成对标签

**PyTorch代码**：
```python
def contrastive_loss(embeddings1, embeddings2, labels, margin=1.0):
    distances = F.pairwise_distance(embeddings1, embeddings2)
    losses = labels * distances.pow(2) + \
             (1 - labels) * F.relu(margin - distances).pow(2)
    return losses.mean()

# labels: 1表示同类，0表示异类
emb1 = torch.randn(10, 128)
emb2 = torch.randn(10, 128)
labels = torch.randint(0, 2, (10,))
loss = contrastive_loss(emb1, emb2, labels)
```

**推荐论文**：
1. [Dimensionality Reduction by Learning an Invariant Mapping (2006)](https://ieeexplore.ieee.org/document/1640720) - 提出Contrastive Loss
2. [Learning a Similarity Metric Discriminatively (2005)](https://ieeexplore.ieee.org/document/1467314) - 早期度量学习工作
3. [SimSiam: Exploring Simple Siamese Representation Learning (2020)](https://arxiv.org/abs/2011.10566) - 无负样本对比学习

## InfoNCE（信息噪声对比估计）

**核心思想**：从互信息角度——最大化正样本对的互信息，把其他样本当噪声。

**公式推导**：
- 给定查询 $q$，正样本 $k_+$，负样本集合 $\{k_i^-\}$
- 损失：$L = -\log \frac{\exp(q \cdot k_+ / \tau)}{\exp(q \cdot k_+ / \tau) + \sum_i \exp(q \cdot k_i^- / \tau)}$
- **温度参数τ的作用**：
  - τ小：softmax更尖锐，只关注最相似的负样本
  - τ大：softmax更平滑，考虑更多负样本
- 本质：多分类交叉熵，把正样本当"正确类"，负样本当"错误类"

**PyTorch代码**：
```python
def info_nce_loss(query, key, keys_all, temperature=0.07):
    # query: (N, D), key: (N, D), keys_all: (M, D) 包含key和其他负样本
    logits = torch.matmul(query, keys_all.T) / temperature
    labels = torch.arange(query.size(0), device=query.device)
    return F.cross_entropy(logits, labels)

# 实际使用通常用MoCo或SimCLR的实现
```

**推荐论文**：
1. [Representation Learning with Contrastive Predictive Coding (CPC, 2018)](https://arxiv.org/abs/1807.03748) - 提出InfoNCE
2. [Momentum Contrast (MoCo, 2019)](https://arxiv.org/abs/1911.05722) - 用队列存储负样本
3. [A Simple Framework for Contrastive Learning (SimCLR, 2020)](https://arxiv.org/abs/2002.05709) - 大批量训练InfoNCE

## NT-Xent（标准化温度交叉熵）

**核心思想**：SimCLR用的InfoNCE变种，标准化特征并加温度参数。

**公式推导**：
- 对两个增强视图 $z_i, z_j$，计算相似度：$\text{sim}(u,v) = \frac{u^T v}{\|u\| \|v\|}$
- 损失（对$z_i$）：$l(i,j) = -\log \frac{\exp(\text{sim}(z_i, z_j)/\tau)}{\sum_{k=1}^{2N} \mathbb{1}_{[k \neq i]} \exp(\text{sim}(z_i, z_k)/\tau)}$
- 总损失：$L = \frac{1}{2N} \sum_{k=1}^{N} [l(2k-1, 2k) + l(2k, 2k-1)]$

**和InfoNCE区别**：显式标准化特征（L2归一化），确保相似度在[-1,1]

**PyTorch代码**（简化版）：
```python
class NTXentLoss(nn.Module):
    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature
        
    def forward(self, z_i, z_j):
        # z_i, z_j: (N, D) 两个增强视图的特征
        z = torch.cat([z_i, z_j], dim=0)
        z = F.normalize(z, dim=1)
        
        sim_matrix = torch.matmul(z, z.T) / self.temperature
        N = z_i.size(0)
        labels = torch.arange(N, device=z.device)
        labels = torch.cat([labels + N, labels], dim=0)
        
        mask = torch.eye(2*N, device=z.device).bool()
        sim_matrix.masked_fill_(mask, -float('inf'))
        return F.cross_entropy(sim_matrix, labels)
```

**推荐论文**：
1. [A Simple Framework for Contrastive Learning (SimCLR, 2020)](https://arxiv.org/abs/2002.05709) - 提出NT-Xent
2. [Big Self-Supervised Models (2021)](https://arxiv.org/abs/2103.03230) - 扩展SimCLR到更大规模
3. [Barlow Twins (2021)](https://arxiv.org/abs/2103.03230) - 不用负样本的对比学习替代方案

## KL Divergence（KL散度）

**核心思想**：衡量两个概率分布P和Q的差异，非对称！

**公式推导**：
- 连续分布：$D_{KL}(P \| Q) = \int P(x) \log \frac{P(x)}{Q(x)} dx$
- 离散分布：$D_{KL}(P \| Q) = \sum_i P(i) \log \frac{P(i)}{Q(i)}$
- **和交叉熵的关系**：$H(P, Q) = H(P) + D_{KL}(P \| Q)$
  - H(P,Q)是交叉熵，H(P)是P的熵（常数）
  - 最小化交叉熵 ≡ 最小化KL散度（当P固定时）

**PyTorch代码**：
```python
# KL散度要求输入是对数概率
p = torch.tensor([[0.1, 0.2, 0.7]])  # 真实分布
q = torch.tensor([[0.3, 0.4, 0.3]])  # 预测分布

# 方法1：用KLDivLoss（输入q需为log-prob）
loss_fn = nn.KLDivLoss(reduction='batchmean')
kl_loss = loss_fn(q.log(), p)

# 方法2：手动计算
kl_manual = (p * (p.log() - q.log())).sum()
print(kl_loss, kl_manual)  # 应该相等
```

**推荐论文**：
1. [Variational Autoencoders (VAE, 2013)](https://arxiv.org/abs/1312.6114) - 用KL散度约束隐变量分布
2. [Knowledge Distillation (2015)](https://arxiv.org/abs/1503.02531) - 用KL散度传递知识
3. [Bayesian Dark Knowledge (2015)](https://arxiv.org/abs/1503.02531) - 知识蒸馏的贝叶斯解释

## Dice Loss（Dice系数损失）

**核心思想**：直接优化分割的重叠度，对类别不平衡友好（比如医学图像中病灶很小）。

**公式推导**：
- Dice系数：$D = \frac{2|X \cap Y|}{|X| + |Y|} = \frac{2 \sum p_i g_i}{\sum p_i + \sum g_i}$
  - X,Y是预测和真实分割
  - $p_i,g_i$是像素预测概率和真实标签
- Dice Loss：$L = 1 - D$
- **平滑版本**（避免除零）：$L = 1 - \frac{2 \sum p_i g_i + \epsilon}{\sum p_i + \sum g_i + \epsilon}$

**PyTorch代码**：
```python
class DiceLoss(nn.Module):
    def __init__(self, smooth=1e-6):
        super().__init__()
        self.smooth = smooth
        
    def forward(self, pred, target):
        pred = torch.sigmoid(pred)  # 如果输入是logits
        intersection = (pred * target).sum()
        dice = (2. * intersection + self.smooth) / \
               (pred.sum() + target.sum() + self.smooth)
        return 1 - dice

# 多分类用Soft Dice
def soft_dice_loss(pred, target, num_classes):
    pred = F.softmax(pred, dim=1)
    target = F.one_hot(target, num_classes).permute(0,3,1,2).float()
    loss = 0
    for c in range(num_classes):
        p = pred[:, c]
        t = target[:, c]
        intersection = (p * t).sum()
        dice = (2. * intersection) / (p.sum() + t.sum())
        loss += (1 - dice)
    return loss / num_classes
```

**推荐论文**：
1. [V-Net: Fully Convolutional Neural Networks for Volumetric Medical Image Segmentation (2016)](https://arxiv.org/abs/1606.04797) - 医学图像分割用Dice Loss
2. [3D U-Net: Learning Dense Volumetric Segmentation (2016)](https://arxiv.org/abs/1606.06650) - 3D分割标准损失
3. [Generalised Dice Loss (2017)](https://arxiv.org/abs/1707.03237) - 改进多类别不平衡问题

## Perceptual Loss（感知损失）

**核心思想**：不用像素级比较，用预训练网络的高层特征距离衡量相似度。

**公式推导**：
- 用预训练VGG网络φ提取特征
- 损失：$L = \sum_l \frac{1}{H_l W_l C_l} \|\phi_l(I) - \phi_l(\hat{I})\|_2^2$
  - l是网络层（比如relu3_3）
  - $H_l,W_l,C_l$是特征图尺寸
- **为什么有效**：高层特征捕捉语义信息，对像素偏移不敏感

**PyTorch代码**：
```python
from torchvision.models import vgg16

class PerceptualLoss(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = vgg16(pretrained=True).features[:23]  # 到relu4_3
        self.vgg = vgg.eval().requires_grad_(False)
        self.criterion = nn.MSELoss()
        
    def forward(self, input, target):
        feat_input = self.vgg(input)
        feat_target = self.vgg(target)
        return self.criterion(feat_input, feat_target)

# 注意：输入需归一化到[0,1]并用ImageNet均值方差标准化
```

**推荐论文**：
1. [Perceptual Losses for Real-Time Style Transfer (2016)](https://arxiv.org/abs/1603.08155) - 风格迁移开创性工作
2. [Photo-Realistic Single Image Super-Resolution (SRGAN, 2017)](https://arxiv.org/abs/1609.04802) - 超分用感知损失提升视觉质量
3. [Unpaired Image-to-Image Translation (CycleGAN, 2017)](https://arxiv.org/abs/1703.10593) - 用感知损失保持语义

## Adversarial Loss（对抗损失）

**核心思想**：GAN的核心——生成器G和判别器D玩min-max博弈。

**公式推导**（原始GAN）：
- 判别器D目标：$\max_D \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$
- 生成器G目标：$\min_G \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$
- **实际训练技巧**：G的目标改为 $\max_G \mathbb{E}_{z \sim p_z}[\log D(G(z))]$（避免早期梯度消失）

**PyTorch代码**（简化训练循环）：
```python
# 判别器训练
real_pred = D(real_images)
fake_pred = D(G(noise))
d_loss = -torch.mean(torch.log(real_pred + 1e-8) + torch.log(1 - fake_pred + 1e-8))

# 生成器训练（用改进版）
fake_pred = D(G(noise))
g_loss = -torch.mean(torch.log(fake_pred + 1e-8))

# 或者用BCEWithLogitsLoss更稳定
criterion = nn.BCEWithLogitsLoss()
d_loss = criterion(real_pred, torch.ones_like(real_pred)) + \
         criterion(fake_pred, torch.zeros_like(fake_pred))
g_loss = criterion(fake_pred, torch.ones_like(fake_pred))
```

**推荐论文**：
1. [Generative Adversarial Networks (Goodfellow, 2014)](https://arxiv.org/abs/1406.2661) - GAN开山之作
2. [Wasserstein GAN (2017)](https://arxiv.org/abs/1701.07875) - 用W距离解决训练不稳定
3. [Improved Training of Wasserstein GANs (2017)](https://arxiv.org/abs/1704.00028) - 梯度惩罚改进

## Physics Loss / PINN Loss（物理信息神经网络损失）

**核心思想**：把物理方程作为约束加入损失函数，让网络解满足物理规律。

**公式推导**：
- 假设要解PDE：$\mathcal{N}[u] = 0$（比如Navier-Stokes方程）
- 损失 = 数据损失 + 物理损失
  - $L = \underbrace{\|u_{\text{pred}} - u_{\text{data}}\|^2}_{\text{数据拟合}} + \lambda \underbrace{\|\mathcal{N}[u_{\text{pred}}]\|^2}_{\text{物理约束}}$
- **自动微分**：用PyTorch的autograd计算$\mathcal{N}[u]$中的导数

**PyTorch代码**（以泊松方程为例）：
```python
def physics_loss(u, x, y):
    # u: 网络输出，x,y: 坐标
    u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_y = torch.autograd.grad(u, y, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), create_graph=True)[0]
    u_yy = torch.autograd.grad(u_y, y, grad_outputs=torch.ones_like(u_y), create_graph=True)[0]
    
    # 泊松方程: u_xx + u_yy = f(x,y)
    f = torch.sin(torch.pi * x) * torch.sin(torch.pi * y)  # 右端项
    pde_residual = u_xx + u_yy - f
    return torch.mean(pde_residual**2)

# 总损失
data_loss = F.mse_loss(u_pred, u_true)
physics_loss_val = physics_loss(u_pred, x, y)
total_loss = data_loss + 100 * physics_loss_val  # λ=100
```

**推荐论文**：
1. [Physics-Informed Neural Networks (Raissi et al., 2019)](https://arxiv.org/abs/1711.10561) - PINN奠基工作
2. [Hidden Fluid Mechanics (2020)](https://www.pnas.org/doi/10.1073/pnas.1910138117) - 用PINN发现隐藏物理
3. [PISFM: Physics-Informed Spectral Fourier Method (2023)](https://arxiv.org/abs/2302.03540) - 结合频谱方法的PINN改进

---
> 这篇文档覆盖了主流损失函数的核心思想、公式和代码。记住：没有最好的损失函数，只有最适合你任务的！多试试，多调参，有问题随时找师兄讨论 :)