# 28. 图神经网络与3D

> 师弟师妹们好！图神经网络和3D处理让AI能理解复杂的关系和空间结构。今天咱们用大白话+公式+代码，彻底搞懂各种图神经网络和3D方法！

---

## Graph Neural Networks（图神经网络）

### 这玩意儿到底是啥？
GNN就是处理图数据的神经网络！它通过消息传递机制，让每个节点聚合邻居的信息，从而学习节点和图的表示。

### 核心公式推导
**消息传递框架**：
$$
m_{u \to v}^{(l)} = M^{(l)}(h_u^{(l)}, h_v^{(l)}, e_{uv})
$$
$$
h_v^{(l+1)} = U^{(l)}(h_v^{(l)}, \text{AGGREGATE}(\{m_{u \to v}^{(l)} | u \in \mathcal{N}(v)\}))
$$

其中：
- $h_v^{(l)}$ 是节点$v$在第$l$层的表示
- $\mathcal{N}(v)$ 是$v$的邻居集合
- $M^{(l)}$ 是消息函数
- $U^{(l)}$ 是更新函数

**GCN（图卷积网络）**：
$$
H^{(l+1)} = \sigma(\hat{D}^{-1/2} \hat{A} \hat{D}^{-1/2} H^{(l)} W^{(l)})
$$

其中$\hat{A} = A + I$是带自环的邻接矩阵，$\hat{D}$是度矩阵。

**GAT（图注意力网络）**：
$$
e_{ij} = a(W h_i, W h_j)
$$
$$
\alpha_{ij} = \frac{\exp(e_{ij})}{\sum_{k \in \mathcal{N}(i)} \exp(e_{ik})}
$$
$$
h_i' = \sigma(\sum_{j \in \mathcal{N}(i)} \alpha_{ij} W h_j)
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv

class GCN(nn.Module):
    def __init__(self, num_features, hidden_dim, num_classes, num_layers=2):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(GCNConv(num_features, hidden_dim))
        
        for _ in range(num_layers - 2):
            self.layers.append(GCNConv(hidden_dim, hidden_dim))
            
        self.layers.append(GCNConv(hidden_dim, num_classes))
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x, edge_index):
        for i, layer in enumerate(self.layers):
            x = layer(x, edge_index)
            if i < len(self.layers) - 1:
                x = F.relu(x)
                x = self.dropout(x)
        return F.log_softmax(x, dim=1)

class GAT(nn.Module):
    def __init__(self, num_features, hidden_dim, num_classes, num_heads=8):
        super().__init__()
        self.conv1 = GATConv(num_features, hidden_dim, heads=num_heads, dropout=0.6)
        self.conv2 = GATConv(hidden_dim * num_heads, num_classes, heads=1, concat=False, dropout=0.6)
        self.dropout = nn.Dropout(0.6)
        
    def forward(self, x, edge_index):
        x = F.dropout(x, p=0.6, training=self.training)
        x = F.elu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

# 使用PyTorch Geometric的Cora数据集
from torch_geometric.datasets import Planetoid

dataset = Planetoid(root='/tmp/Cora', name='Cora')
data = dataset[0]

# GCN训练
gcn_model = GCN(dataset.num_features, 16, dataset.num_classes)
optimizer = torch.optim.Adam(gcn_model.parameters(), lr=0.01, weight_decay=5e-4)

gcn_model.train()
for epoch in range(200):
    optimizer.zero_grad()
    out = gcn_model(data.x, data.edge_index)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()

# 测试
gcn_model.eval()
pred = gcn_model(data.x, data.edge_index).argmax(dim=1)
acc = (pred[data.test_mask] == data.y[data.test_mask]).float().mean()
print(f"GCN Accuracy: {acc:.4f}")

# GAT训练
gat_model = GAT(dataset.num_features, 8, dataset.num_classes)
optimizer = torch.optim.Adam(gat_model.parameters(), lr=0.005, weight_decay=5e-4)

gat_model.train()
for epoch in range(200):
    optimizer.zero_grad()
    out = gat_model(data.x, data.edge_index)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()

gat_model.eval()
pred = gat_model(data.x, data.edge_index).argmax(dim=1)
acc = (pred[data.test_mask] == data.y[data.test_mask]).float().mean()
print(f"GAT Accuracy: {acc:.4f}")
```

### 推荐论文
1. Kipf & Welling, "Semi-Supervised Classification with Graph Convolutional Networks", ICLR 2017
2. Velickovic et al., "Graph Attention Networks", ICLR 2018
3. Wu et al., "A Comprehensive Survey on Graph Neural Networks", IEEE Transactions on Neural Networks and Learning Systems 2021

---

## PointNet（点云网络）

### 这玩意儿到底是啥？
PointNet就是直接处理点云数据的网络！它通过共享MLP和对称函数（如max pooling）来实现对点顺序的不变性。

### 核心公式推导
**输入变换**：
$$
T = f_{\text{input}}(X), \quad X' = X \cdot T
$$

**特征变换**：
$$
T' = f_{\text{feature}}(F), \quad F' = F \cdot T'
$$

**对称函数**：
$$
g: \mathbb{R}^{n \times d} \to \mathbb{R}^k, \quad g(x_1, ..., x_n) = \gamma \circ h(x_1) \oplus ... \oplus h(x_n)
$$

其中$\oplus$是对称操作（如max pooling），$h$是MLP。

**分割头**：
$$
\text{segmentation}(x_i) = f_{\text{seg}}([h(x_i), g(X)])
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class TNet(nn.Module):
    """变换网络"""
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.mlp1 = nn.Sequential(
            nn.Conv1d(k, 64, 1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, 1024, 1),
            nn.BatchNorm1d(1024),
            nn.ReLU()
        )
        self.mlp2 = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, k*k)
        )
        
    def forward(self, x):
        batch_size = x.size(0)
        x = self.mlp1(x)
        x = F.adaptive_max_pool1d(x, 1).squeeze(2)
        x = self.mlp2(x)
        
        # 初始化为单位矩阵
        identity = torch.eye(self.k, device=x.device).view(1, self.k*self.k).repeat(batch_size, 1)
        x = x + identity
        
        return x.view(batch_size, self.k, self.k)

class PointNet(nn.Module):
    def __init__(self, num_classes=40, num_parts=50):
        super().__init__()
        self.num_classes = num_classes
        self.num_parts = num_parts
        
        # 输入变换
        self.input_transform = TNet(k=3)
        
        # 共享MLP
        self.mlp1 = nn.Sequential(
            nn.Conv1d(3, 64, 1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, 1024, 1),
            nn.BatchNorm1d(1024),
            nn.ReLU()
        )
        
        # 特征变换
        self.feature_transform = TNet(k=128)
        
        # 分类头
        self.classifier = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
        # 分割头
        self.segmentation = nn.Sequential(
            nn.Conv1d(1088, 512, 1),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Conv1d(512, 256, 1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(256, 128, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, num_parts, 1)
        )
        
    def forward(self, x, task='classification'):
        batch_size, num_points, _ = x.shape
        x = x.transpose(2, 1)  # [B, 3, N]
        
        # 输入变换
        input_trans = self.input_transform(x)
        x = torch.bmm(x.transpose(1, 2), input_trans).transpose(1, 2)
        
        # 共享MLP
        x = self.mlp1(x)
        
        # 特征变换
        feature_trans = self.feature_transform(x)
        x = torch.bmm(x.transpose(1, 2), feature_trans).transpose(1, 2)
        
        # 全局特征
        global_feature = F.adaptive_max_pool1d(x, 1).squeeze(2)  # [B, 1024]
        
        if task == 'classification':
            return self.classifier(global_feature)
        elif task == 'segmentation':
            # 重复全局特征到每个点
            global_feature_expanded = global_feature.unsqueeze(2).expand(-1, -1, num_points)
            x = torch.cat([x, global_feature_expanded], dim=1)
            return self.segmentation(x).transpose(1, 2)

# 使用示例
pointnet = PointNet(num_classes=40, num_parts=50)

# 分类任务
points = torch.randn(32, 1024, 3)  # 32个样本，每个1024个点
class_logits = pointnet(points, task='classification')
print(f"Classification output shape: {class_logits.shape}")  # [32, 40]

# 分割任务
seg_logits = pointnet(points, task='segmentation')
print(f"Segmentation output shape: {seg_logits.shape}")  # [32, 1024, 50]

# 计算变换矩阵正则化损失
def transform_loss(transform_matrix):
    """计算变换矩阵的正则化损失"""
    batch_size = transform_matrix.size(0)
    I = torch.eye(transform_matrix.size(1)).unsqueeze(0).repeat(batch_size, 1, 1)
    I = I.to(transform_matrix.device)
    
    loss = torch.mean(torch.norm(torch.bmm(transform_matrix, transform_matrix.transpose(2, 1)) - I, dim=(1, 2)))
    return loss

input_trans = pointnet.input_transform(points.transpose(2, 1))
feature_trans = pointnet.feature_transform(pointnet.mlp1(points.transpose(2, 1)))

input_loss = transform_loss(input_trans)
feature_loss = transform_loss(feature_trans)
print(f"Input transform loss: {input_loss:.6f}")
print(f"Feature transform loss: {feature_loss:.6f}")
```

### 推荐论文
1. Qi et al., "PointNet: Deep Learning on Point Sets for 3D Classification and Segmentation", CVPR 2017
2. Qi et al., "PointNet++: Deep Hierarchical Feature Learning on Point Sets in a Metric Space", NeurIPS 2017
3. Wang et al., "Dynamic Graph CNN for Learning on Point Clouds", ACM Transactions on Graphics 2019

---

## MeshCNN（网格卷积网络）

### 这玩意儿到底是啥？
MeshCNN就是直接在3D网格上进行卷积的网络！它定义了网格上的卷积操作，可以处理三角形网格数据。

### 核心公式推导
**边特征定义**：
对于边$e_{ij}$连接顶点$v_i$和$v_j$：
$$
f(e_{ij}) = \phi(v_i, v_j, n_i, n_j, \theta_{ij}, \phi_{ij})
$$

其中$n_i, n_j$是法向量，$\theta_{ij}, \phi_{ij}$是几何角度。

**网格卷积**：
$$
(f * g)(e) = \sum_{e' \in \mathcal{N}(e)} f(e') \cdot g(e, e')
$$

其中$\mathcal{N}(e)$是边$e$的邻居边。

**池化操作**：
通过边折叠（edge collapse）来减少网格复杂度：
- 选择要折叠的边
- 合并两个顶点
- 更新邻接关系

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MeshConv(nn.Module):
    """网格卷积层"""
    def __init__(self, in_channels, out_channels, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # 权重矩阵：4个方向（两个顶点，每个顶点两个邻居）
        self.weight = nn.Parameter(torch.Tensor(out_channels, in_channels, 4))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_channels))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()
        
    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)
            
    def forward(self, x, mesh):
        """
        x: [num_edges, in_channels] 边特征
        mesh: 包含网格拓扑信息的对象
        """
        # 获取邻居边索引
        neighbors = mesh.get_neighbors()  # [num_edges, 4]
        
        # 聚合邻居特征
        neighbor_features = x[neighbors]  # [num_edges, 4, in_channels]
        
        # 应用卷积权重
        output = torch.einsum('eic,oic->eo', neighbor_features, self.weight)
        
        if self.bias is not None:
            output = output + self.bias
            
        return output

class MeshPool(nn.Module):
    """网格池化层"""
    def __init__(self, target_faces):
        super().__init__()
        self.target_faces = target_faces
        
    def forward(self, x, mesh):
        """
        x: [num_edges, channels] 边特征
        mesh: 网格对象
        """
        # 计算每条边的重要性（基于特征范数）
        edge_scores = torch.norm(x, dim=1)
        
        # 选择要保留的边
        num_edges_to_keep = self.target_faces * 3 // 2  # 每个面有3条边，每条边被2个面共享
        _, keep_indices = torch.topk(edge_scores, num_edges_to_keep, largest=True)
        
        # 执行边折叠
        new_mesh, new_x = mesh.collapse_edges(keep_indices, x)
        
        return new_x, new_mesh

class MeshCNN(nn.Module):
    def __init__(self, num_classes=10, pool_sizes=[1700, 1300, 1000, 700]):
        super().__init__()
        self.pool_sizes = pool_sizes
        
        # 卷积层
        self.conv1 = MeshConv(6, 64)  # 6个几何特征
        self.conv2 = MeshConv(64, 128)
        self.conv3 = MeshConv(128, 256)
        self.conv4 = MeshConv(256, 512)
        
        # 池化层
        self.pool1 = MeshPool(pool_sizes[0])
        self.pool2 = MeshPool(pool_sizes[1])
        self.pool3 = MeshPool(pool_sizes[2])
        self.pool4 = MeshPool(pool_sizes[3])
        
        # 分类头
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x, mesh):
        # 第一层
        x = F.relu(self.conv1(x, mesh))
        x, mesh = self.pool1(x, mesh)
        
        # 第二层
        x = F.relu(self.conv2(x, mesh))
        x, mesh = self.pool2(x, mesh)
        
        # 第三层
        x = F.relu(self.conv3(x, mesh))
        x, mesh = self.pool3(x, mesh)
        
        # 第四层
        x = F.relu(self.conv4(x, mesh))
        x, mesh = self.pool4(x, mesh)
        
        # 全局平均池化
        x = x.mean(dim=0)  # [512]
        
        # 分类
        return self.classifier(x)

# 注意：这需要自定义的Mesh类来处理网格拓扑
# 实际使用可以参考PyTorch3D或Kaolin库
```

### 推荐论文
1. Hanocka et al., "MeshCNN: A Network with an Edge", SIGGRAPH 2019
2. Zhou et al., "Learning Local Shape Descriptors from Part Correspondences with Multi-view Convolutional Networks", SIGGRAPH 2018
3. Litany et al., "Deformable Shape Completion with Graph Convolutional Autoencoders", CVPR 2018

---

## 3D Gaussian Splatting

### 这玩意儿到底是啥？
3D Gaussian Splatting就是用3D高斯椭球体来表示场景！每个高斯体有位置、协方差、颜色和不透明度，通过光栅化生成2D图像。

### 核心公式推导
**3D高斯表示**：
每个高斯体由以下参数定义：
- 位置：$\mu \in \mathbb{R}^3$
- 协方差：$\Sigma \in \mathbb{R}^{3 \times 3}$
- 颜色：$c \in \mathbb{R}^3$
- 不透明度：$\alpha \in [0, 1]$

**视锥剔除**：
只渲染在视锥内的高斯体：
$$
\text{visible} = \{g_i | g_i \in \text{frustum}\}
$$

**排序和Alpha混合**：
按深度排序后进行alpha混合：
$$
C = \sum_{i=1}^N c_i \alpha_i \prod_{j=1}^{i-1} (1 - \alpha_j)
$$

**梯度优化**：
通过可微分光栅化优化高斯参数：
$$
\mathcal{L} = \|I_{\text{rendered}} - I_{\text{gt}}\|^2 + \lambda_{\text{reg}} \mathcal{L}_{\text{reg}}
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Gaussian3D(nn.Module):
    def __init__(self, num_gaussians=10000):
        super().__init__()
        self.num_gaussians = num_gaussians
        
        # 位置 (x, y, z)
        self.positions = nn.Parameter(torch.randn(num_gaussians, 3) * 10.0)
        
        # 协方差 (通过尺度和旋转参数化)
        self.scales = nn.Parameter(torch.ones(num_gaussians, 3) * 0.1)
        self.rotations = nn.Parameter(torch.zeros(num_gaussians, 4))  # 四元数
        self.rotations.data[:, 0] = 1.0  # 初始化为单位四元数
        
        # 颜色 (RGB + SH系数)
        self.colors = nn.Parameter(torch.randn(num_gaussians, 3) * 0.1 + 0.5)
        
        # 不透明度 (通过sigmoid约束到[0,1])
        self.opacities = nn.Parameter(torch.ones(num_gaussians) * 0.1)
        
    def get_covariance(self):
        """从尺度和旋转计算协方差矩阵"""
        # 尺度矩阵
        S = torch.diag_embed(self.scales)
        
        # 旋转矩阵 (从四元数)
        q = F.normalize(self.rotations, dim=1)
        R = self.quaternion_to_rotation_matrix(q)
        
        # 协方差: R @ S @ S.T @ R.T
        cov = torch.bmm(R, torch.bmm(S, torch.bmm(S.transpose(1, 2), R.transpose(1, 2))))
        return cov
    
    def quaternion_to_rotation_matrix(self, q):
        """四元数到旋转矩阵"""
        w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
        R = torch.stack([
            1 - 2*y*y - 2*z*z, 2*x*y - 2*w*z, 2*x*z + 2*w*y,
            2*x*y + 2*w*z, 1 - 2*x*x - 2*z*z, 2*y*z - 2*w*x,
            2*x*z - 2*w*y, 2*y*z + 2*w*x, 1 - 2*x*x - 2*y*y
        ], dim=1).view(-1, 3, 3)
        return R
    
    def forward(self, camera_params):
        """渲染图像"""
        # 获取协方差
        covariances = self.get_covariance()
        
        # 视锥剔除 (简化版)
        visible_mask = self.frustum_culling(camera_params)
        visible_positions = self.positions[visible_mask]
        visible_covariances = covariances[visible_mask]
        visible_colors = torch.sigmoid(self.colors[visible_mask])
        visible_opacities = torch.sigmoid(self.opacities[visible_mask])
        
        # 投影到2D
        projected_positions, projected_covariances = self.project_to_2d(
            visible_positions, visible_covariances, camera_params
        )
        
        # 光栅化 (简化版)
        image = self.rasterize(
            projected_positions, projected_covariances, 
            visible_colors, visible_opacities, camera_params
        )
        
        return image
    
    def frustum_culling(self, camera_params):
        """视锥剔除"""
        # 简化：假设所有高斯体都可见
        return torch.ones(self.num_gaussians, dtype=torch.bool)
    
    def project_to_2d(self, positions_3d, covariances_3d, camera_params):
        """投影到2D"""
        # 简化：假设正交投影
        positions_2d = positions_3d[:, :2]
        covariances_2d = covariances_3d[:, :2, :2]
        return positions_2d, covariances_2d
    
    def rasterize(self, positions_2d, covariances_2d, colors, opacities, camera_params):
        """光栅化"""
        # 简化：返回空白图像
        height, width = camera_params.get('height', 512), camera_params.get('width', 512)
        return torch.zeros(3, height, width)

# 使用示例
gaussian_scene = Gaussian3D(num_gaussians=1000)

camera_params = {
    'height': 512,
    'width': 512,
    'fov': 45.0
}

rendered_image = gaussian_scene(camera_params)
print(f"Rendered image shape: {rendered_image.shape}")

# 优化高斯参数
target_image = torch.randn(3, 512, 512)
optimizer = torch.optim.Adam(gaussian_scene.parameters(), lr=0.01)

for step in range(100):
    optimizer.zero_grad()
    rendered = gaussian_scene(camera_params)
    loss = F.mse_loss(rendered, target_image)
    loss.backward()
    optimizer.step()
    
    if step % 20 == 0:
        print(f"Step {step}, Loss: {loss.item():.6f}")
```

### 推荐论文
1. Kerbl et al., "3D Gaussian Splatting for Real-Time Radiance Field Rendering", SIGGRAPH 2023
2. Mildenhall et al., "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis", ECCV 2020
3. Müller et al., "Instant Neural Graphics Primitives with a Multiresolution Hash Encoding", SIGGRAPH 2022

---
> 图神经网络和3D处理让AI更强大！GNN处理关系数据，PointNet处理点云，MeshCNN处理网格，3D Gaussian Splatting实现高质量渲染。记住：好的3D表示能让虚拟世界更真实，让AI理解更深入！