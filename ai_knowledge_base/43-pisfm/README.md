# 43. PISFM项目相关汇总

> 一句话：摄影测量与三维重建是计算机视觉的核心任务，传统方法依赖特征匹配，深度学习方法用Mamba/Transformer实现端到端重建。

---

## 摄影测量基础

### 这玩意儿到底是啥？

摄影测量（Photogrammetry）就是从照片中恢复三维信息。拍几张照片，就能重建出三维模型。应用场景包括：
- **测绘**：无人机航拍生成地形图
- **文物保护**：数字化保存古建筑
- **工业检测**：测量产品尺寸
- **影视特效**：生成数字资产

**核心流程：**
```
多视角图像 → 特征提取 → 特征匹配 → 相机位姿估计 → 稠密重建 → 纹理映射
```

### 传统方法 vs 深度学习

| 环节 | 传统方法 | 深度学习方法 |
|------|----------|--------------|
| 特征提取 | SIFT, ORB, SURF | SuperPoint, Disk |
| 特征匹配 | 最近邻 + RANSAC | SuperGlue, LoFTR |
| 深度估计 | 立体匹配 | MVSNet, UniMVS |
| 位姿估计 | PnP + BA | PoseNet, MegaDepth |

---

## Structure from Motion (SfM)

### 这玩意儿到底是啥？

Structure from Motion（SfM）是从运动图像序列中恢复场景三维结构和相机运动的技术。简单说：拿着相机走一圈，就能重建出周围的三维场景。

**核心步骤：**
1. **特征提取**：在每张图像上找关键点
2. **特征匹配**：找出不同图像中的同一个点
3. **初始重建**：选两张图建立初始点云
4. **增量重建**：逐步加入新图像
5. **Bundle Adjustment**：全局优化

### 经典SfM流程

```python
# 增量式SfM伪代码
class IncrementalSfM:
    def __init__(self):
        self.feature_extractor = SIFT()
        self.matcher = BFMatcher()
        self.points_3d = []
        self.camera_poses = []

    def reconstruct(self, images):
        # 1. 特征提取
        keypoints, descriptors = [], []
        for img in images:
            kp, desc = self.feature_extractor.detectAndCompute(img)
            keypoints.append(kp)
            descriptors.append(desc)

        # 2. 特征匹配
        matches = self.match_images(descriptors)

        # 3. 选择初始图像对
        init_pair = self.select_initial_pair(matches)
        self.initialize_reconstruction(init_pair)

        # 4. 增量添加图像
        for i in range(2, len(images)):
            self.add_image(i, matches[i])

        # 5. Bundle Adjustment
        self.bundle_adjustment()

        return self.points_3d, self.camera_poses

    def bundle_adjustment(self):
        """光束法平差：优化相机位姿和三维点"""
        # 最小化重投影误差
        # min Σ ||x_ij - project(P_i, X_j)||²
        pass
```

### 主流SfM工具

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| COLMAP | 开源最完整 | 学术研究 |
| OpenMVG | 模块化设计 | 定制开发 |
| VisualSFM | 速度快 | 大规模重建 |
| Meshroom | 图形化界面 | 非专业用户 |

---

## 深度学习特征提取

### SuperPoint

### 这玩意儿到底是啥？

SuperPoint是用CNN同时做关键点检测和描述子提取的端到端网络。比SIFT更快、更鲁棒。

```python
import torch
import torch.nn as nn

class SuperPoint(nn.Module):
    """SuperPoint: 自监督兴趣点检测和描述子提取"""

    def __init__(self):
        super().__init__()
        # 共享编码器
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(),
        )

        # 关键点检测头
        self.detector = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 65, 1),  # 8x8格子 + dustbin
        )

        # 描述子提取头
        self.descriptor = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, 1),
        )

    def forward(self, x):
        # x: (B, 1, H, W)
        features = self.encoder(x)

        # 关键点热力图
        heatmap = self.detector(features)  # (B, 65, H/8, W/8)
        heatmap = torch.softmax(heatmap, dim=1)[:, :-1]  # 去掉dustbin
        heatmap = heatmap.reshape(heatmap.shape[0], -1, heatmap.shape[2] * 8, heatmap.shape[3] * 8)

        # 描述子
        desc = self.descriptor(features)  # (B, 256, H/8, W/8)
        desc = desc / torch.norm(desc, dim=1, keepdim=True)

        return heatmap, desc
```

### 推荐论文

1. **DeTone et al., 2018** - "SuperPoint: Self-Supervised Interest Point Detection and Description"
2. **Sarlin et al., 2020** - "SuperGlue: Learning Feature Matching with Graph Neural Networks"
3. **Tyszkiewicz et al., 2020** - "DISK: Learning local features with policy gradient"

---

## 深度学习特征匹配

### SuperGlue

### 这玩意儿到底是啥？

SuperGlue用图神经网络做特征匹配，把匹配问题变成最优传输问题，效果大幅超越传统方法。

```python
import torch
import torch.nn as nn

class SuperGlue(nn.Module):
    """基于GNN的特征匹配"""

    def __init__(self, config=None):
        super().__init__()
        self.kenc = KeypointEncoder()  # 关键点编码器
        self.gnn = AttentionalGNN()    # 图神经网络
        self.final_proj = nn.Linear(256, 256)
        self.sinkhorn = Sinkhorn()     # 最优传输层

    def forward(self, desc0, desc1, kpts0, kpts1):
        """
        desc0, desc1: (B, N, D) 描述子
        kpts0, kpts1: (B, N, 2) 关键点坐标
        """
        # 1. 编码关键点位置
        kenc0 = self.kenc(kpts0)
        kenc1 = self.kenc(kpts1)

        # 2. 初始特征
        desc0 = desc0 + kenc0
        desc1 = desc1 + kenc1

        # 3. 图神经网络传播
        desc0, desc1 = self.gnn(desc0, desc1)

        # 4. 计算相似度矩阵
        desc0 = self.final_proj(desc0)
        desc1 = self.final_proj(desc1)
        sim = torch.einsum('bnd,bmd->bnm', desc0, desc1)

        # 5. Sinkhorn算法求解最优匹配
        matches = self.sinkhorn(sim)

        return matches


class Sinkhorn(nn.Module):
    """Sinkhorn算法：求解最优传输"""

    def __init__(self, iters=20):
        super().__init__()
        self.iters = iters

    def forward(self, scores):
        # scores: (B, N, M)
        # 添加dustbin
        b, n, m = scores.shape
        scores = torch.cat([scores, scores.new_zeros(b, n, 1)], dim=-1)
        scores = torch.cat([scores, scores.new_zeros(b, 1, m + 1)], dim=-2)

        # Sinkhorn迭代
        for _ in range(self.iters):
            scores = torch.exp(scores)
            scores = scores / scores.sum(dim=-1, keepdim=True)
            scores = scores / scores.sum(dim=-2, keepdim=True)
            scores = torch.log(scores + 1e-6)

        return scores[:, :-1, :-1]  # 去掉dustbin
```

### LoFTR

### 这玩意儿到底是啥？

LoFTR（Local Feature Matching without Detector）不需要先检测关键点，直接在粗粒度上做匹配，然后用细粒度优化。

```python
class LoFTR(nn.Module):
    """无需检测器的局部特征匹配"""

    def __init__(self):
        super().__init__()
        self.backbone = ResNetFPN()
        self.coarse_layer = CoarseMatching()
        self.fine_layer = FineMatching()

    def forward(self, img0, img1):
        # 1. 提取多尺度特征
        feat0, feat1 = self.backbone(img0), self.backbone(img1)

        # 2. 粗粒度匹配
        coarse_matches = self.coarse_layer(feat0['coarse'], feat1['coarse'])

        # 3. 细粒度优化
        fine_matches = self.fine_layer(
            feat0['fine'], feat1['fine'], coarse_matches
        )

        return fine_matches
```

### 推荐论文

1. **Sarlin et al., 2020** - "SuperGlue: Learning Feature Matching with Graph Neural Networks"
2. **Sun et al., 2021** - "LoFTR: Detector-Free Local Feature Matching with Transformers"
3. **Chen et al., 2022** - "MatchFormer: Interleaving Attention in Transformers for Feature Matching"

---

## 多视角立体匹配 (MVS)

### 这玩意儿到底是啥？

MVS（Multi-View Stereo）是从多视角图像重建稠密三维点云的技术。相比SfM只得到稀疏点云，MVS能得到更密集的表面重建。

### MVSNet

```python
import torch
import torch.nn as nn

class MVSNet(nn.Module):
    """端到端多视角立体匹配"""

    def __init__(self, num_depth=192):
        super().__init__()
        self.feature_extractor = FeatureNet()
        self.cost_volume = CostVolumeNet(num_depth)
        self.depth_net = DepthNet()

    def forward(self, ref_img, src_imgs, ref_pose, src_poses, intrinsics):
        """
        ref_img: 参考图像 (B, 3, H, W)
        src_imgs: 源图像列表
        """
        # 1. 提取特征
        ref_feat = self.feature_extractor(ref_img)
        src_feats = [self.feature_extractor(src) for src in src_imgs]

        # 2. 构建代价体
        cost_volume = self.cost_volume(
            ref_feat, src_feats, ref_pose, src_poses, intrinsics
        )

        # 3. 深度估计
        depth = self.depth_net(cost_volume)

        return depth


class CostVolumeNet(nn.Module):
    """代价体构建"""

    def __init__(self, num_depth=192):
        super().__init__()
        self.num_depth = num_depth

    def forward(self, ref_feat, src_feats, ref_pose, src_poses, intrinsics):
        B, C, H, W = ref_feat.shape

        # 生成深度假设
        depth_values = torch.linspace(0.5, 10, self.num_depth)

        # 构建代价体
        cost_volume = []
        for d, depth in enumerate(depth_values):
            # 将源特征warp到参考视角
            warped_feats = []
            for src_feat, src_pose in zip(src_feats, src_poses):
                warped = self.warp(src_feat, ref_pose, src_pose, intrinsics, depth)
                warped_feats.append(warped)

            # 计算方差作为代价
            stacked = torch.stack([ref_feat] + warped_feats, dim=0)
            variance = torch.var(stacked, dim=0)
            cost_volume.append(variance)

        return torch.stack(cost_volume, dim=2)  # (B, C, D, H, W)

    def warp(self, src_feat, ref_pose, src_pose, intrinsics, depth):
        """将源特征warp到参考视角"""
        # 计算单应性矩阵
        pass
```

### 推荐论文

1. **Yao et al., 2018** - "MVSNet: Depth Inference for Unstructured Multi-view Stereo"
2. **Yi et al., 2020** - "Cascade Cost Volume for High-Resolution Multi-View Stereo"
3. **Wang et al., 2022** - "UniMVS: Unified Multi-View Stereo with Correlation Volume"

---

## Bi-Mamba在PISFM中的应用

### 为什么用Bi-Mamba？

在摄影测量任务中，图像序列存在长距离依赖：
- **全局一致性**：远处帧的信息影响当前帧
- **长序列建模**：无人机航拍序列很长
- **线性复杂度**：Transformer的O(n²)太慢

Bi-Mamba的双向特性适合理解整个序列的上下文。

### 代码示例

```python
import torch
import torch.nn as nn
from mamba_ssm import Mamba

class BiMambaSfM(nn.Module):
    """Bi-Mamba用于SfM特征处理"""

    def __init__(self, d_model=256, d_state=16, n_layers=6):
        super().__init__()
        self.feature_proj = nn.Linear(256, d_model)

        # 正向和反向Mamba
        self.forward_mamba = nn.ModuleList([
            Mamba(d_model, d_state) for _ in range(n_layers)
        ])
        self.backward_mamba = nn.ModuleList([
            Mamba(d_model, d_state) for _ in range(n_layers)
        ])

        self.output_proj = nn.Linear(d_model * 2, 256)

    def forward(self, features):
        """
        features: (B, N, 256) N帧图像的特征
        """
        x = self.feature_proj(features)

        # 正向传播
        h_forward = x
        for layer in self.forward_mamba:
            h_forward = layer(h_forward)

        # 反向传播
        h_backward = x.flip(1)
        for layer in self.backward_mamba:
            h_backward = layer(h_backward)
        h_backward = h_backward.flip(1)

        # 融合
        output = torch.cat([h_forward, h_backward], dim=-1)
        output = self.output_proj(output)

        return output


class MambaFeatureMatcher(nn.Module):
    """Mamba用于特征匹配"""

    def __init__(self, d_model=256):
        super().__init__()
        self.bi_mamba = BiMambaSfM(d_model)
        self.match_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, desc0, desc1):
        # desc0: (B, N, D), desc1: (B, M, D)
        B, N, D = desc0.shape
        M = desc1.shape[1]

        # 拼接两个描述子集
        combined = torch.cat([desc0, desc1], dim=1)  # (B, N+M, D)

        # Bi-Mamba处理
        enhanced = self.bi_mamba(combined)

        # 分离
        enhanced0 = enhanced[:, :N, :]
        enhanced1 = enhanced[:, N:, :]

        # 计算相似度
        sim = torch.einsum('bnd,bmd->bnm', enhanced0, enhanced1)
        matches = self.match_head(sim.unsqueeze(-1)).squeeze(-1)

        return matches
```

---

## 常用数据集

### 室内数据集

| 数据集 | 场景 | 图像数 | 特点 |
|--------|------|--------|------|
| ScanNet | 室内 | 2.5M | RGB-D，完整重建 |
| 7-Scenes | 室内 | 26K | 相机定位 |
| TUM RGB-D | 室内 | - | SLAM基准 |

### 室外数据集

| 数据集 | 场景 | 图像数 | 特点 |
|--------|------|--------|------|
| MegaDepth | 地标 | 100K+ | 多视角，深度GT |
| YFCC100M | 互联网 | 100M | 大规模 |
| IMC 2023 | 地标 | 1M+ | 匹配基准 |

### 航拍数据集

| 数据集 | 场景 | 特点 |
|--------|------|------|
| ETH3D | 高精度 | 激光雷达GT |
| DTU | 物体MVS | 结构光GT |
| BlendedMVS | 物体/场景 | 大规模MVS |

---

## 工具与框架

### 传统工具

```bash
# COLMAP - 最完整的SfM/MVS工具
colmap feature_extractor --database_path db.db --image_path images/
colmap exhaustive_matcher --database_path db.db
colmap mapper --database_path db.db --image_path images/ --output_path model/

# OpenMVG
openMVG_main_SfMInit_ImageListing -i images/ -d camera_model.txt -o matches/
openMVG_main_ComputeFeatures -i matches/sfm_data.json -o matches/
openMVG_main_ComputeMatches -i matches/sfm_data.json -o matches/
```

### 深度学习工具

```python
# 使用预训练的SuperPoint + SuperGlue
from superglue import SuperPoint, SuperGlue

# 特征提取
superpoint = SuperPoint({'weights': 'superpoint_v1'})
keypoints0, descriptors0 = superpoint.extract(image0)
keypoints1, descriptors1 = superpoint.extract(image1)

# 特征匹配
superglue = SuperGlue({'weights': 'superglue_outdoor'})
matches = superglue({
    'keypoints0': keypoints0,
    'keypoints1': keypoints1,
    'descriptors0': descriptors0,
    'descriptors1': descriptors1,
})

# 使用HLoc进行完整重建
from hloc import extract_features, match_features, reconstruction
extract_features.main(conf, image_dir, feature_path)
match_features.main(conf, pairs, features, matches)
reconstruction.main(workspace, image_dir, pairs, features, matches)
```

---

## 对比总结

| 任务 | 传统方法 | 深度学习方法 | 推荐 |
|------|----------|--------------|------|
| 特征提取 | SIFT | SuperPoint/DISK | SuperPoint |
| 特征匹配 | BFMatcher | SuperGlue/LoFTR | SuperGlue |
| 深度估计 | SGM/MC-CNN | MVSNet/UniMVS | UniMVS |
| 相机定位 | PnP | PoseNet | 传统PnP |
| 长序列处理 | 滑动窗口 | Bi-Mamba | Bi-Mamba |

### 选择建议

```
小规模重建 → COLMAP (传统方法足够)
大规模重建 → HLoc + SuperGlue
高精度需求 → 多视角MVSNet
长序列处理 → Bi-Mamba + Transformer
```

---

> 摄影测量把照片变成三维世界！传统方法稳定可靠，深度学习方法端到端高效，Bi-Mamba解决长序列建模难题。选对工具，重建无忧！