# 25. 扩散模型

> 师弟师妹们好！扩散模型就是通过逐步添加和去除噪声来生成高质量图像。今天咱们用大白话+公式+代码，彻底搞懂各种扩散模型方法！

---

## DDPM（去噪扩散概率模型）

### 这玩意儿到底是啥？
DDPM是扩散模型的基础！它分两个阶段：前向扩散（加噪声）和反向生成（去噪声）。核心思想是：把数据分布转换成简单分布（比如高斯分布），然后学习如何逆转这个过程。

### 核心公式推导
**前向扩散过程**：
$$
q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t I)
$$

其中$\beta_t$是噪声调度参数。

**重参数化技巧**：
$$
x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)
$$

其中$\bar{\alpha}_t = \prod_{s=1}^t (1 - \beta_s)$。

**反向生成过程**：
$$
p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))
$$

**训练目标**（简化版）：
$$
\mathcal{L}_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| \epsilon - \epsilon_\theta(x_t, t) \|^2 \right]
$$

其中$\epsilon_\theta$是U-Net网络，预测添加的噪声。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class DDPM(nn.Module):
    def __init__(self, denoise_model, betas):
        super().__init__()
        self.denoise_model = denoise_model
        self.num_timesteps = len(betas)
        
        # 预计算α和累积α
        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        alphas_cumprod_prev = F.pad(alphas_cumprod[:-1], (1, 0), value=1.0)
        
        self.register_buffer('betas', betas)
        self.register_buffer('alphas', alphas)
        self.register_buffer('alphas_cumprod', alphas_cumprod)
        self.register_buffer('alphas_cumprod_prev', alphas_cumprod_prev)
        
        # 计算方差
        self.register_buffer('sqrt_alphas_cumprod', torch.sqrt(alphas_cumprod))
        self.register_buffer('sqrt_one_minus_alphas_cumprod', torch.sqrt(1.0 - alphas_cumprod))
        
    def q_sample(self, x_start, t, noise=None):
        """前向扩散：给x_start添加t步噪声"""
        if noise is None:
            noise = torch.randn_like(x_start)
            
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
        
        return sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
    
    def p_losses(self, x_start, t, noise=None):
        """计算训练损失"""
        if noise is None:
            noise = torch.randn_like(x_start)
            
        x_noisy = self.q_sample(x_start, t, noise)
        predicted_noise = self.denoise_model(x_noisy, t)
        
        loss = F.mse_loss(noise, predicted_noise)
        return loss
    
    def p_sample(self, x, t):
        """单步去噪采样"""
        batch_size = x.shape[0]
        device = x.device
        
        with torch.no_grad():
            noise_pred = self.denoise_model(x, t)
            
            # 计算均值
            alpha_t = self.alphas[t].view(batch_size, 1, 1, 1)
            alpha_cumprod_t = self.alphas_cumprod[t].view(batch_size, 1, 1, 1)
            alpha_cumprod_prev_t = self.alphas_cumprod_prev[t].view(batch_size, 1, 1, 1)
            
            mu = (1.0 / torch.sqrt(alpha_t)) * (
                x - ((1.0 - alpha_t) / torch.sqrt(1.0 - alpha_cumprod_t)) * noise_pred
            )
            
            # 添加噪声（除了最后一步）
            if t[0] > 0:
                sigma = torch.sqrt((1.0 - alpha_cumprod_prev_t) / (1.0 - alpha_cumprod_t) * (1.0 - alpha_t))
                noise = torch.randn_like(x)
                mu = mu + sigma * noise
                
        return mu
    
    def sample(self, batch_size, image_size, channels=3):
        """完整采样过程"""
        device = next(self.denoise_model.parameters()).device
        x = torch.randn(batch_size, channels, image_size, image_size).to(device)
        
        for t in reversed(range(self.num_timesteps)):
            t_tensor = torch.full((batch_size,), t, device=device, dtype=torch.long)
            x = self.p_sample(x, t_tensor)
            
        return x

# U-Net去噪网络（简化版）
class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=3, time_emb_dim=256):
        super().__init__()
        self.time_mlp = nn.Sequential(
            nn.Linear(1, time_emb_dim),
            nn.ReLU(),
            nn.Linear(time_emb_dim, time_emb_dim)
        )
        
        # 简化的U-Net结构
        self.conv1 = nn.Conv2d(in_channels, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.conv4 = nn.Conv2d(256, 128, 3, padding=1)
        self.conv5 = nn.Conv2d(128, 64, 3, padding=1)
        self.conv6 = nn.Conv2d(64, out_channels, 3, padding=1)
        
    def forward(self, x, t):
        # 时间嵌入
        t_emb = self.time_mlp(t.float().unsqueeze(1))
        t_emb = t_emb.view(t_emb.size(0), -1, 1, 1)
        
        # U-Net前向传播
        x1 = F.relu(self.conv1(x))
        x2 = F.relu(self.conv2(x1))
        x3 = F.relu(self.conv3(x2 + t_emb))
        x4 = F.relu(self.conv4(x3))
        x5 = F.relu(self.conv5(x4))
        out = self.conv6(x5)
        
        return out

# 使用示例
betas = torch.linspace(0.0001, 0.02, 1000)  # 线性噪声调度
denoise_model = UNet()
ddpm = DDPM(denoise_model, betas)

# 训练
x_start = torch.randn(32, 3, 32, 32)  # 假设32x32图像
t = torch.randint(0, 1000, (32,))
loss = ddpm.p_losses(x_start, t)
print(f"Training loss: {loss.item():.6f}")

# 采样
samples = ddpm.sample(4, 32)
print(f"Sample shape: {samples.shape}")
```

### 推荐论文
1. Ho et al., "Denoising Diffusion Probabilistic Models", NeurIPS 2020
2. Song et al., "Score-Based Generative Modeling through Stochastic Differential Equations", ICLR 2021
3. Nichol & Dhariwal, "Improved Denoising Diffusion Probabilistic Models", ICML 2021

---

## DDIM（去噪扩散隐式模型）

### 这玩意儿到底是啥？
DDIM是DDPM的加速版本！它通过非马尔可夫过程实现更快的采样，可以在很少的步骤内生成高质量样本。

### 核心公式推导
**DDIM采样方程**：
$$
x_{t-1} = \sqrt{\bar{\alpha}_{t-1}} \left( \frac{x_t - \sqrt{1 - \bar{\alpha}_t} \epsilon_\theta(x_t, t)}{\sqrt{\bar{\alpha}_t}} \right) + \sqrt{1 - \bar{\alpha}_{t-1} - \sigma_t^2} \cdot \epsilon_\theta(x_t, t) + \sigma_t \epsilon
$$

**确定性采样**（$\sigma_t = 0$）：
$$
x_{t-1} = \sqrt{\bar{\alpha}_{t-1}} \left( \frac{x_t - \sqrt{1 - \bar{\alpha}_t} \epsilon_\theta(x_t, t)}{\sqrt{\bar{\alpha}_t}} \right) + \sqrt{1 - \bar{\alpha}_{t-1}} \cdot \epsilon_\theta(x_t, t)
$$

**关键洞察**：
- DDPM必须按顺序采样所有步骤
- DDIM可以跳过中间步骤，直接从$t$跳到$t'$  
- 当$\sigma_t = 0$时，采样过程是确定性的

### PyTorch代码示例
```python
class DDIMSampler:
    def __init__(self, ddpm_model):
        self.ddpm = ddpm_model
        
    def sample(self, x_T, timesteps, eta=0.0):
        """
        DDIM采样
        x_T: 初始噪声
        timesteps: 采样时间步列表，如[999, 799, 599, ...]
        eta: 控制随机性的参数 (eta=0 -> 确定性, eta=1 -> DDPM)
        """
        x = x_T
        device = x.device
        
        for i in range(len(timesteps) - 1):
            t = torch.full((x.size(0),), timesteps[i], device=device, dtype=torch.long)
            t_next = torch.full((x.size(0),), timesteps[i+1], device=device, dtype=torch.long)
            
            # 预测噪声
            with torch.no_grad():
                epsilon = self.ddpm.denoise_model(x, t)
                
            # 计算x0的估计
            alpha_cumprod_t = self.ddpm.alphas_cumprod[t].view(-1, 1, 1, 1)
            sqrt_one_minus_alpha_cumprod_t = self.ddpm.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
            
            x0_pred = (x - sqrt_one_minus_alpha_cumprod_t * epsilon) / torch.sqrt(alpha_cumprod_t)
            
            # 计算下一步的x
            alpha_cumprod_t_next = self.ddpm.alphas_cumprod[t_next].view(-1, 1, 1, 1)
            sigma_t = eta * torch.sqrt(
                (1 - alpha_cumprod_t_next) / (1 - alpha_cumprod_t) * 
                (1 - alpha_cumprod_t / alpha_cumprod_t_next)
            )
            
            if timesteps[i+1] == 0:
                sigma_t = 0  # 最后一步不加噪声
                
            mean_pred = torch.sqrt(alpha_cumprod_t_next) * x0_pred + \
                       torch.sqrt(1 - alpha_cumprod_t_next - sigma_t**2) * epsilon
            
            if sigma_t > 0:
                noise = torch.randn_like(x)
                x = mean_pred + sigma_t * noise
            else:
                x = mean_pred
                
        return x

# 使用示例
ddim_sampler = DDIMSampler(ddpm)
x_T = torch.randn(4, 3, 32, 32)
timesteps = [999, 799, 599, 399, 199, 0]  # 只用6步采样
samples_ddim = ddim_sampler.sample(x_T, timesteps, eta=0.0)
print(f"DDIM samples shape: {samples_ddim.shape}")
print(f"DDIM steps: {len(timesteps)-1}")
```

### 推荐论文
1. Song et al., "Denoising Diffusion Implicit Models", ICLR 2021
2. Lu et al., "DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling", NeurIPS 2022
3. Liu et al., "Pseudo Numerical Methods for Diffusion Models on Manifolds", ICLR 2022

---

## Latent Diffusion（潜在扩散）

### 这玩意儿到底是啥？
潜在扩散就是在低维潜在空间中进行扩散，而不是在像素空间！先用VAE把图像压缩到潜在空间，然后在潜在空间中做扩散，大大减少计算开销。

### 核心公式推导
**VAE编码**：
$$
z = \mathcal{E}(x), \quad x = \mathcal{D}(z)
$$

**潜在空间扩散**：
$$
q(z_t | z_{t-1}) = \mathcal{N}(z_t; \sqrt{1-\beta_t} z_{t-1}, \beta_t I)
$$

**训练目标**：
$$
\mathcal{L} = \lambda_{\text{diffusion}} \mathbb{E}[\|\epsilon - \epsilon_\theta(z_t, t)\|^2] + \lambda_{\text{recon}} \mathbb{E}[\|x - \mathcal{D}(\mathcal{E}(x))\|^2] + \lambda_{\text{kl}} D_{KL}(q(z|x) \| p(z))
$$

**优势**：
- 潜在空间维度比像素空间小得多（64x64 vs 512x512）
- 训练和采样速度大幅提升
- 内存占用大幅减少

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from diffusers import AutoencoderKL

class LatentDiffusion(nn.Module):
    def __init__(self, vae_model="stabilityai/sd-vae-ft-mse", unet_model=None):
        super().__init__()
        # VAE编码器/解码器
        self.vae = AutoencoderKL.from_pretrained(vae_model)
        for param in self.vae.parameters():
            param.requires_grad = False
            
        # 潜在空间扩散模型
        self.unet = unet_model or UNet(in_channels=4, out_channels=4)  # 潜在空间通常是4通道
        
    def encode_to_latent(self, images):
        """将图像编码到潜在空间"""
        with torch.no_grad():
            latent_dist = self.vae.encode(images)
            latents = latent_dist.latent_dist.sample()
            latents = latents * self.vae.config.scaling_factor
        return latents
    
    def decode_from_latent(self, latents):
        """从潜在空间解码到图像"""
        latents = latents / self.vae.config.scaling_factor
        with torch.no_grad():
            images = self.vae.decode(latents).sample
        return images
    
    def forward(self, images, timesteps, noise=None):
        """训练前向传播"""
        # 编码到潜在空间
        latents = self.encode_to_latent(images)
        
        # 添加噪声
        if noise is None:
            noise = torch.randn_like(latents)
        noisy_latents = self.q_sample(latents, timesteps, noise)
        
        # 预测噪声
        noise_pred = self.unet(noisy_latents, timesteps)
        
        loss = F.mse_loss(noise, noise_pred)
        return loss

# 使用示例（概念演示）
latent_diffusion = LatentDiffusion()

# 训练
images = torch.randn(4, 3, 512, 512)  # 高分辨率图像
timesteps = torch.randint(0, 1000, (4,))
loss = latent_diffusion(images, timesteps)
print(f"Latent diffusion loss: {loss.item():.6f}")

# 采样（需要DDIM或DDPM采样器适配潜在空间）
# 这里省略具体实现
```

### 推荐论文
1. Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022
2. Saharia et al., "Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding", NeurIPS 2022
3. Peebles & Xie, "Scalable Diffusion Models with Transformers", ICCV 2023

---

## Stable Diffusion

### 这玩意儿到底是啥？
Stable Diffusion是Latent Diffusion的具体实现！它结合了文本条件、潜在扩散和大规模训练，成为最流行的文本到图像生成模型。

### 核心公式推导
**文本条件扩散**：
$$
\epsilon_\theta(z_t, t, c) = \text{UNet}(z_t, t, \text{CLIP}(c))
$$

其中$c$是文本提示，CLIP是文本编码器。

**Classifier-Free Guidance**：
$$
\hat{\epsilon}_\theta(z_t, t, c) = (1 + w) \cdot \epsilon_\theta(z_t, t, c) - w \cdot \epsilon_\theta(z_t, t, \emptyset)
$$

其中$w$是引导权重，$\emptyset$表示空文本。

**训练目标**：
以一定概率$p$使用真实文本，以概率$(1-p)$使用空文本：
$$
\mathcal{L} = \mathbb{E}_{x,c,t,\epsilon}[\|\epsilon - \epsilon_\theta(z_t, t, c_{\text{train}})\|^2]
$$

### PyTorch代码示例
```python
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import StableDiffusionPipeline

class StableDiffusionWrapper:
    def __init__(self, model_name="runwayml/stable-diffusion-v1-5"):
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            safety_checker=None
        )
        self.pipeline = self.pipeline.to("cuda")
        
    def generate_image(self, prompt, negative_prompt="", num_inference_steps=50, guidance_scale=7.5):
        """生成图像"""
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=512,
            width=512
        ).images[0]
        return image
    
    def get_text_embeddings(self, prompts):
        """获取文本嵌入"""
        tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14")
        
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            embeddings = text_encoder(inputs.input_ids).last_hidden_state
        return embeddings

# 使用示例
sd = StableDiffusionWrapper()

# 文本到图像生成
prompt = "a beautiful landscape with mountains and lake"
image = sd.generate_image(prompt, guidance_scale=8.0)
image.save("generated_landscape.png")

# 获取文本嵌入
embeddings = sd.get_text_embeddings(["a cat", "a dog"])
print(f"Text embeddings shape: {embeddings.shape}")

# 高级用法：自定义采样
def custom_sampling(sd_pipeline, prompt, steps=20):
    """自定义采样过程"""
    from diffusers import DDIMScheduler
    
    # 设置调度器
    sd_pipeline.scheduler = DDIMScheduler.from_config(sd_pipeline.scheduler.config)
    
    # 准备输入
    text_input = sd_pipeline.tokenizer(
        prompt,
        padding="max_length",
        max_length=sd_pipeline.tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt"
    )
    
    with torch.no_grad():
        text_embeddings = sd_pipeline.text_encoder(text_input.input_ids.to(sd_pipeline.device))[0]
        
    # 初始化潜在表示
    latents = torch.randn(
        (1, sd_pipeline.unet.config.in_channels, 64, 64),
        device=sd_pipeline.device
    )
    
    # 采样循环
    sd_pipeline.scheduler.set_timesteps(steps)
    for t in sd_pipeline.scheduler.timesteps:
        latent_model_input = torch.cat([latents] * 2)
        latent_model_input = sd_pipeline.scheduler.scale_model_input(latent_model_input, t)
        
        with torch.no_grad():
            noise_pred = sd_pipeline.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample
            
        # Classifier-free guidance
        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
        noise_pred = noise_pred_uncond + 7.5 * (noise_pred_text - noise_pred_uncond)
        
        latents = sd_pipeline.scheduler.step(noise_pred, t, latents).prev_sample
        
    # 解码到图像
    latents = 1 / 0.18215 * latents
    image = sd_pipeline.vae.decode(latents).sample
    image = (image / 2 + 0.5).clamp(0, 1)
    return image

# 自定义采样
custom_image = custom_sampling(sd.pipeline, "a futuristic cityscape", steps=30)
```

### 推荐论文
1. Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022
2. Ho & Salimans, "Classifier-Free Diffusion Guidance", NeurIPS Workshop 2022
3. Saharia et al., "Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding", NeurIPS 2022

---
> 扩散模型是生成式AI的革命！DDPM奠定基础，DDIM加速采样，Latent Diffusion提升效率，Stable Diffusion实现文本到图像生成。记住：好的扩散模型需要精心设计的噪声调度、强大的去噪网络和高效的采样算法！