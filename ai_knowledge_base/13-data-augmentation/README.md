# 13. 数据增强/生成

> 师弟师妹们好！数据不够？质量不好？别慌！这篇文档讲透各种数据增强和生成技术，每个都有原理、代码和论文。记住：增强不是万能的，但不用增强是万万不能的！

## RandAugment（随机增强）

**核心思想**：不搜最优策略，直接随机选N个增强操作，每个操作用统一强度M。

**公式推导**：
- 增强池：T = {旋转, 裁剪, 颜色抖动, ...} 共K种操作
- 对每张图：
  1. 随机选N个操作（可重复）
  2. 每个操作用强度M（0-10的整数，映射到具体参数）
- **为什么有效**：大幅减少搜索空间（从$K^N$种策略到1种），靠随机性也能找到好策略

**PyTorch代码**：
```python
from torchvision import transforms as T
from PIL import Image

# 手动实现RandAugment核心逻辑
class RandAugment:
    def __init__(self, n=2, m=9):
        self.n = n  # 选n个操作
        self.m = m  # 强度m (0-10)
        self.augment_list = [
            (T.AutoContrast, 0, 1),
            (T.Equalize, 0, 1),
            (T.Invert, 0, 1),
            (T.Rotate, 0, 30),
            (T.Posterize, 0, 4),
            (T.Solarize, 0, 256),
            (T.ColorJitter, 0.1, 1.9),
            # ... 其他操作
        ]
        
    def __call__(self, img):
        ops = random.choices(self.augment_list, k=self.n)
        for op, min_val, max_val in ops:
            val = (float(self.m) / 10) * float(max_val - min_val) + min_val
            if random.random() > 0.5:  # 50%概率应用
                if op == T.ColorJitter:
                    img = op(brightness=val, contrast=val, saturation=val)(img)
                else:
                    img = op(val)(img)
        return img

# 使用
transform = T.Compose([
    T.Resize(224),
    RandAugment(n=2, m=9),
    T.ToTensor()
])
```

**推荐论文**：
1. [RandAugment: Practical automated data augmentation (2019)](https://arxiv.org/abs/1909.13719) - 提出RandAugment
2. [EfficientNet: Rethinking Model Scaling (2019)](https://arxiv.org/abs/1905.11946) - 用RandAugment训练EfficientNet
3. [Revisiting Unreasonable Effectiveness of Data (2017)](https://arxiv.org/abs/1707.02968) - 数据增强重要性分析

## AutoAugment（自动增强）

**核心思想**：用强化学习搜索最优增强策略——哪个操作、什么强度、用多少概率。

**公式推导**：
- 策略 = {(op, prob, mag), ...} 的序列
- 搜索过程：
  1. Controller RNN生成策略
  2. 用策略训练子模型
  3. 子模型验证集准确率作为reward
  4. 用policy gradient更新Controller
- **缺点**：搜索成本高（5000 GPU hours），但得到的策略可迁移

**PyTorch代码**（用现成策略）：
```python
# torchvision已内置AutoAugment策略
transform = T.Compose([
    T.AutoAugment(T.AutoAugmentPolicy.IMAGENET),
    T.ToTensor()
])

# 或用timm库
import timm
aa_params = dict(
    translate_const=int(224 * 0.45),
    img_mean=timm.data.constants.IMAGENET_DEFAULT_MEAN,
)
auto_augment_transform = timm.data.create_transform(
    input_size=224,
    is_training=True,
    auto_augment='rand-m9-mstd0.5'
)
```

**推荐论文**：
1. [AutoAugment: Learning Augmentation Policies (2018)](https://arxiv.org/abs/1805.09501) - 开创性自动增强工作
2. [Population Based Augmentation (2019)](https://arxiv.org/abs/1905.05393) - 进化算法搜索增强策略
3. [Fast AutoAugment (2019)](https://arxiv.org/abs/1905.00397) - 用密度匹配加速搜索

## Cutout（随机遮挡）

**核心思想**：随机遮掉图片一块区域，强迫模型不依赖局部特征。

**公式推导**：
- 在图像上随机选中心$(x,y)$，画边长$L$的正方形
- $L = \text{int}(\text{length} \times \text{image_size})$
- 遮挡区域填0（或均值）
- **为什么有效**：类似Dropout，提升泛化性，对遮挡鲁棒

**PyTorch代码**：
```python
class Cutout:
    def __init__(self, length=16):
        self.length = length
        
    def __call__(self, img):
        h, w = img.size(1), img.size(2)
        mask = torch.ones_like(img)
        y = torch.randint(h, ())
        x = torch.randint(w, ())
        y1 = torch.clamp(y - self.length // 2, 0, h)
        y2 = torch.clamp(y + self.length // 2, 0, h)
        x1 = torch.clamp(x - self.length // 2, 0, w)
        x2 = torch.clamp(x + self.length // 2, 0, w)
        mask[:, y1:y2, x1:x2] = 0
        return img * mask

# 使用
transform = T.Compose([
    T.ToTensor(),
    Cutout(length=16)
])
```

**推荐论文**：
1. [Improved Regularization of Convolutional Neural Networks (2017)](https://arxiv.org/abs/1708.04552) - 提出Cutout
2. [Shake-Shake Regularization (2017)](https://arxiv.org/abs/1705.07485) - 和Cutout一起用效果好
3. [Random Erasing Data Augmentation (2017)](https://arxiv.org/abs/1708.04896) - Cutout的变种（填随机值）

## Mixup（像素级混合）

**核心思想**：线性插值两张图和标签，创造新样本。

**公式推导**：
- 选两张图$(x_i,y_i)$, $(x_j,y_j)$
- 混合：$\hat{x} = \lambda x_i + (1-\lambda) x_j$
- $\hat{y} = \lambda y_i + (1-\lambda) y_j$
- $\lambda \sim \text{Beta}(\alpha, \alpha)$, α控制混合程度（α=0.2常用）
- **为什么有效**：鼓励模型在样本间线性行为，提升泛化和鲁棒性

**PyTorch代码**：
```python
class Mixup:
    def __init__(self, alpha=0.2):
        self.alpha = alpha
        
    def __call__(self, x, y):
        lam = np.random.beta(self.alpha, self.alpha)
        batch_size = x.size(0)
        index = torch.randperm(batch_size)
        mixed_x = lam * x + (1 - lam) * x[index]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam

# 训练时用
mixup = Mixup(alpha=0.2)
for x, y in dataloader:
    x, y_a, y_b, lam = mixup(x, y)
    pred = model(x)
    loss = lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)
```

**推荐论文**：
1. [mixup: Beyond Empirical Risk Minimization (2017)](https://arxiv.org/abs/1710.09412) - 提出Mixup
2. [On Mixup Training: Performance, Confidence, and Calibration (2020)](https://arxiv.org/abs/2001.06268) - Mixup的校准效果
3. [Manifold Mixup (2018)](https://arxiv.org/abs/1806.05236) - 在特征空间做Mixup

## CutMix（区域级混合）

**核心思想**：Cutout + Mixup——切一块区域从另一张图粘贴。

**公式推导**：
- 随机生成裁剪框R（宽w，高h）
- $\hat{x} = \begin{cases} x_i & \text{outside R} \\ x_j & \text{inside R} \end{cases}$
- $\hat{y} = \lambda y_i + (1-\lambda) y_j$, $\lambda = 1 - \frac{wh}{HW}$
- **优势**：保留图像整体结构（不像Mixup模糊），同时利用两图信息

**PyTorch代码**：
```python
class CutMix:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        
    def __call__(self, x, y):
        lam = np.random.beta(self.alpha, self.alpha)
        batch_size = x.size(0)
        index = torch.randperm(batch_size)
        
        # 生成裁剪框
        bbx1, bby1, bbx2, bby2 = rand_bbox(x.size(), lam)
        x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
        
        # 调整lambda
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size()[-1] * x.size()[-2]))
        y_a, y_b = y, y[index]
        return x, y_a, y_b, lam

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
1. [CutMix: Regularization Strategy to Train Strong Classifiers (2019)](https://arxiv.org/abs/1905.04899) - 提出CutMix
2. [Puzzle Mix (2020)](https://arxiv.org/abs/2004.08514) - 基于显著性的CutMix改进
3. [Saliency Mix (2020)](https://arxiv.org/abs/2006.05973) - 用显著性图指导CutMix区域

## Mosaic（四图拼接）

**核心思想**：四张图缩放到1/4大小，拼成一张大图，增加小目标检测能力。

**公式推导**：
- 选四张图$I_1,I_2,I_3,I_4$
- 缩放到$(H/2, W/2)$
- 拼接：$\begin{bmatrix} I_1 & I_2 \\ I_3 & I_4 \end{bmatrix}$
- 标签坐标相应调整
- **优势**：一次看到多图上下文，提升小目标检测（小目标在原图占比小，拼接后相对变大）

**PyTorch代码**：
```python
def mosaic(images, labels, img_size=640):
    # images: [4, C, H, W], labels: [4, num_boxes, 5] (class, x, y, w, h)
    mosaic_img = torch.zeros(3, img_size, img_size)
    mosaic_labels = []
    
    # 随机选中心点（不一定是正中心）
    yc, xc = [int(random.uniform(-x, 2*img_size + x)) for x in (-img_size//2, -img_size//2)]
    
    for i in range(4):
        img = images[i]
        h, w = img.shape[1:]
        
        # 放置位置
        if i == 0:  # top left
            x1a, y1a, x2a, y2a = max(xc - w, 0), max(yc - h, 0), xc, yc
            x1b, y1b, x2b, y2b = w - (x2a - x1a), h - (y2a - y1a), w, h
        elif i == 1:  # top right
            x1a, y1a, x2a, y2a = xc, max(yc - h, 0), min(xc + w, img_size), yc
            x1b, y1b, x2b, y2b = 0, h - (y2a - y1a), min(w, x2a - x1a), h
        # ... 类似处理i=2,3
        
        mosaic_img[:, y1a:y2a, x1a:x2a] = img[:, y1b:y2b, x1b:x2b]
        
        # 调整标签坐标
        padw = x1a - x1b
        padh = y1a - y1b
        if labels[i].size(0) > 0:
            labels[i][:, 1:] = xywhn2xyxy(labels[i][:, 1:], w, h, padw, padh)
            mosaic_labels.append(labels[i])
    
    mosaic_labels = torch.cat(mosaic_labels, 0) if mosaic_labels else torch.zeros((0, 5))
    return mosaic_img, mosaic_labels
```

**推荐论文**：
1. [YOLOv4: Optimal Speed and Accuracy (2020)](https://arxiv.org/abs/2004.10934) - 首次在YOLO用Mosaic
2. [YOLOv5 (2020)](https://github.com/ultralytics/yolov5) - 官方实现Mosaic
3. [PP-YOLO (2020)](https://arxiv.org/abs/2007.12099) - 用Mosaic提升检测性能

## Copy-Paste（实例粘贴）

**核心思想**：从一张图复制物体实例，粘贴到另一张图，解决少样本问题。

**公式推导**：
- 有掩码标注时：直接复制掩码区域
- 无掩码时：用边界框近似（可能带背景）
- 粘贴位置：随机或基于场景合理性
- **关键**：保持实例的尺度、方向一致性

**PyTorch代码**（简化版）：
```python
def copy_paste(image, boxes, labels, masks, 
               paste_image, paste_boxes, paste_labels, paste_masks):
    # 随机选要粘贴的实例
    num_paste = random.randint(1, len(paste_boxes))
    indices = random.sample(range(len(paste_boxes)), num_paste)
    
    for idx in indices:
        box = paste_boxes[idx]
        mask = paste_masks[idx]
        x1, y1, x2, y2 = box.astype(int)
        
        # 复制实例
        instance = paste_image[:, y1:y2, x1:x2]
        instance_mask = mask[y1:y2, x1:x2]
        
        # 随机粘贴位置
        h, w = instance.shape[1:]
        new_x = random.randint(0, image.shape[2] - w)
        new_y = random.randint(0, image.shape[1] - h)
        
        # 粘贴（用mask融合）
        image[:, new_y:new_y+h, new_x:new_x+w] = \
            image[:, new_y:new_y+h, new_x:new_x+w] * (1 - instance_mask) + \
            instance * instance_mask
        
        # 添加新标签
        new_box = [new_x, new_y, new_x+w, new_y+h]
        boxes = torch.cat([boxes, torch.tensor(new_box).unsqueeze(0)])
        labels = torch.cat([labels, paste_labels[idx].unsqueeze(0)])
    
    return image, boxes, labels
```

**推荐论文**：
1. [Simple Copy-Paste is a Strong Data Augmentation Method (2020)](https://arxiv.org/abs/2012.07177) - Google提出Copy-Paste
2. [Instaboost (2019)](https://arxiv.org/abs/1908.07801) - 基于实例的增强
3. [TransWeather (2022)](https://arxiv.org/abs/2202.10116) - 用Copy-Paste做天气迁移

## GAN-based Augmentation（GAN生成增强）

**核心思想**：用GAN生成逼真新样本，尤其适合少样本场景。

**公式推导**：
- 训练一个Conditional GAN：$G(z, y) \to x$，y是类别标签
- 生成样本：$x_{\text{fake}} = G(z, y)$，z~N(0,1)
- **挑战**：模式崩溃（生成多样性不足）、训练不稳定
- **改进**：用WGAN-GP、Spectral Norm稳定训练

**PyTorch代码**（DCGAN风格）：
```python
# 生成器（简化）
class Generator(nn.Module):
    def __init__(self, nz=100, ngf=64, nc=3, num_classes=10):
        super().__init__()
        self.label_emb = nn.Embedding(num_classes, nz)
        self.main = nn.Sequential(
            # 输入: (nz+num_classes, 1, 1)
            nn.ConvTranspose2d(nz+num_classes, ngf*8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(ngf*8),
            nn.ReLU(True),
            # ... 更多层
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
            nn.Tanh()
        )
        
    def forward(self, z, labels):
        label_embedding = self.label_emb(labels).unsqueeze(2).unsqueeze(3)
        x = torch.cat([z, label_embedding], 1)
        return self.main(x)

# 生成新样本
z = torch.randn(batch_size, nz, 1, 1)
labels = torch.randint(0, num_classes, (batch_size,))
fake_images = G(z, labels)
```

**推荐论文**：
1. [Data Augmentation Generative Adversarial Networks (DAGAN, 2017)](https://arxiv.org/abs/1711.04340) - 少样本GAN增强
2. [TGAN (2018)](https://arxiv.org/abs/1803.00657) - 表格数据GAN增强
3. [CT-GAN (2019)](https://arxiv.org/abs/1907.00503) - 解决模式崩溃的GAN增强

## Diffusion-based Augmentation（扩散模型生成增强）

**核心思想**：用扩散模型生成高质量、多样化的样本，比GAN更稳定。

**公式推导**：
- 扩散过程：$q(x_t|x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t}x_{t-1}, \beta_t I)$
- 逆扩散：$p_\theta(x_{t-1}|x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t,t), \Sigma_\theta(x_t,t))$
- 条件生成：$p_\theta(x_0|y) = \int p_\theta(x_0|x_1) q(x_1|y) dx_1$
- **优势**：生成质量高、多样性好、训练稳定

**PyTorch代码**（用预训练模型）：
```python
# 用HuggingFace的DiffusionPipeline
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda")

# 生成新样本（给定文本提示）
prompt = "a photo of a cat"
images = pipe(prompt, num_images_per_prompt=4).images

# 或用Classifier-Free Guidance (CFG)
images = pipe(prompt, guidance_scale=7.5).images

# 对于特定领域，需微调模型（如DreamBooth）
```

**推荐论文**：
1. [Denoising Diffusion Probabilistic Models (DDPM, 2020)](https://arxiv.org/abs/2006.11239) - 扩散模型奠基
2. [High-Resolution Image Synthesis with Latent Diffusion Models (Stable Diffusion, 2022)](https://arxiv.org/abs/2112.10752) - 高效扩散模型
3. [Diffusion Augmentation for Medical Image Analysis (2023)](https://arxiv.org/abs/2303.15540) - 医学图像扩散增强

---
> 数据增强是免费的午餐！但记住：增强要符合任务需求（比如医学图像不能随便旋转）。先试简单方法（RandAugment, Mixup），再考虑复杂生成（GAN/Diffusion）。有问题随时找师兄！