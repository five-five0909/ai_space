# 27. 自监督学习

> 师弟师妹们好！自监督学习就是让模型自己给自己创造标签，不用人工标注数据。今天咱们用大白话+公式+代码，彻底搞懂各种自监督学习方法！

---

## SimCLR（简单对比学习）

### 这玩意儿到底是啥？
SimCLR就是通过数据增强创造正负样本对，让模型学会区分相似和不相似的样本。核心思想是：同一张图的不同增强版本应该相似，不同图的增强版本应该不相似。

### 核心公式推导
**对比损失（NT-Xent）**：
$$
\mathcal{L}_{i,j} = -\log \frac{\exp(\text{sim}(z_i, z_j) / \tau)}{\sum_{k=1}^{2N} \mathbb{1}_{[k \neq i]} \exp(\text{sim}(z_i, z_k) / \tau)}
$$

其中：
- $z_i, z_j$ 是同一张图的两个增强视图的特征
- $\text{sim}(u,v) = \frac{u^T v}{\|u\| \|v\|}$ 是余弦相似度
- $\tau$ 是温度参数
- $N$ 是batch size

**总损失**：
$$
\mathcal{L} = \frac{1}{2N} \sum_{k=1}^N [\mathcal{L}_{2k-1,2k} + \mathcal{L}_{2k,2k-1}]
$$

**为什么有效？**
- 大batch size提供更多负样本
- 特征归一化确保相似度在[-1,1]
- 温度参数控制softmax的尖锐程度

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

class SimCLR(nn.Module):
    def __init__(self, backbone, hidden_dim=512, projection_dim=128):
        super().__init__()
        self.backbone = backbone
        self.projection_head = nn.Sequential(
            nn.Linear(backbone.fc.in_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, projection_dim)
        )
        # 移除原始分类头
        self.backbone.fc = nn.Identity()
        
    def forward(self, x):
        features = self.backbone(x)
        projections = self.projection_head(features)
        return F.normalize(projections, dim=1)

class NTXentLoss(nn.Module):
    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature
        
    def forward(self, z_i, z_j):
        batch_size = z_i.size(0)
        z = torch.cat([z_i, z_j], dim=0)
        
        # 计算相似度矩阵
        sim_matrix = torch.matmul(z, z.t()) / self.temperature
        mask = torch.eye(2 * batch_size, device=z.device).bool()
        sim_matrix.masked_fill_(mask, -float('inf'))
        
        # 创建标签
        labels = torch.arange(batch_size, device=z.device)
        labels = torch.cat([labels + batch_size, labels], dim=0)
        
        loss = F.cross_entropy(sim_matrix, labels)
        return loss

# 数据增强
def get_simclr_transform(crop_size=224):
    return transforms.Compose([
        transforms.RandomResizedCrop(crop_size, scale=(0.2, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomApply([transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)], p=0.8),
        transforms.RandomGrayscale(p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

# 使用示例
from torchvision.models import resnet50

backbone = resnet50(pretrained=False)
model = SimCLR(backbone, hidden_dim=512, projection_dim=128)
criterion = NTXentLoss(temperature=0.5)

# 创建两个增强视图
transform = get_simclr_transform()
image = torch.randn(3, 224, 224)  # 实际使用PIL.Image
view1 = transform(image)
view2 = transform(image)

# 前向传播
z1 = model(view1.unsqueeze(0))
z2 = model(view2.unsqueeze(0))

# 计算损失
loss = criterion(z1, z2)
print(f"SimCLR loss: {loss.item():.6f}")
```

### 推荐论文
1. Chen et al., "A Simple Framework for Contrastive Learning of Visual Representations", ICML 2020
2. He et al., "Momentum Contrast for Unsupervised Visual Representation Learning", CVPR 2020
3. Grill et al., "Bootstrap Your Own Latent: A New Approach to Self-Supervised Learning", NeurIPS 2020

---

## MoCo（动量对比）

### 这玩意儿到底是啥？
MoCo就是用动量更新的队列来存储负样本！它解决了SimCLR需要大batch size的问题，可以用小batch size训练。

### 核心公式推导
**动量编码器**：
$$
\theta_k = m \cdot \theta_k + (1 - m) \cdot \theta_q
$$

其中：
- $\theta_q$ 是查询编码器参数
- $\theta_k$ 是键编码器参数  
- $m$ 是动量系数（通常0.999）

**队列机制**：
- 维护一个固定大小的队列存储负样本
- 每次迭代，新样本入队，旧样本出队
- 队列大小可以远大于batch size

**对比损失**：
$$
\mathcal{L} = -\log \frac{\exp(q \cdot k_+ / \tau)}{\exp(q \cdot k_+ / \tau) + \sum_{k_- \in \text{queue}} \exp(q \cdot k_- / \tau)}
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MoCo(nn.Module):
    def __init__(self, backbone, dim=128, K=65536, m=0.999, T=0.07):
        super().__init__()
        self.K = K
        self.m = m
        self.T = T
        
        # 查询编码器
        self.encoder_q = backbone
        self.projector_q = nn.Sequential(
            nn.Linear(backbone.fc.in_features, backbone.fc.in_features),
            nn.ReLU(),
            nn.Linear(backbone.fc.in_features, dim)
        )
        self.encoder_q.fc = nn.Identity()
        
        # 键编码器（动量更新）
        self.encoder_k = self._build_encoder_k(backbone)
        self.projector_k = self._build_projector_k(dim)
        
        # 初始化队列
        self.register_buffer("queue", torch.randn(dim, K))
        self.queue = F.normalize(self.queue, dim=0)
        self.register_buffer("queue_ptr", torch.zeros(1, dtype=torch.long))
        
    def _build_encoder_k(self, backbone):
        encoder_k = type(backbone)(pretrained=False)
        encoder_k.fc = nn.Identity()
        # 复制查询编码器权重
        for param_q, param_k in zip(self.encoder_q.parameters(), encoder_k.parameters()):
            param_k.data.copy_(param_q.data)
            param_k.requires_grad = False
        return encoder_k
    
    def _build_projector_k(self, dim):
        projector_k = nn.Sequential(
            nn.Linear(self.encoder_k.fc.in_features, self.encoder_k.fc.in_features),
            nn.ReLU(),
            nn.Linear(self.encoder_k.fc.in_features, dim)
        )
        # 复制查询投影器权重
        for param_q, param_k in zip(self.projector_q.parameters(), projector_k.parameters()):
            param_k.data.copy_(param_q.data)
            param_k.requires_grad = False
        return projector_k
    
    @torch.no_grad()
    def _momentum_update_key_encoder(self):
        """动量更新键编码器"""
        for param_q, param_k in zip(self.encoder_q.parameters(), self.encoder_k.parameters()):
            param_k.data = param_k.data * self.m + param_q.data * (1. - self.m)
            
        for param_q, param_k in zip(self.projector_q.parameters(), self.projector_k.parameters()):
            param_k.data = param_k.data * self.m + param_q.data * (1. - self.m)
    
    @torch.no_grad()
    def _dequeue_and_enqueue(self, keys):
        """更新队列"""
        batch_size = keys.shape[0]
        ptr = int(self.queue_ptr)
        
        # 入队出队
        if ptr + batch_size <= self.K:
            self.queue[:, ptr:ptr + batch_size] = keys.t()
        else:
            # 跨越队列末尾
            left = self.K - ptr
            self.queue[:, ptr:] = keys[:left].t()
            self.queue[:, :batch_size - left] = keys[left:].t()
            
        ptr = (ptr + batch_size) % self.K
        self.queue_ptr[0] = ptr
    
    def forward(self, im_q, im_k):
        # 查询编码
        q = self.projector_q(self.encoder_q(im_q))
        q = F.normalize(q, dim=1)
        
        # 键编码（无梯度）
        with torch.no_grad():
            self._momentum_update_key_encoder()
            k = self.projector_k(self.encoder_k(im_k))
            k = F.normalize(k, dim=1)
            
        # 计算对比损失
        l_pos = torch.einsum('nc,nc->n', [q, k]).unsqueeze(-1)
        l_neg = torch.einsum('nc,ck->nk', [q, self.queue.clone().detach()])
        
        logits = torch.cat([l_pos, l_neg], dim=1)
        logits /= self.T
        
        labels = torch.zeros(logits.shape[0], dtype=torch.long).to(q.device)
        loss = F.cross_entropy(logits, labels)
        
        # 更新队列
        self._dequeue_and_enqueue(k)
        
        return loss

# 使用示例
from torchvision.models import resnet50

backbone = resnet50(pretrained=False)
moco = MoCo(backbone, dim=128, K=65536, m=0.999, T=0.07)

im_q = torch.randn(32, 3, 224, 224)
im_k = torch.randn(32, 3, 224, 224)

loss = moco(im_q, im_k)
print(f"MoCo loss: {loss.item():.6f}")
print(f"Queue size: {moco.queue.shape}")
```

### 推荐论文
1. He et al., "Momentum Contrast for Unsupervised Visual Representation Learning", CVPR 2020
2. Chen et al., "Improved Baselines with Momentum Contrastive Learning", arXiv 2020
3. Caron et al., "Unsupervised Learning of Visual Features by Contrasting Cluster Assignments", NeurIPS 2020

---

## BYOL（自己引导自己）

### 这玩意儿到底是啥？
BYOL就是完全不用负样本的对比学习！它用两个不同的编码器互相学习，一个叫在线网络，一个叫目标网络。

### 核心公式推导
**双网络架构**：
- 在线网络：$y_\theta = f_\theta(g_\theta(x))$
- 目标网络：$z_\xi = f_\xi(g_\xi(x'))$

其中$x$和$x'$是同一张图的两个增强视图。

**损失函数**：
$$
\mathcal{L}_\theta = \| \bar{y}_\theta - z_\xi \|^2
$$

其中$\bar{y}_\theta$是$y_\theta$的L2归一化。

**目标网络更新**：
$$
\xi = \tau \xi + (1 - \tau) \theta
$$

**为什么不用负样本也能工作？**
- 在线网络和目标网络的不对称性提供了隐式负样本
- BatchNorm的批统计信息提供了额外的监督信号
- 动量更新稳定了目标网络

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BYOL(nn.Module):
    def __init__(self, backbone, hidden_dim=512, projection_dim=256, momentum=0.996):
        super().__init__()
        self.momentum = momentum
        
        # 在线网络
        self.online_encoder = backbone
        self.online_encoder.fc = nn.Identity()
        self.online_projector = nn.Sequential(
            nn.Linear(backbone.fc.in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, projection_dim)
        )
        self.online_predictor = nn.Sequential(
            nn.Linear(projection_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, projection_dim)
        )
        
        # 目标网络
        self.target_encoder = self._build_target_network(backbone)
        self.target_projector = self._build_target_projector(hidden_dim, projection_dim)
        
    def _build_target_network(self, backbone):
        target_encoder = type(backbone)(pretrained=False)
        target_encoder.fc = nn.Identity()
        # 复制在线编码器权重
        for param_online, param_target in zip(self.online_encoder.parameters(), target_encoder.parameters()):
            param_target.data.copy_(param_online.data)
            param_target.requires_grad = False
        return target_encoder
    
    def _build_target_projector(self, hidden_dim, projection_dim):
        target_projector = nn.Sequential(
            nn.Linear(self.target_encoder.fc.in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, projection_dim)
        )
        # 复制在线投影器权重
        for param_online, param_target in zip(self.online_projector.parameters(), target_projector.parameters()):
            param_target.data.copy_(param_online.data)
            param_target.requires_grad = False
        return target_projector
    
    @torch.no_grad()
    def _update_target_network(self):
        """动量更新目标网络"""
        for param_online, param_target in zip(self.online_encoder.parameters(), self.target_encoder.parameters()):
            param_target.data = param_target.data * self.momentum + param_online.data * (1 - self.momentum)
            
        for param_online, param_target in zip(self.online_projector.parameters(), self.target_projector.parameters()):
            param_target.data = param_target.data * self.momentum + param_online.data * (1 - self.momentum)
    
    def forward(self, view1, view2):
        # 在线网络前向传播
        online_proj1 = self.online_projector(self.online_encoder(view1))
        online_proj2 = self.online_projector(self.online_encoder(view2))
        
        pred1 = self.online_predictor(online_proj1)
        pred2 = self.online_predictor(online_proj2)
        
        # 目标网络前向传播（无梯度）
        with torch.no_grad():
            self._update_target_network()
            target_proj1 = self.target_projector(self.target_encoder(view1))
            target_proj2 = self.target_projector(self.target_encoder(view2))
            
        # 计算损失
        loss1 = F.mse_loss(F.normalize(pred1, dim=1), F.normalize(target_proj2, dim=1))
        loss2 = F.mse_loss(F.normalize(pred2, dim=1), F.normalize(target_proj1, dim=1))
        
        return (loss1 + loss2) / 2

# 使用示例
from torchvision.models import resnet50

backbone = resnet50(pretrained=False)
byol = BYOL(backbone, hidden_dim=512, projection_dim=256)

view1 = torch.randn(32, 3, 224, 224)
view2 = torch.randn(32, 3, 224, 224)

loss = byol(view1, view2)
print(f"BYOL loss: {loss.item():.6f}")
```

### 推荐论文
1. Grill et al., "Bootstrap Your Own Latent: A New Approach to Self-Supervised Learning", NeurIPS 2020
2. Chen & He, "Exploring Simple Siamese Representation Learning", CVPR 2021
3. Tian et al., "Understanding Self-Supervised Learning Dynamics without Contrastive Pairs", ICML 2021

---

## DINO（自己蒸馏）

### 这玩意儿到底是啥？
DINO就是用知识蒸馏的思想做自监督学习！它用教师-学生架构，但没有标签，让学生网络学习教师网络的输出分布。

### 核心公式推导
**教师-学生架构**：
- 学生网络：$s_\theta(x)$
- 教师网络：$t_\xi(x')$

**中心化和锐化**：
- 教师输出中心化：$\bar{q} = q - c$
- 学生输出锐化：$p = \text{softmax}(s / \tau_s)$
- 教师输出锐化：$q = \text{softmax}(t / \tau_t)$

**损失函数**：
$$
\mathcal{L} = -\sum_{i=1}^K \bar{q}_i \log p_i
$$

**教师网络更新**：
$$
\xi \leftarrow \lambda \xi + (1 - \lambda) \theta
$$

**动量中心**：
$$
c \leftarrow m_c \cdot c + (1 - m_c) \cdot \frac{1}{B} \sum_{i=1}^B q_i
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class DINOHead(nn.Module):
    def __init__(self, in_dim, out_dim, use_bn=False, nlayers=3, hidden_dim=2048, bottleneck_dim=256):
        super().__init__()
        layers = [nn.Linear(in_dim, hidden_dim)]
        if use_bn:
            layers.append(nn.BatchNorm1d(hidden_dim))
        layers.append(nn.GELU())
        
        for _ in range(nlayers - 2):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            if use_bn:
                layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.GELU())
            
        layers.append(nn.Linear(hidden_dim, bottleneck_dim))
        self.mlp = nn.Sequential(*layers)
        self.apply(self._init_weights)
        self.last_layer = nn.utils.weight_norm(nn.Linear(bottleneck_dim, out_dim, bias=False))
        self.last_layer.weight_g.data.fill_(1)
        self.last_layer.weight_g.requires_grad = False
        
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
                
    def forward(self, x):
        x = self.mlp(x)
        x = nn.functional.normalize(x, dim=-1, p=2)
        x = self.last_layer(x)
        return x

class DINO(nn.Module):
    def __init__(self, student_backbone, teacher_backbone, out_dim=65536, 
                 student_temp=0.1, teacher_temp=0.04, center_momentum=0.9):
        super().__init__()
        self.student_temp = student_temp
        self.teacher_temp = teacher_temp
        self.center_momentum = center_momentum
        
        # 学生网络
        self.student = student_backbone
        self.student_head = DINOHead(student_backbone.embed_dim, out_dim)
        
        # 教师网络
        self.teacher = teacher_backbone
        self.teacher_head = DINOHead(teacher_backbone.embed_dim, out_dim)
        
        # 冻结教师网络
        for param in self.teacher.parameters():
            param.requires_grad = False
            
        # 中心缓冲区
        self.register_buffer("center", torch.zeros(1, out_dim))
        
    @torch.no_grad()
    def update_teacher(self, momentum=0.996):
        """动量更新教师网络"""
        for param_student, param_teacher in zip(self.student.parameters(), self.teacher.parameters()):
            param_teacher.data = param_teacher.data * momentum + param_student.data * (1 - momentum)
            
        for param_student, param_teacher in zip(self.student_head.parameters(), self.teacher_head.parameters()):
            param_teacher.data = param_teacher.data * momentum + param_student.data * (1 - momentum)
    
    def forward(self, student_views, teacher_views):
        # 学生网络前向传播
        student_output = self.student(student_views)
        student_logits = self.student_head(student_output)
        student_probs = F.softmax(student_logits / self.student_temp, dim=-1)
        
        # 教师网络前向传播
        with torch.no_grad():
            self.update_teacher()
            teacher_output = self.teacher(teacher_views)
            teacher_logits = self.teacher_head(teacher_output)
            
            # 中心化和锐化
            teacher_logits = teacher_logits - self.center
            teacher_probs = F.softmax(teacher_logits / self.teacher_temp, dim=-1)
            
        # 计算损失
        loss = torch.sum(-teacher_probs * F.log_softmax(student_logits / self.student_temp, dim=-1), dim=-1)
        loss = loss.mean()
        
        # 更新中心
        self.update_center(teacher_probs)
        
        return loss
    
    @torch.no_grad()
    def update_center(self, teacher_probs):
        """更新中心"""
        batch_center = torch.mean(teacher_probs, dim=0, keepdim=True)
        self.center = self.center * self.center_momentum + batch_center * (1 - self.center_momentum)

# 使用示例（简化版，假设使用Vision Transformer）
# from transformers import ViTModel
# student_vit = ViTModel.from_pretrained("google/vit-base-patch16-224")
# teacher_vit = ViTModel.from_pretrained("google/vit-base-patch16-224")

# dino = DINO(student_vit, teacher_vit, out_dim=65536)

# student_views = torch.randn(32, 3, 224, 224)
# teacher_views = torch.randn(32, 3, 224, 224)

# loss = dino(student_views, teacher_views)
# print(f"DINO loss: {loss.item():.6f}")
```

### 推荐论文
1. Caron et al., "Emerging Properties in Self-Supervised Vision Transformers", ICCV 2021
2. Caron et al., "DINOv2: Learning Robust Visual Features without Supervision", arXiv 2023
3. Bordes et al., "VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning", arXiv 2021

---
> 自监督学习让AI学会自己找规律！SimCLR用对比学习，MoCo用动量队列，BYOL不用负样本，DINO用知识蒸馏。记住：好的自监督方法能用1%的标注数据达到全监督的性能！