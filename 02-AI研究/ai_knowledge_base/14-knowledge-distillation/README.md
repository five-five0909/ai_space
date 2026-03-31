# 14. 知识蒸馏

> 师弟师妹们好！知识蒸馏（Knowledge Distillation）就是让小模型"偷学"大模型的精华，既能保持高性能又能轻量化部署。今天咱们用大白话+公式+代码，彻底搞懂各种蒸馏方法！

---

## 温度软化蒸馏（Temperature Softening）

### 这玩意儿到底是啥？
这是最经典的蒸馏方法！大模型（teacher）在预测时用一个温度参数T来"软化"输出概率分布，小模型（student）不仅要学真实标签，还要学大模型的软化概率分布。

### 核心公式推导
**标准softmax**：
$$
P(y=i|x) = \frac{e^{z_i}}{\sum_j e^{z_j}}
$$

**带温度的softmax**：
$$
P_T(y=i|x) = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}
$$

- 当T=1时，就是标准softmax
- 当T>1时，概率分布更平滑（不确定性更高）
- 当T→∞时，所有类别的概率趋近相等

**总损失函数**：
$$
\mathcal{L} = \alpha \cdot \mathcal{L}_{CE}(y, P_S) + (1-\alpha) \cdot T^2 \cdot \mathcal{L}_{KL}(P_T^{teacher}, P_T^{student})
$$

其中：
- $\mathcal{L}_{CE}$是学生模型对真实标签的交叉熵损失
- $\mathcal{L}_{KL}$是教师和学生软化概率分布的KL散度
- $T^2$因子是为了补偿温度对梯度的影响

**为什么用KL散度？**
因为KL散度衡量的是两个概率分布的差异，而且当教师分布固定时，最小化KL散度等价于最小化交叉熵。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class KnowledgeDistillationLoss(nn.Module):
    def __init__(self, temperature=3.0, alpha=0.7):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
        
    def forward(self, student_logits, teacher_logits, labels):
        # 学生对真实标签的损失
        ce_loss = self.ce_loss(student_logits, labels)
        
        # 软化概率分布
        student_soft = F.log_softmax(student_logits / self.temperature, dim=1)
        teacher_soft = F.softmax(teacher_logits / self.temperature, dim=1)
        
        # KL散度损失
        kl_loss = F.kl_div(student_soft, teacher_soft, reduction='batchmean')
        
        # 总损失
        total_loss = self.alpha * ce_loss + (1 - self.alpha) * kl_loss * (self.temperature ** 2)
        return total_loss

# 使用示例
teacher_model = ...  # 预训练的大模型
student_model = ...  # 要训练的小模型

kd_loss_fn = KnowledgeDistillationLoss(temperature=3.0, alpha=0.3)

for images, labels in dataloader:
    with torch.no_grad():
        teacher_logits = teacher_model(images)
    
    student_logits = student_model(images)
    loss = kd_loss_fn(student_logits, teacher_logits, labels)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

### 推荐论文
1. Hinton et al., "Distilling the Knowledge in a Neural Network", NIPS 2014 Workshop
2. Ba & Caruana, "Do Deep Nets Really Need to be Deep?", NIPS 2014
3. Romero et al., "FitNets: Hints for Thin Deep Nets", ICLR 2015

---

## 特征图蒸馏（Feature Map Distillation）

### 这玩意儿到底是啥？
不只蒸馏最后的输出，还蒸馏中间层的特征图！让学生模型的中间表示也尽量接近教师模型，这样能学到更多细节信息。

### 核心公式推导
假设教师模型在第l层的特征图为$F_T^l$，学生模型对应层的特征图为$F_S^l$，那么特征蒸馏损失为：
$$
\mathcal{L}_{feature} = \sum_l \| \phi(F_T^l) - \psi(F_S^l) \|_2^2
$$

其中$\phi$和$\psi$是适配函数，用于处理教师和学生特征图维度不一致的问题：
- 如果维度相同：$\phi$和$\psi$可以是恒等映射
- 如果维度不同：$\phi$和$\psi$通常是1x1卷积或全连接层

**常见的特征对齐方式**：
1. **直接对齐**：$\|F_T - F_S\|_2^2$
2. **注意力对齐**：$\|A_T \odot F_T - A_S \odot F_S\|_2^2$，其中A是注意力权重
3. **关系对齐**：$\|F_T F_T^T - F_S F_S^T\|_F^2$，保持特征间的相关性

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class FeatureMapDistillation(nn.Module):
    def __init__(self, teacher_channels, student_channels):
        super().__init__()
        # 适配层，将学生特征图映射到教师维度
        if teacher_channels != student_channels:
            self.adapter = nn.Conv2d(student_channels, teacher_channels, 1, bias=False)
        else:
            self.adapter = nn.Identity()
            
    def forward(self, teacher_features, student_features):
        # 适配学生特征
        student_adapted = self.adapter(student_features)
        
        # L2损失
        loss = F.mse_loss(student_adapted, teacher_features)
        return loss

# 完整的蒸馏训练
class DistillationTrainer:
    def __init__(self, teacher_model, student_model, feature_pairs):
        self.teacher = teacher_model
        self.student = student_model
        self.feature_pairs = feature_pairs  # [(teacher_layer, student_layer), ...]
        
        # 为每个特征对创建适配器
        self.adapters = nn.ModuleList()
        for t_layer, s_layer in feature_pairs:
            t_ch = get_channel_count(teacher_model, t_layer)
            s_ch = get_channel_count(student_model, s_layer)
            self.adapters.append(FeatureMapDistillation(t_ch, s_ch))
    
    def train_step(self, images, labels):
        # 提取教师特征
        teacher_outputs = []
        def hook_fn(module, input, output):
            teacher_outputs.append(output)
        
        hooks = []
        for layer_name in [pair[0] for pair in self.feature_pairs]:
            layer = get_module_by_name(self.teacher, layer_name)
            hook = layer.register_forward_hook(hook_fn)
            hooks.append(hook)
            
        with torch.no_grad():
            teacher_logits = self.teacher(images)
        
        # 移除钩子
        for hook in hooks:
            hook.remove()
        
        # 提取学生特征
        student_outputs = []
        def student_hook_fn(module, input, output):
            student_outputs.append(output)
            
        student_hooks = []
        for layer_name in [pair[1] for pair in self.feature_pairs]:
            layer = get_module_by_name(self.student, layer_name)
            hook = layer.register_forward_hook(student_hook_fn)
            student_hooks.append(hook)
            
        student_logits = self.student(images)
        
        for hook in student_hooks:
            hook.remove()
        
        # 计算损失
        total_loss = 0
        # 输出蒸馏损失
        kd_loss = KnowledgeDistillationLoss()(student_logits, teacher_logits, labels)
        total_loss += kd_loss
        
        # 特征蒸馏损失
        for i, adapter in enumerate(self.adapters):
            feat_loss = adapter(teacher_outputs[i], student_outputs[i])
            total_loss += 0.1 * feat_loss  # 权重可调
        
        return total_loss
```

### 推荐论文
1. Zagoruyko & Komodakis, "Paying More Attention to Attention: Improving the Performance of Convolutional Neural Networks via Attention Transfer", ICLR 2017
2. Yim et al., "A Gift from Knowledge Distillation: Fast Optimization, Network Minimization and Transfer Learning", CVPR 2017
3. Heo et al., "Knowledge Transfer via Distillation of Activation Boundaries Formed by Hidden Neurons", AAAI 2019

---

## 对抗蒸馏（Adversarial Distillation）

### 这玩意儿到底是啥？
引入对抗训练的思想！用一个判别器来判断特征图是来自教师还是学生，学生不仅要模仿教师的输出，还要骗过判别器。

### 核心公式推导
这是一个min-max博弈问题：

**判别器D的目标**（最大化）：
$$
\max_D \mathbb{E}[\log D(F_T)] + \mathbb{E}[\log(1 - D(F_S))]
$$

**学生模型S的目标**（最小化）：
$$
\min_S \mathcal{L}_{task} + \lambda \cdot \mathbb{E}[\log(1 - D(F_S))]
$$

其中$\mathcal{L}_{task}$是任务损失（如分类交叉熵），$\lambda$是平衡权重。

**训练流程**：
1. 固定学生模型，训练判别器D区分教师和学生特征
2. 固定判别器D，训练学生模型S生成能骗过D的特征
3. 重复步骤1-2直到收敛

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Discriminator(nn.Module):
    def __init__(self, feature_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.layers(x)

class AdversarialDistillation:
    def __init__(self, teacher_model, student_model, feature_dim, lambda_adv=0.1):
        self.teacher = teacher_model
        self.student = student_model
        self.discriminator = Discriminator(feature_dim)
        self.lambda_adv = lambda_adv
        self.criterion = nn.BCELoss()
        
    def train_discriminator(self, teacher_features, student_features):
        # 真实样本（教师特征）标签为1
        real_labels = torch.ones(teacher_features.size(0), 1).to(teacher_features.device)
        # 虚假样本（学生特征）标签为0
        fake_labels = torch.zeros(student_features.size(0), 1).to(student_features.device)
        
        real_preds = self.discriminator(teacher_features.detach())
        fake_preds = self.discriminator(student_features.detach())
        
        d_loss_real = self.criterion(real_preds, real_labels)
        d_loss_fake = self.criterion(fake_preds, fake_labels)
        
        d_loss = d_loss_real + d_loss_fake
        return d_loss
    
    def train_student(self, student_features, task_loss):
        # 学生要骗过判别器，所以目标是让判别器输出1
        target_labels = torch.ones(student_features.size(0), 1).to(student_features.device)
        fake_preds = self.discriminator(student_features)
        adv_loss = self.criterion(fake_preds, target_labels)
        
        total_loss = task_loss + self.lambda_adv * adv_loss
        return total_loss

# 使用示例
adv_distill = AdversarialDistillation(teacher_model, student_model, feature_dim=512)

for images, labels in dataloader:
    # 获取特征
    with torch.no_grad():
        teacher_features = teacher_model.get_features(images)
    student_features = student_model.get_features(images)
    student_logits = student_model.classifier(student_features)
    
    # 任务损失
    task_loss = F.cross_entropy(student_logits, labels)
    
    # 训练判别器
    d_optimizer.zero_grad()
    d_loss = adv_distill.train_discriminator(teacher_features, student_features)
    d_loss.backward()
    d_optimizer.step()
    
    # 训练学生
    s_optimizer.zero_grad()
    s_loss = adv_distill.train_student(student_features, task_loss)
    s_loss.backward()
    s_optimizer.step()
```

### 推荐论文
1. Xu et al., "Training Shallow and Thin Networks for Acceleration via Knowledge Distillation with Conditional Adversarial Networks", ICLR Workshop 2018
2. Chen et al., "Learning Efficient Object Detection Models with Knowledge Distillation", NeurIPS 2017
3. Wang et al., "Adversarial Feature Matching for Knowledge Distillation", arXiv 2020

---

## 自蒸馏（Self-Distillation）

### 这玩意儿到底是啥？
不用老师模型，自己教自己！通常用深层的输出来指导浅层的学习，或者用模型的平均输出来指导当前输出。

### 核心公式推导
**深度自蒸馏**：
- 让浅层模块学习深层模块的输出
- 损失函数：$\mathcal{L} = \mathcal{L}_{task} + \lambda \sum_{i<j} \mathcal{L}_{KL}(P_j, P_i)$
- 其中$P_i$是第i层的输出概率分布

**时间自蒸馏**（Temporal Self-Distillation）：
- 用历史模型的平均输出作为软标签
- $P_{avg} = \frac{1}{T} \sum_{t=1}^T P_t$
- 损失函数：$\mathcal{L} = \mathcal{L}_{CE}(y, P) + \lambda \mathcal{L}_{KL}(P_{avg}, P)$

**在线自蒸馏**（Online Self-Distillation）：
- 同一输入的不同增强版本相互学习
- $\mathcal{L} = \mathcal{L}_{CE}(y, P_1) + \mathcal{L}_{CE}(y, P_2) + \lambda \mathcal{L}_{KL}(P_1, P_2)$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SelfDistillationModel(nn.Module):
    def __init__(self, base_model, num_intermediate_outputs=3):
        super().__init__()
        self.base_model = base_model
        self.num_intermediate_outputs = num_intermediate_outputs
        
        # 为每个中间层添加分类头
        self.intermediate_classifiers = nn.ModuleList()
        for i in range(num_intermediate_outputs):
            self.intermediate_classifiers.append(
                nn.Linear(base_model.feature_dim, base_model.num_classes)
            )
    
    def forward(self, x):
        features = self.base_model.extract_features(x)
        final_output = self.base_model.classifier(features[-1])
        
        intermediate_outputs = []
        for i, classifier in enumerate(self.intermediate_classifiers):
            intermediate_outputs.append(classifier(features[i]))
            
        return final_output, intermediate_outputs

class SelfDistillationLoss(nn.Module):
    def __init__(self, temperature=3.0, alpha=0.3):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
        
    def forward(self, final_output, intermediate_outputs, labels):
        # 最终输出的交叉熵损失
        main_loss = self.ce_loss(final_output, labels)
        
        # 自蒸馏损失：深层指导浅层
        distill_loss = 0
        num_layers = len(intermediate_outputs)
        for i in range(num_layers):
            # 用最终输出作为教师信号
            teacher_soft = F.softmax(final_output / self.temperature, dim=1)
            student_soft = F.log_softmax(intermediate_outputs[i] / self.temperature, dim=1)
            kl_loss = F.kl_div(student_soft, teacher_soft, reduction='batchmean')
            distill_loss += kl_loss
            
        total_loss = main_loss + self.alpha * distill_loss * (self.temperature ** 2)
        return total_loss

# 使用示例
model = SelfDistillationModel(base_model)
criterion = SelfDistillationLoss()

for images, labels in dataloader:
    final_output, intermediate_outputs = model(images)
    loss = criterion(final_output, intermediate_outputs, labels)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

### 推荐论文
1. Zhang et al., "Be Your Own Teacher: Improve the Performance of Convolutional Neural Networks via Self Distillation", ICCV 2019
2. Xie et al., "Self-Distillation as a Generalization Regularizer", NeurIPS 2020
3. Mobahi et al., "Self-Distillation Amplifies Regularization in Hilbert Space", NeurIPS 2020

---

## 在线蒸馏（Online Distillation）

### 这玩意儿到底是啥？
多个学生模型同时训练，互相学习！不需要预训练的教师模型，所有模型都是学生，但在训练过程中互为师生。

### 核心公式推导
假设有K个学生模型$\{S_1, S_2, ..., S_K\}$，每个模型的损失函数为：
$$
\mathcal{L}_k = \mathcal{L}_{CE}(y, P_k) + \lambda \sum_{j \neq k} \mathcal{L}_{KL}(P_j, P_k)
$$

其中$P_k$是第k个模型的输出概率分布。

**关键思想**：
- 所有模型并行训练
- 每个模型既学习真实标签，也学习其他模型的预测
- 避免了预训练教师模型的成本
- 多个模型的集成效果更好

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class OnlineDistillationEnsemble(nn.Module):
    def __init__(self, model_list):
        super().__init__()
        self.models = nn.ModuleList(model_list)
        self.num_models = len(model_list)
        
    def forward(self, x):
        outputs = []
        for model in self.models:
            outputs.append(model(x))
        return outputs

class OnlineDistillationLoss(nn.Module):
    def __init__(self, temperature=3.0, alpha=0.3):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
        
    def forward(self, model_outputs, labels):
        total_loss = 0
        num_models = len(model_outputs)
        
        for i in range(num_models):
            # 交叉熵损失
            ce_loss = self.ce_loss(model_outputs[i], labels)
            
            # 蒸馏损失：学习其他模型
            distill_loss = 0
            for j in range(num_models):
                if i != j:
                    teacher_soft = F.softmax(model_outputs[j] / self.temperature, dim=1)
                    student_soft = F.log_softmax(model_outputs[i] / self.temperature, dim=1)
                    kl_loss = F.kl_div(student_soft, teacher_soft, reduction='batchmean')
                    distill_loss += kl_loss
                    
            distill_loss /= (num_models - 1)  # 平均其他模型
            model_loss = ce_loss + self.alpha * distill_loss * (self.temperature ** 2)
            total_loss += model_loss
            
        return total_loss / num_models  # 平均所有模型的损失

# 使用示例
# 创建多个学生模型
student_models = [create_student_model() for _ in range(3)]
ensemble = OnlineDistillationEnsemble(student_models)
criterion = OnlineDistillationLoss()

# 为每个模型创建优化器
optimizers = [torch.optim.Adam(model.parameters(), lr=0.001) for model in student_models]

for images, labels in dataloader:
    model_outputs = ensemble(images)
    loss = criterion(model_outputs, labels)
    
    # 更新所有模型
    for optimizer in optimizers:
        optimizer.zero_grad()
    loss.backward()
    for optimizer in optimizers:
        optimizer.step()
```

### 推荐论文
1. Lan et al., "Knowledge Distillation in Ensembles of Neural Networks", arXiv 2018
2. Chen et al., "Online Knowledge Distillation with Diverse Peers", AAAI 2020
3. Kim et al., "Online Knowledge Distillation via Collaborative Learning", CVPR 2019

---

## 关系蒸馏（Relational Knowledge Distillation）

### 这玩意儿到底是啥？
不只蒸馏单个样本的输出，还蒸馏样本之间的关系！比如两个样本在特征空间中的距离关系。

### 核心公式推导
**样本关系矩阵**：
对于一批样本$\{x_1, x_2, ..., x_N\}$，计算它们在特征空间中的关系矩阵：
$$
R_{ij} = f(\phi(x_i), \phi(x_j))
$$

其中$\phi$是特征提取函数，$f$是关系函数（如余弦相似度、欧氏距离等）。

**关系蒸馏损失**：
$$
\mathcal{L}_{rel} = \| R_T - R_S \|_F^2
$$

其中$R_T$和$R_S$分别是教师和学生的关系矩阵，$\|\cdot\|_F$是Frobenius范数。

**常用的关系函数**：
1. **余弦相似度**：$R_{ij} = \frac{\phi(x_i)^T \phi(x_j)}{\|\phi(x_i)\| \|\phi(x_j)\|}$
2. **欧氏距离**：$R_{ij} = \|\phi(x_i) - \phi(x_j)\|_2^2$
3. **高斯核**：$R_{ij} = \exp(-\|\phi(x_i) - \phi(x_j)\|_2^2 / \sigma^2)$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class RelationalKnowledgeDistillation(nn.Module):
    def __init__(self, relation_type='cosine'):
        super().__init__()
        self.relation_type = relation_type
        
    def compute_relation_matrix(self, features):
        if self.relation_type == 'cosine':
            # 余弦相似度
            features_norm = F.normalize(features, dim=1)
            relation_matrix = torch.mm(features_norm, features_norm.t())
        elif self.relation_type == 'euclidean':
            # 欧氏距离的平方
            pairwise_distances = torch.cdist(features, features, p=2)
            relation_matrix = pairwise_distances ** 2
        elif self.relation_type == 'gaussian':
            # 高斯核
            pairwise_distances = torch.cdist(features, features, p=2)
            sigma = pairwise_distances.mean()
            relation_matrix = torch.exp(-pairwise_distances ** 2 / (2 * sigma ** 2))
        else:
            raise ValueError(f"Unknown relation type: {self.relation_type}")
            
        return relation_matrix
    
    def forward(self, teacher_features, student_features):
        teacher_relations = self.compute_relation_matrix(teacher_features)
        student_relations = self.compute_relation_matrix(student_features)
        
        # 关系蒸馏损失
        loss = F.mse_loss(student_relations, teacher_relations)
        return loss

# 完整训练流程
class RKDTrainer:
    def __init__(self, teacher_model, student_model, alpha_rkd=0.5):
        self.teacher = teacher_model
        self.student = student_model
        self.rkd_loss_fn = RelationalKnowledgeDistillation(relation_type='cosine')
        self.alpha_rkd = alpha_rkd
        
    def train_step(self, images, labels):
        # 提取特征
        with torch.no_grad():
            teacher_features = self.teacher.extract_features(images)
        student_features = self.student.extract_features(images)
        student_logits = self.student.classifier(student_features)
        
        # 任务损失
        task_loss = F.cross_entropy(student_logits, labels)
        
        # 关系蒸馏损失
        rkd_loss = self.rkd_loss_fn(teacher_features, student_features)
        
        total_loss = task_loss + self.alpha_rkd * rkd_loss
        return total_loss
```

### 推荐论文
1. Park et al., "Relational Knowledge Distillation", CVPR 2019
2. Liu et al., "Structured Knowledge Distillation for Semantic Segmentation", CVPR 2019
3. Wu et al., "Contrastive Representation Distillation", ICLR 2020

---

## 注意力蒸馏（Attention Transfer）

### 这玩意儿到底是啥？
专门蒸馏注意力机制！让学生模型学习教师模型的注意力权重或注意力图，特别适合Transformer和CNN。

### 核心公式推导
**CNN注意力图**：
对于CNN的某一层特征图$F \in \mathbb{R}^{C \times H \times W}$，注意力图定义为：
$$
A = \frac{1}{C} \sum_{c=1}^C |F_c|
$$

**Transformer注意力权重**：
对于多头注意力，第h个头的注意力权重为：
$$
A_h = \text{softmax}\left(\frac{Q_h K_h^T}{\sqrt{d}}\right)
$$

**注意力蒸馏损失**：
$$
\mathcal{L}_{attn} = \sum_l \| A_T^l - A_S^l \|_2^2
$$

其中$A_T^l$和$A_S^l$分别是教师和学生在第l层的注意力图。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class AttentionTransferLoss(nn.Module):
    def __init__(self):
        super().__init__()
        
    def compute_attention_map(self, features):
        # features: [B, C, H, W]
        attention_map = torch.mean(torch.abs(features), dim=1, keepdim=True)
        # 归一化到[0,1]
        attention_map = attention_map / (attention_map.max() + 1e-8)
        return attention_map
    
    def forward(self, teacher_features, student_features):
        teacher_attn = self.compute_attention_map(teacher_features)
        student_attn = self.compute_attention_map(student_features)
        
        # L2损失
        loss = F.mse_loss(student_attn, teacher_attn)
        return loss

# Transformer注意力蒸馏
class TransformerAttentionDistillation(nn.Module):
    def __init__(self):
        super().__init__()
        
    def forward(self, teacher_attn_weights, student_attn_weights):
        # teacher_attn_weights: [B, H, T, T]
        # student_attn_weights: [B, H, T, T]
        loss = F.mse_loss(student_attn_weights, teacher_attn_weights)
        return loss

# 使用示例（CNN）
at_loss_fn = AttentionTransferLoss()

for images, labels in dataloader:
    # 假设我们能获取中间层特征
    with torch.no_grad():
        teacher_features = teacher_model.get_intermediate_features(images)
    student_features = student_model.get_intermediate_features(images)
    
    attn_loss = at_loss_fn(teacher_features, student_features)
    task_loss = F.cross_entropy(student_model(images), labels)
    
    total_loss = task_loss + 0.1 * attn_loss
    total_loss.backward()
```

### 推荐论文
1. Zagoruyko & Komodakis, "Paying More Attention to Attention: Improving the Performance of Convolutional Neural Networks via Attention Transfer", ICLR 2017
2. Jiao et al., "TinyBERT: Distilling BERT for Natural Language Understanding", EMNLP 2020
3. Sun et al., "Patient Knowledge Distillation for BERT Model Compression", EMNLP 2019

---
> 知识蒸馏的核心思想就是"站在巨人的肩膀上"！选择哪种蒸馏方法取决于你的具体需求：要简单就用温度软化，要精细就用特征蒸馏，要创新就试试对抗蒸馏。记住，蒸馏不是万能的，但合理的蒸馏策略能让你的小模型性能提升不少！