# 15. 量化

> 师弟师妹们好！量化就是把高精度的模型（比如32位浮点数）转换成低精度（比如8位整数），让模型变小、变快，还能在手机等设备上跑起来。今天咱们用大白话+公式+代码，彻底搞懂各种量化方法！

---

## Post-Training Quantization (PTQ)

### 这玩意儿到底是啥？
训练完再量化！先把模型训好，然后直接把权重和激活值从浮点数转成整数，不需要重新训练。简单粗暴，适合快速部署。

### 核心公式推导
**量化映射**：
$$
x_{int} = \text{round}\left(\frac{x_{float}}{s} + z\right)
$$

**反量化映射**：
$$
x_{float} = s \cdot (x_{int} - z)
$$

其中：
- $s$ 是缩放因子（scale）
- $z$ 是零点（zero point，整数）
- $x_{int} \in [0, 255]$ 对于8位无符号整数

**缩放因子计算**：
对于对称量化（z=0）：
$$
s = \frac{\max(|x_{min}|, |x_{max}|)}{2^{b-1} - 1}
$$

对于非对称量化：
$$
s = \frac{x_{max} - x_{min}}{2^b - 1}, \quad z = \text{round}\left(\frac{-x_{min}}{s}\right)
$$

**为什么这样设计？**
- 缩放因子$s$确保浮点数范围能映射到整数范围
- 零点$z$确保浮点数0能精确映射到整数（避免bias量化误差）

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.quantization as quant

# 方法1：使用PyTorch内置的PTQ
model = ...  # 预训练模型
model.eval()

# 设置量化配置
model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
# 或者使用qnnpack（ARM处理器）
# model.qconfig = torch.quantization.get_default_qconfig('qnnpack')

# 准备模型进行静态量化
quantized_model = torch.quantization.prepare(model, inplace=False)

# 校准：用少量数据确定量化参数
calibration_data = ...  # 少量校准数据
with torch.no_grad():
    for data in calibration_data:
        quantized_model(data)

# 转换为量化模型
quantized_model = torch.quantization.convert(quantized_model, inplace=True)

# 方法2：手动实现量化
class ManualQuantizer:
    def __init__(self, bits=8):
        self.bits = bits
        self.qmin = 0
        self.qmax = 2**bits - 1
        
    def calibrate(self, x):
        """校准：计算缩放因子和零点"""
        self.x_min = x.min()
        self.x_max = x.max()
        
        # 非对称量化
        self.scale = (self.x_max - self.x_min) / (self.qmax - self.qmin)
        self.zero_point = self.qmin - torch.round(self.x_min / self.scale)
        self.zero_point = torch.clamp(self.zero_point, self.qmin, self.qmax)
        
    def quantize(self, x):
        """量化：浮点数 -> 整数"""
        x_int = torch.round(x / self.scale + self.zero_point)
        x_int = torch.clamp(x_int, self.qmin, self.qmax)
        return x_int.to(torch.uint8)
    
    def dequantize(self, x_int):
        """反量化：整数 -> 浮点数"""
        x_float = self.scale * (x_int.float() - self.zero_point)
        return x_float

# 使用示例
quantizer = ManualQuantizer(bits=8)
dummy_input = torch.randn(1, 3, 224, 224)
quantizer.calibrate(dummy_input)

# 量化权重
weight = torch.randn(64, 3, 3, 3)
quantizer.calibrate(weight)
weight_quant = quantizer.quantize(weight)
weight_dequant = quantizer.dequantize(weight_quant)
```

### 推荐论文
1. Jacob et al., "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", CVPR 2018
2. Krishnamoorthi, "Quantizing deep convolutional networks for efficient inference: A whitepaper", arXiv 2018
3. Nagel et al., "A White Paper on Neural Network Quantization", arXiv 2021

---

## Quantization-Aware Training (QAT)

### 这玩意儿到底是啥？
边训练边量化！在训练过程中模拟量化过程，让模型适应量化带来的误差，效果比PTQ好很多。

### 核心公式推导
**伪量化操作**（Fake Quantization）：
$$
\hat{x} = \text{clip}\left(\text{round}\left(\frac{x}{s}\right) \cdot s, x_{min}, x_{max}\right)
$$

在训练时，前向传播使用伪量化，反向传播时梯度直接通过（Straight-Through Estimator）：
$$
\frac{\partial \hat{x}}{\partial x} = 1
$$

**为什么需要QAT？**
- PTQ在训练后直接量化，模型没有适应量化误差
- QAT让模型在训练时就"看到"量化效果，学会补偿量化误差
- 特别适合对量化敏感的模型（如Transformer）

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.quantization as quant

# 方法1：使用PyTorch内置的QAT
class QATModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, 1, 1)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(64, 128, 3, 1, 1)
        self.fc = nn.Linear(128, 10)
        
        # 添加量化感知模块
        self.quant = torch.quantization.QuantStub()
        self.dequant = torch.quantization.DeQuantStub()
        
    def forward(self, x):
        x = self.quant(x)
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = torch.flatten(x, 1)
        x = self.fc(x)
        x = self.dequant(x)
        return x

# 创建模型并设置QAT配置
model = QATModel()
model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
torch.quantization.prepare_qat(model, inplace=True)

# 训练模型（正常训练流程）
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
for epoch in range(10):
    for data, target in train_loader:
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()

# 转换为量化模型
model.eval()
quantized_model = torch.quantization.convert(model, inplace=True)

# 方法2：手动实现QAT
class FakeQuantize(nn.Module):
    def __init__(self, bits=8):
        super().__init__()
        self.bits = bits
        self.qmin = 0
        self.qmax = 2**bits - 1
        self.register_buffer('scale', torch.tensor(1.0))
        self.register_buffer('zero_point', torch.tensor(0.0))
        self.observer = None
        
    def observe(self, x):
        """观察输入分布，更新scale和zero_point"""
        if self.observer is None:
            self.observer = MinMaxObserver()
        self.observer(x)
        self.scale, self.zero_point = self.observer.calculate_qparams()
        
    def forward(self, x):
        if self.training:
            # 训练时：伪量化
            self.observe(x)
            x_quant = torch.fake_quantize_per_tensor_affine(
                x, self.scale, self.zero_point, self.qmin, self.qmax
            )
            return x_quant
        else:
            # 推理时：直接返回（实际量化在convert阶段处理）
            return x

class MinMaxObserver:
    def __init__(self):
        self.min_val = float('inf')
        self.max_val = float('-inf')
        
    def __call__(self, x):
        self.min_val = min(self.min_val, x.min().item())
        self.max_val = max(self.max_val, x.max().item())
        
    def calculate_qparams(self):
        qmin, qmax = 0, 255
        scale = (self.max_val - self.min_val) / (qmax - qmin)
        zero_point = qmin - round(self.min_val / scale)
        zero_point = max(qmin, min(qmax, zero_point))
        return torch.tensor(scale), torch.tensor(zero_point)
```

### 推荐论文
1. Esser et al., "Learned Step Size Quantization", ICLR 2020
2. Lou et al., "AutoQB: Automated Quantization and Bit-Width Selection for Deep Neural Networks", ICCAD 2020
3. Gong et al., "Mixed Precision Quantization with Adaptive Bitwidth", NeurIPS 2021

---

## SmoothQuant

### 这玩意儿到底是啥？
专门针对Transformer的量化方法！通过平滑激活值的分布，让权重和激活值都能用INT8量化，而不会损失太多精度。

### 核心公式推导
**问题分析**：
在Transformer中，激活值的分布往往很尖锐（有少数很大的值），导致量化时大部分信息丢失。

**SmoothQuant的核心思想**：
将权重矩阵$W$分解为两个部分：
$$
W = W \cdot D^{-1} \cdot D
$$

其中$D$是对角矩阵，用于平滑激活值：
$$
D_{ii} = \frac{1}{\max_j |X_{ji}|^\alpha}
$$

这样，原始的矩阵乘法$Y = XW$变成：
$$
Y = (XD) \cdot (D^{-1}W)
$$

- $XD$：平滑后的激活值，分布更均匀
- $D^{-1}W$：调整后的权重

**关键参数$\alpha$**：
- $\alpha = 0$：不平滑，只量化权重
- $\alpha = 1$：完全平滑，权重和激活值都容易量化
- 通常取$\alpha = 0.5$作为平衡点

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class SmoothQuantLinear(nn.Module):
    def __init__(self, linear_layer, alpha=0.5):
        super().__init__()
        self.alpha = alpha
        self.in_features = linear_layer.in_features
        self.out_features = linear_layer.out_features
        
        # 计算平滑因子
        weight = linear_layer.weight.data
        # 假设我们有激活值统计信息
        # 在实际应用中，需要在校准阶段收集激活值
        self.register_buffer('smooth_factor', torch.ones(self.in_features))
        
        # 初始化平滑后的权重
        self.register_parameter('smooth_weight', 
                              nn.Parameter(linear_layer.weight.data.clone()))
        if linear_layer.bias is not None:
            self.register_parameter('bias', 
                                  nn.Parameter(linear_layer.bias.data.clone()))
        else:
            self.bias = None
            
    def calibrate(self, activation_data):
        """校准：计算平滑因子"""
        # activation_data: [num_samples, in_features]
        act_abs_max = torch.max(torch.abs(activation_data), dim=0)[0]
        weight_abs_max = torch.max(torch.abs(self.smooth_weight.data), dim=0)[0]
        
        # 计算平滑因子
        smooth_factor = torch.pow(act_abs_max, self.alpha) / \
                       torch.pow(weight_abs_max, 1 - self.alpha)
        smooth_factor = torch.clamp(smooth_factor, min=1e-8)
        self.smooth_factor.copy_(smooth_factor)
        
        # 更新平滑后的权重
        smooth_weight = self.smooth_weight.data / self.smooth_factor.unsqueeze(0)
        self.smooth_weight.data.copy_(smooth_weight)
        
    def forward(self, x):
        # 平滑激活值
        x_smooth = x / self.smooth_factor
        # 矩阵乘法
        output = torch.nn.functional.linear(x_smooth, self.smooth_weight, self.bias)
        return output

# 完整的SmoothQuant流程
class SmoothQuantCalibrator:
    def __init__(self, model, alpha=0.5):
        self.model = model
        self.alpha = alpha
        self.hooks = []
        self.activation_cache = {}
        
    def register_hooks(self):
        """注册钩子来收集激活值"""
        def hook_fn(name):
            def hook(module, input, output):
                if name not in self.activation_cache:
                    self.activation_cache[name] = []
                self.activation_cache[name].append(input[0].detach().cpu())
            return hook
        
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                hook = module.register_forward_hook(hook_fn(name))
                self.hooks.append(hook)
                
    def calibrate(self, calibration_data):
        """执行校准"""
        self.register_hooks()
        
        with torch.no_grad():
            for data in calibration_data:
                _ = self.model(data)
                
        # 应用SmoothQuant
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear) and name in self.activation_cache:
                activations = torch.cat(self.activation_cache[name], dim=0)
                smooth_module = SmoothQuantLinear(module, self.alpha)
                smooth_module.calibrate(activations)
                
                # 替换原模块
                parent_name = '.'.join(name.split('.')[:-1])
                child_name = name.split('.')[-1]
                if parent_name:
                    parent = dict(self.model.named_modules())[parent_name]
                else:
                    parent = self.model
                setattr(parent, child_name, smooth_module)
                
        # 清理
        for hook in self.hooks:
            hook.remove()
        self.activation_cache.clear()
```

### 推荐论文
1. Xiao et al., "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", ICML 2023
2. Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", ICLR 2024
3. Dettmers et al., "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", NeurIPS 2022

---

## GPTQ (Generalized Post-Training Quantization)

### 这玩意儿到底是啥？
专门为大语言模型设计的量化方法！通过贪心策略逐层量化，同时最小化量化误差对后续层的影响。

### 核心公式推导
**Hessian矩阵近似**：
GPTQ使用二阶信息来指导量化顺序。对于权重矩阵$W$，其对损失函数的影响可以用Hessian矩阵$H$近似：
$$
\Delta L \approx \frac{1}{2} \text{vec}(\Delta W)^T H \text{vec}(\Delta W)
$$

**贪心量化策略**：
1. 按列处理权重矩阵（因为Transformer中权重通常是[out_features, in_features]）
2. 对每一列，选择使误差最小的量化值
3. 更新后续列的输入以补偿当前列的量化误差

**数学形式**：
假设我们要量化第j列$w_j$，已知前面j-1列的量化误差为$E_{1:j-1}$，那么第j列的最优量化为：
$$
w_j^{quant} = \arg\min_{\tilde{w}_j} \| X_{:,j} \odot (w_j - \tilde{w}_j) + \sum_{k=1}^{j-1} X_{:,k} \odot (w_k - w_k^{quant}) \|_2^2
$$

其中$X$是输入激活值。

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class GPTQQuantizer:
    def __init__(self, layer, bits=4):
        self.layer = layer
        self.bits = bits
        self.qmin = -(2**(bits-1))
        self.qmax = 2**(bits-1) - 1
        
    def quantize(self, X, W):
        """
        X: 输入激活值 [batch_size, in_features]
        W: 权重矩阵 [out_features, in_features]
        """
        out_features, in_features = W.shape
        W_quant = torch.zeros_like(W)
        errors = torch.zeros_like(X)
        
        # 计算Hessian矩阵的对角线（简化版）
        H = torch.zeros(in_features, in_features)
        for i in range(X.shape[0]):
            H += X[i:i+1].T @ X[i:i+1]
        H = H / X.shape[0]
        
        # 添加小常数防止除零
        H.diagonal().add_(1e-8)
        
        # 贪心量化
        for j in range(in_features):
            # 获取当前列的权重
            w_col = W[:, j]
            
            # 计算当前列的输入（考虑之前的误差）
            x_col = X[:, j] + errors[:, j]
            
            # 计算最优量化
            scale = (w_col.max() - w_col.min()) / (self.qmax - self.qmin)
            zero_point = self.qmin - torch.round(w_col.min() / scale)
            
            w_quant_col = torch.clamp(
                torch.round(w_col / scale + zero_point),
                self.qmin, self.qmax
            )
            w_quant_col = scale * (w_quant_col - zero_point)
            
            W_quant[:, j] = w_quant_col
            
            # 计算量化误差并传播到后续列
            error = (w_col - w_quant_col).unsqueeze(0)  # [1, out_features]
            if j < in_features - 1:
                # 更新后续列的输入
                residual = error @ W[:, j+1:].T  # [1, in_features-j-1]
                errors[:, j+1:] += residual
                
        return W_quant

# 使用GPTQ量化整个模型
def gptq_quantize_model(model, calibration_data, bits=4):
    model.eval()
    
    # 收集所有线性层
    linear_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            linear_layers.append((name, module))
    
    # 逐层量化
    for name, layer in linear_layers:
        print(f"Quantizing layer: {name}")
        
        # 收集该层的输入激活值
        activation_cache = []
        def hook_fn(module, input, output):
            activation_cache.append(input[0].detach())
            
        hook = layer.register_forward_hook(hook_fn)
        
        with torch.no_grad():
            for data in calibration_data[:10]:  # 用少量数据校准
                _ = model(data)
                
        hook.remove()
        activations = torch.cat(activation_cache, dim=0)
        
        # 执行GPTQ量化
        quantizer = GPTQQuantizer(layer, bits=bits)
        W_quant = quantizer.quantize(activations, layer.weight.data)
        
        # 替换权重
        layer.weight.data.copy_(W_quant)
        
    return model
```

### 推荐论文
1. Frantar et al., "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", ICLR 2023
2. Frantar et al., "SqueezeLLM: Dense-and-Sparse Quantization", ICLR 2024
3. Yao et al., "ZeroQuant: Efficient and Portable Post-Training Quantization", NeurIPS 2022

---

## AWQ (Activation-aware Weight Quantization)

### 这玩意儿到底是啥？
注意到并不是所有权重都同样重要！AWQ通过分析激活值的重要性，给重要的权重分配更多比特，不重要的权重用更少比特。

### 核心公式推导
**重要性评分**：
对于权重$w_{ij}$，其重要性由对应的激活值$x_j$决定：
$$
\text{importance}_{ij} = |x_j| \cdot |w_{ij}|
$$

**通道级重要性**：
对每个输入通道j，计算平均重要性：
$$
\text{channel_importance}_j = \frac{1}{N} \sum_{i=1}^N |x_j^{(i)}| \cdot \mathbb{E}[|w_{ij}|]
$$

**保护重要通道**：
AWQ发现，只需要保护约1%最重要的通道不被量化（或用更高精度），就能保持模型性能。

**量化策略**：
- 重要通道：保持FP16或INT8
- 其他通道：INT4量化

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class AWQQuantizer:
    def __init__(self, layer, bits=4, protect_ratio=0.01):
        self.layer = layer
        self.bits = bits
        self.protect_ratio = protect_ratio
        self.qmin = 0
        self.qmax = 2**bits - 1
        
    def find_important_channels(self, activations):
        """找到重要的输入通道"""
        # activations: [batch_size, in_features]
        avg_activation = torch.mean(torch.abs(activations), dim=0)
        weight_magnitude = torch.mean(torch.abs(self.layer.weight.data), dim=0)
        
        # 重要性评分
        importance = avg_activation * weight_magnitude
        num_protect = int(self.protect_ratio * importance.shape[0])
        
        # 找到最重要的通道
        _, important_indices = torch.topk(importance, num_protect, largest=True)
        protect_mask = torch.zeros_like(importance, dtype=torch.bool)
        protect_mask[important_indices] = True
        
        return protect_mask
        
    def quantize(self, activations):
        """执行AWQ量化"""
        protect_mask = self.find_important_channels(activations)
        
        # 分别处理保护通道和量化通道
        weight = self.layer.weight.data.clone()
        quant_weight = torch.zeros_like(weight)
        
        # 保护通道：保持原样
        quant_weight[:, protect_mask] = weight[:, protect_mask]
        
        # 量化通道：INT4量化
        non_protect_mask = ~protect_mask
        if torch.any(non_protect_mask):
            w_to_quant = weight[:, non_protect_mask]
            
            # 计算量化参数
            w_min = w_to_quant.min()
            w_max = w_to_quant.max()
            scale = (w_max - w_min) / (self.qmax - self.qmin)
            zero_point = self.qmin - torch.round(w_min / scale)
            
            # 量化
            w_quant = torch.clamp(
                torch.round(w_to_quant / scale + zero_point),
                self.qmin, self.qmax
            )
            w_quant = scale * (w_quant - zero_point)
            
            quant_weight[:, non_protect_mask] = w_quant
            
        return quant_weight, protect_mask

# 使用AWQ量化模型
def awq_quantize_model(model, calibration_data, bits=4, protect_ratio=0.01):
    model.eval()
    
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            print(f"Quantizing layer: {name}")
            
            # 收集激活值
            activation_cache = []
            def hook_fn(module, input, output):
                activation_cache.append(input[0].detach())
                
            hook = module.register_forward_hook(hook_fn)
            
            with torch.no_grad():
                for data in calibration_data[:10]:
                    _ = model(data)
                    
            hook.remove()
            activations = torch.cat(activation_cache, dim=0)
            
            # 执行AWQ量化
            quantizer = AWQQuantizer(module, bits=bits, protect_ratio=protect_ratio)
            quant_weight, protect_mask = quantizer.quantize(activations)
            
            # 替换权重
            module.weight.data.copy_(quant_weight)
            
            # 保存保护掩码（用于推理）
            module.register_buffer('awq_protect_mask', protect_mask)
            
    return model
```

### 推荐论文
1. Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", ICLR 2024
2. Xiao et al., "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", ICML 2023
3. Dettmers et al., "SpQR: Sparse-Quantized Representation for Near-Lossless 4-bit LLM Compression", ICLR 2024

---

## SpQR (Sparse-Quantized Representation)

### 这玩意儿到底是啥？
结合稀疏化和量化的终极方案！把权重分成三部分：重要权重（FP16）、可量化权重（INT4）、可剪枝权重（0）。

### 核心公式推导
**三路分解**：
对于权重矩阵$W$，分解为：
$$
W = W_{\text{important}} + W_{\text{quantizable}} + W_{\text{sparse}}
$$

其中：
- $W_{\text{important}}$：最重要的权重，保持FP16
- $W_{\text{quantizable}}$：可以安全量化的权重，用INT4
- $W_{\text{sparse}}$：接近零的权重，直接设为0

**重要性阈值**：
基于激活值和权重的乘积确定重要性：
$$
\text{score}_{ij} = |x_j| \cdot |w_{ij}|
$$

设定两个阈值：
- $\tau_1$：高于此阈值的权重为important
- $\tau_2$：低于此阈值的权重为sparse
- 中间的权重为quantizable

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class SpQRQuantizer:
    def __init__(self, layer, bits=4, tau1=0.99, tau2=0.01):
        self.layer = layer
        self.bits = bits
        self.tau1 = tau1  # important threshold
        self.tau2 = tau2  # sparse threshold
        self.qmin = 0
        self.qmax = 2**bits - 1
        
    def decompose_weights(self, activations):
        """三路分解权重"""
        # 计算重要性分数
        avg_activation = torch.mean(torch.abs(activations), dim=0)
        weight_abs = torch.abs(self.layer.weight.data)
        importance_scores = avg_activation.unsqueeze(0) * weight_abs
        
        # 展平并排序
        scores_flat = importance_scores.flatten()
        sorted_scores, _ = torch.sort(scores_flat)
        
        # 确定阈值
        idx1 = int(self.tau1 * len(sorted_scores))
        idx2 = int(self.tau2 * len(sorted_scores))
        threshold1 = sorted_scores[idx1]
        threshold2 = sorted_scores[idx2]
        
        # 创建掩码
        important_mask = importance_scores >= threshold1
        sparse_mask = importance_scores <= threshold2
        quantizable_mask = ~(important_mask | sparse_mask)
        
        return important_mask, quantizable_mask, sparse_mask
        
    def quantize(self, activations):
        """执行SpQR量化"""
        important_mask, quantizable_mask, sparse_mask = self.decompose_weights(activations)
        
        weight = self.layer.weight.data.clone()
        spqr_weight = torch.zeros_like(weight)
        
        # Important weights: keep as FP16
        spqr_weight[important_mask] = weight[important_mask]
        
        # Sparse weights: set to zero
        spqr_weight[sparse_mask] = 0.0
        
        # Quantizable weights: INT4 quantization
        if torch.any(quantizable_mask):
            w_to_quant = weight[quantizable_mask]
            
            # INT4 quantization
            w_min = w_to_quant.min()
            w_max = w_to_quant.max()
            scale = (w_max - w_min) / (self.qmax - self.qmin)
            zero_point = self.qmin - torch.round(w_min / scale)
            
            w_quant = torch.clamp(
                torch.round(w_to_quant / scale + zero_point),
                self.qmin, self.qmax
            )
            w_quant = scale * (w_quant - zero_point)
            
            spqr_weight[quantizable_mask] = w_quant
            
        return spqr_weight, important_mask, quantizable_mask, sparse_mask

# 使用SpQR量化模型
def spqr_quantize_model(model, calibration_data, bits=4):
    model.eval()
    
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            print(f"Applying SpQR to layer: {name}")
            
            # 收集激活值
            activation_cache = []
            def hook_fn(module, input, output):
                activation_cache.append(input[0].detach())
                
            hook = module.register_forward_hook(hook_fn)
            
            with torch.no_grad():
                for data in calibration_data[:10]:
                    _ = model(data)
                    
            hook.remove()
            activations = torch.cat(activation_cache, dim=0)
            
            # 执行SpQR量化
            quantizer = SpQRQuantizer(module, bits=bits)
            spqr_weight, imp_mask, quant_mask, sparse_mask = quantizer.quantize(activations)
            
            # 替换权重
            module.weight.data.copy_(spqr_weight)
            
            # 保存掩码信息
            module.register_buffer('spqr_important_mask', imp_mask)
            module.register_buffer('spqr_quantizable_mask', quant_mask)
            module.register_buffer('spqr_sparse_mask', sparse_mask)
            
    return model
```

### 推荐论文
1. Dettmers et al., "SpQR: Sparse-Quantized Representation for Near-Lossless 4-bit LLM Compression", ICLR 2024
2. Frantar et al., "SqueezeLLM: Dense-and-Sparse Quantization", ICLR 2024
3. Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", ICLR 2024

---
> 量化是个技术活！PTQ适合快速部署，QAT适合精度要求高的场景，SmoothQuant/GPTQ/AWQ/SpQR这些专门针对大模型的方法能让4-bit量化也能保持不错性能。记住：量化不是万能的，但合理的量化策略能让你的模型在手机上飞起来！