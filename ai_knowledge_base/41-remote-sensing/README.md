# 41. 遥感/光谱相关

> 一句话：遥感深度学习把卫星图像变成有用信息，CNN做基础、Transformer做全局、Mamba做长序列，光谱分析能识别物质成分。

---

## 遥感图像分类

### 这玩意儿到底是啥？

遥感图像分类就是根据卫星或航空图像判断地表类型——这块是森林、那块是农田、那边是城市。传统方法靠人工设计特征（颜色、纹理），现在都用深度学习自动学特征。

**核心挑战：**
- **尺度多样**：同一类地物在不同分辨率下外观差异大
- **类内差异**：同样是森林，热带雨林和针叶林长得不一样
- **类间相似**：不同地物看起来可能很像（比如深色水体和阴影）
- **数据标注难**：高质量标注需要专业知识，成本高

### 主流方法

**CNN方法：**

```python
import torch
import torch.nn as nn
import torchvision.models as models

# 使用预训练ResNet做遥感分类
class RemoteSensingClassifier(nn.Module):
    def __init__(self, num_classes=10, pretrained=True):
        super().__init__()
        # 使用ResNet50作为backbone
        self.backbone = models.resnet50(pretrained=pretrained)
        # 替换最后的全连接层
        self.backbone.fc = nn.Linear(2048, num_classes)

    def forward(self, x):
        return self.backbone(x)

# 多尺度特征融合
class MultiScaleRSNet(nn.Module):
    """多尺度遥感分类网络"""
    def __init__(self, num_classes=10):
        super().__init__()
        # 多个不同感受野的分支
        self.branch1 = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.branch2 = nn.Sequential(
            nn.Conv2d(3, 64, 5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.branch3 = nn.Sequential(
            nn.Conv2d(3, 64, 7, padding=3),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Linear(64 * 3 * 32 * 32, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        b1 = self.branch1(x)
        b2 = self.branch2(x)
        b3 = self.branch3(x)
        # 拼接多尺度特征
        feat = torch.cat([b1, b2, b3], dim=1)
        feat = feat.view(feat.size(0), -1)
        return self.classifier(feat)
```

**Transformer方法：**

```python
import timm

# 使用ViT做遥感分类
class RSViT(nn.Module):
    def __init__(self, img_size=224, num_classes=10):
        super().__init__()
        self.vit = timm.create_model(
            'vit_base_patch16_224',
            pretrained=True,
            num_classes=num_classes,
            img_size=img_size
        )

    def forward(self, x):
        return self.vit(x)

# Swin Transformer更适合遥感（多尺度）
class RSSwinTransformer(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.swin = timm.create_model(
            'swin_base_patch4_window7_224',
            pretrained=True,
            num_classes=num_classes
        )

    def forward(self, x):
        return self.swin(x)
```

### 推荐论文

1. **Cheng et al., 2017** - "Remote Sensing Image Scene Classification Using CNNs" - CNN在遥感的早期应用
2. **He et al., 2020** - "Remote Sensing Image Classification Based on Vision Transformer" - ViT用于遥感
3. **Wang et al., 2022** - "Transformers in Remote Sensing: A Survey" - 遥感Transformer综述

---

## 目标检测

### 这玩意儿到底是啥？

遥感目标检测就是从卫星图像中找出感兴趣的目标——飞机、舰船、车辆、建筑物等。和普通目标检测的区别是：

**遥感特点：**
- **俯视视角**：只能看到物体顶部
- **尺度变化大**：同一类目标大小差异悬殊
- **方向任意**：物体可以是任意旋转角度
- **背景复杂**：大片区域都是背景，目标稀疏

### 旋转目标检测

遥感中目标通常是任意方向的，需要旋转框检测：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class RotatedAnchorGenerator(nn.Module):
    """旋转锚框生成器"""
    def __init__(self, scales=[8, 16, 32], ratios=[0.5, 1.0, 2.0], angles=[-90, -60, -30, 0, 30, 60, 90]):
        super().__init__()
        self.scales = scales
        self.ratios = ratios
        self.angles = angles

    def forward(self, feat_h, feat_w, stride=16):
        """生成旋转锚框 (x, y, w, h, theta)"""
        anchors = []
        for i in range(feat_h):
            for j in range(feat_w):
                cx = j * stride + stride / 2
                cy = i * stride + stride / 2
                for scale in self.scales:
                    for ratio in self.ratios:
                        w = scale * (ratio ** 0.5)
                        h = scale / (ratio ** 0.5)
                        for angle in self.angles:
                            anchors.append([cx, cy, w, h, angle])
        return torch.tensor(anchors)

# 旋转IoU计算
def rotated_iou(box1, box2):
    """
    计算两个旋转框的IoU
    box: (x, y, w, h, theta) theta为角度（度）
    """
    # 使用shapely库计算多边形IoU
    from shapely.geometry import Polygon
    import math

    def to_polygon(box):
        x, y, w, h, theta = box
        theta_rad = math.radians(theta)
        # 计算四个角点坐标
        cos_t, sin_t = math.cos(theta_rad), math.sin(theta_rad)
        corners = [
            (x + w/2*cos_t - h/2*sin_t, y + w/2*sin_t + h/2*cos_t),
            (x - w/2*cos_t - h/2*sin_t, y - w/2*sin_t + h/2*cos_t),
            (x - w/2*cos_t + h/2*sin_t, y - w/2*sin_t - h/2*cos_t),
            (x + w/2*cos_t + h/2*sin_t, y + w/2*sin_t - h/2*cos_t),
        ]
        return Polygon(corners)

    poly1 = to_polygon(box1)
    poly2 = to_polygon(box2)

    if not poly1.is_valid or not poly2.is_valid:
        return 0.0

    inter = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return inter / union if union > 0 else 0.0
```

### 常用检测框架

```python
# 使用MMDetection进行遥感目标检测
from mmdet.apis import init_detector, inference_detector

# 配置文件（旋转目标检测）
config_file = 'configs/rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota.py'
checkpoint_file = 'checkpoints/rotated_retinanet_r50_fpn_1x_dota.pth'

model = init_detector(config_file, checkpoint_file, device='cuda:0')
result = inference_detector(model, 'satellite_image.tif')
```

### 推荐论文

1. **Xia et al., 2018** - "DOTA: A Large-scale Dataset for Object Detection in Aerial Images" - DOTA数据集
2. **Yang et al., 2021** - "Learning High-Precision Bounding Box for Rotated Object Detection" - 旋转框检测
3. **Ding et al., 2019** - "Learning ROI Transformation for Oriented Object Detection" - 定向目标检测

---

## 变化检测

### 这玩意儿到底是啥？

变化检测就是对比同一地区不同时期的图像，找出变化的部分。比如：去年这里是农田，今年变成建筑工地了；上周这里没有洪水，今天被淹了。

**核心挑战：**
- **季节变化**：同一地点不同季节看起来不一样（树叶颜色）
- **光照差异**：不同时间拍摄的图像亮度、阴影不同
- **配准误差**：两次拍摄的位置不完全对齐
- **伪变化**：看起来变了但实际没变（比如收割后的农田）

### 主流方法

```python
import torch
import torch.nn as nn

class ChangeDetectionNet(nn.Module):
    """双时相变化检测网络"""
    def __init__(self, in_channels=3, out_channels=1):
        super().__init__()
        # 孪生编码器（共享权重）
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        # 差分融合模块
        self.diff_module = nn.Sequential(
            nn.Conv2d(128 * 2, 128, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
        )

        # 解码器
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 2, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 2, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, out_channels, 1),
            nn.Sigmoid()
        )

    def forward(self, t1, t2):
        """
        t1: 时相1图像 (B, C, H, W)
        t2: 时相2图像 (B, C, H, W)
        """
        # 分别编码
        f1 = self.encoder(t1)
        f2 = self.encoder(t2)
        # 差分特征
        diff = torch.abs(f1 - f2)
        concat = torch.cat([f1, f2], dim=1)
        fused = self.diff_module(concat) + diff
        # 解码
        out = self.decoder(fused)
        return out

# Transformer-based变化检测
class TransformerCD(nn.Module):
    """基于Transformer的变化检测"""
    def __init__(self, img_size=256, patch_size=16, embed_dim=768):
        super().__init__()
        from timm.models.vision_transformer import PatchEmbed

        self.patch_embed = PatchEmbed(img_size, patch_size, 3, embed_dim)
        num_patches = (img_size // patch_size) ** 2

        # 双时相特征交互
        self.cross_attention = nn.MultiheadAttention(embed_dim, num_heads=8)
        self.norm = nn.LayerNorm(embed_dim)

        # 解码头
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, 256, 2, stride=2),
            nn.ReLU(),
            nn.Conv2d(256, 128, 3, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 2, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 1, 1),
            nn.Sigmoid()
        )

    def forward(self, t1, t2):
        # Patch embedding
        p1 = self.patch_embed(t1)  # (B, N, D)
        p2 = self.patch_embed(t2)

        # Cross-attention
        combined = torch.cat([p1, p2], dim=1)  # (B, 2N, D)
        combined = combined.permute(1, 0, 2)  # (2N, B, D)
        attn_out, _ = self.cross_attention(combined, combined, combined)
        attn_out = self.norm(combined + attn_out)

        # 只取差异部分
        n = attn_out.shape[0] // 2
        diff = torch.abs(attn_out[:n] - attn_out[n:])

        # Reshape并解码
        B = t1.shape[0]
        H = W = int((diff.shape[0] / B) ** 0.5)
        diff = diff.permute(1, 0, 2).reshape(B, H, W, -1).permute(0, 3, 1, 2)
        out = self.decoder(diff)
        return out
```

### 推荐论文

1. **Chen & Shi, 2020** - "A Spatial-Temporal Attention-Based Method and a New Dataset for Remote Sensing Image Change Detection" - 注意力变化检测
2. **Bandara & Patel, 2022** - "A Transformer-Based Change Detection Network for Remote Sensing Images" - Transformer变化检测
3. **Lebedev et al., 2018** - "Fully Convolutional Change Detection Neural Network" - FCN变化检测

---

## 高光谱图像处理

### 这玩意儿到底是啥？

普通RGB图像只有3个波段（红、绿、蓝），高光谱图像有**几十到几百个波段**，能记录每个像素的光谱曲线。因为不同物质的光谱特征不同，高光谱可以识别出"这是什么材料"——比如识别矿物种类、农作物类型、水体污染程度。

**核心特点：**
- **数据量大**：几百个波段，数据维度高
- **标注少**：光谱标注需要专业设备，样本稀缺
- **波段相关**：相邻波段高度相关，信息冗余
- **混合像元**：一个像素可能包含多种物质

### 降维方法

```python
import numpy as np
from sklearn.decomposition import PCA

def pca_reduction(data, n_components=30):
    """
    PCA降维
    data: (H, W, C) 高光谱数据
    """
    H, W, C = data.shape
    # 展平
    data_flat = data.reshape(-1, C)
    # PCA
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(data_flat)
    # 恢复形状
    return reduced.reshape(H, W, n_components)

# 3D-CNN for HSI Classification
class HSI3DCNN(nn.Module):
    """3D CNN用于高光谱分类"""
    def __init__(self, in_channels, num_classes, patch_size=7):
        super().__init__()
        self.conv3d = nn.Sequential(
            nn.Conv3d(1, 8, kernel_size=(7, 3, 3), padding=(0, 1, 1)),
            nn.ReLU(),
            nn.Conv3d(8, 16, kernel_size=(5, 3, 3), padding=(0, 1, 1)),
            nn.ReLU(),
            nn.Conv3d(16, 32, kernel_size=(3, 3, 3), padding=(0, 1, 1)),
            nn.ReLU(),
        )
        # 计算flatten后的维度
        self.flatten_dim = self._get_flatten_dim(in_channels, patch_size)
        self.classifier = nn.Sequential(
            nn.Linear(self.flatten_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def _get_flatten_dim(self, in_channels, patch_size):
        # 简化计算
        return 32 * (patch_size - 4) * (patch_size - 4)

    def forward(self, x):
        # x: (B, C, H, W) -> (B, 1, C, H, W)
        x = x.unsqueeze(1)
        x = self.conv3d(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)
```

### 推荐论文

1. **Chen et al., 2016** - "Deep Feature Extraction and Classification of Hyperspectral Images" - 深度学习HSI分类
2. **Zhong et al., 2018** - "Spectral-Spatial Residual Network for Hyperspectral Image Classification" - 光谱-空间联合
3. **He et al., 2020** - "Hyperspectral Image Classification Based on Transformer" - Transformer for HSI

---

## 语义分割

### 这玩意儿到底是啥？

遥感语义分割就是给每个像素分类——这个像素是道路、那个是建筑、那片是植被。和普通语义分割的区别是：

**遥感特点：**
- **大尺寸图像**：卫星图像通常很大，需要分块处理
- **类别不平衡**：背景占大多数，目标类稀疏
- **边界模糊**：不同地物之间过渡模糊

```python
# U-Net for Remote Sensing Segmentation
class RSUNet(nn.Module):
    """遥感语义分割U-Net"""
    def __init__(self, in_channels=3, num_classes=10):
        super().__init__()

        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, 3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(),
                nn.Conv2d(out_c, out_c, 3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU()
            )

        # Encoder
        self.enc1 = conv_block(in_channels, 64)
        self.enc2 = conv_block(64, 128)
        self.enc3 = conv_block(128, 256)
        self.enc4 = conv_block(256, 512)

        self.pool = nn.MaxPool2d(2)

        # Decoder
        self.up3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3 = conv_block(512, 256)
        self.up2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2 = conv_block(256, 128)
        self.up1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec1 = conv_block(128, 64)

        self.final = nn.Conv2d(64, num_classes, 1)

    def forward(self, x):
        # Encode
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        # Decode with skip connections
        d3 = self.dec3(torch.cat([self.up3(e4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        return self.final(d1)
```

### 推荐论文

1. **Kemker et al., 2018** - "Algorithms for Semantic Segmentation of Multispectral Remote Sensing Imagery" - 多光谱分割综述
2. **Maggiori et al., 2017** - "Convolutional Neural Networks for Large-Scale Remote-Sensing Image Classification" - 大规模分割
3. **Chen et al., 2021** - "Remote Sensing Image Semantic Segmentation Based on Transformer" - Transformer分割

---

## 常用数据集

### 场景分类

| 数据集 | 类别数 | 样本数 | 分辨率 | 来源 |
|--------|--------|--------|--------|------|
| UC Merced | 21 | 2,100 | 0.3m | 航空 |
| NWPU-RESISC45 | 45 | 31,500 | 0.2-30m | Google Earth |
| AID | 30 | 10,000 | 0.5-8m | Google Earth |
| PatternNet | 38 | 30,400 | 0.06-4.7m | 航空/卫星 |

### 目标检测

| 数据集 | 目标类型 | 实例数 | 图像数 | 特点 |
|--------|----------|--------|--------|------|
| DOTA | 15类 | 188k | 2,806 | 旋转框，大图 |
| HRSC2016 | 舰船 | 2,976 | 1,074 | 旋转框 |
| UCAS-AOD | 飞机/车 | 7,482 | 1,510 | 旋转框 |
| xView | 60类 | 1M+ | 1,413 | 大规模 |

### 变化检测

| 数据集 | 图像对数 | 分辨率 | 变化类型 |
|--------|----------|--------|----------|
| LEVIR-CD | 637对 | 0.5m | 建筑 |
| WHU-CD | 1对大图 | 0.3m | 建筑 |
| SYSU-CD | 20,000对 | 0.5m | 多类型 |

### 高光谱

| 数据集 | 波段数 | 像素数 | 类别数 | 传感器 |
|--------|--------|--------|--------|--------|
| Indian Pines | 200 | 145×145 | 16 | AVIRIS |
| Pavia University | 103 | 610×340 | 9 | ROSIS |
| Salinas | 204 | 512×217 | 16 | AVIRIS |
| Houston 2013 | 144 | 349×1905 | 15 | CASI |

---

## 工具与框架

### 常用库

```python
# Rasterio - 遥感图像读写
import rasterio
from rasterio.plot import show

with rasterio.open('satellite.tif') as src:
    # 读取数据
    image = src.read()  # (C, H, W)
    metadata = src.meta
    crs = src.crs  # 坐标系
    transform = src.transform  # 仿射变换

# GDAL - 遥感数据处理
from osgeo import gdal

dataset = gdal.Open('image.tif')
band = dataset.GetRasterBand(1)
array = band.ReadAsArray()

# PyTorch Lightning训练框架
import pytorch_lightning as pl

class RSModule(pl.LightningModule):
    def __init__(self, model, lr=1e-4):
        super().__init__()
        self.model = model
        self.lr = lr

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = nn.CrossEntropyLoss()(y_hat, y)
        self.log('train_loss', loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.lr)
```

### 数据增强

```python
import albumentations as A
from albumentations.pytorch import ToTensorV2

# 遥感专用数据增强
rs_transforms = A.Compose([
    A.RandomRotate90(p=0.5),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.GaussNoise(p=0.2),
    A.Normalize(),
    ToTensorV2()
])
```

---

## 对比总结

| 任务 | 主流方法 | 核心挑战 | 推荐模型 |
|------|----------|----------|----------|
| 场景分类 | CNN/ViT | 类内差异 | ResNet, Swin |
| 目标检测 | Faster R-CNN/YOLO | 旋转、尺度 | Rotated RetinaNet |
| 变化检测 | 孪生网络 | 季节、光照 | BIT, ChangeFormer |
| 高光谱 | 3D-CNN/Transformer | 维度高、样本少 | HybirdSN |
| 语义分割 | U-Net/DeepLab | 大图、不平衡 | U-Net, SegFormer |

### 选择建议

```
场景分类 → ResNet + 数据增强
旋转目标检测 → Rotated RetinaNet / Oriented R-CNN
变化检测 → 孪生CNN / Transformer
高光谱分类 → 3D-CNN + 光谱注意力
语义分割 → U-Net / DeepLabV3+
```

---

> 遥感深度学习把天上的"眼睛"变成了智能分析师！CNN捕获局部特征，Transformer建模全局关系，高光谱能识别物质成分。选对模型，数据价值翻倍！