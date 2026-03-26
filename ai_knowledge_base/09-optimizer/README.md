# 9. 优化器

## SGD（随机梯度下降）

**核心思想**：用单个样本（或小批量）的梯度来更新参数，而不是整个数据集。

**公式推导**：
$$\theta_{t+1} = \theta_t - \eta \nabla_\theta J(\theta; x^{(i)}, y^{(i)})$$

其中 $\eta$ 是学习率，$\nabla_\theta J$ 是损失函数对参数的梯度。

**为什么有效**：计算快，内存占用小，适合大数据集。

**PyTorch代码**：
```python
import torch
import torch.nn as nn

model = nn.Linear(10, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
```

**推荐论文**：
1. Robbins, H., & Monro, S. (1951). A stochastic approximation method.
2. Bottou, L. (2010). Large-scale machine learning with stochastic gradient descent.
3. Zhang, C. (2004). Solving large scale linear prediction problems using stochastic gradient descent algorithms.

## SGD + Momentum（动量）

**核心思想**：引入动量项，让优化过程像小球下山一样有惯性，能越过局部极小值。

**公式推导**：
$$v_t = \beta v_{t-1} + (1-\beta) \nabla_\theta J(\theta_t)$$
$$\theta_{t+1} = \theta_t - \eta v_t$$

其中 $v_t$ 是速度（动量），$\beta$ 是动量系数（通常0.9）。

**为什么动量能加速**：在梯度方向一致的维度上，动量会累积，加速收敛；在震荡的维度上，动量会平滑震荡。

**PyTorch代码**：
```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
```

**推荐论文**：
1. Polyak, B. T. (1964). Some methods of speeding up the convergence of iteration methods.
2. Qian, N. (1999). On the momentum term in gradient descent learning algorithms.
3. Sutskever, I., et al. (2013). On the importance of initialization and momentum in deep learning.

## Adam（自适应学习率）

**核心思想**：结合动量和自适应学习率，为每个参数维护一阶矩（均值）和二阶矩（未中心化方差）。

**公式完整推导**：
1. 计算梯度：$g_t = \nabla_\theta J(\theta_t)$
2. 更新一阶矩（动量）：$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$
3. 更新二阶矩（平方梯度）：$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$
4. 偏差校正：$\hat{m}_t = m_t / (1-\beta_1^t)$, $\hat{v}_t = v_t / (1-\beta_2^t)$
5. 参数更新：$\theta_{t+1} = \theta_t - \eta \hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon)$

**为什么有效**：自适应调整每个参数的学习率，对稀疏梯度友好。

**PyTorch代码**：
```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999))
```

**推荐论文**：
1. Kingma, D. P., & Ba, J. (2015). Adam: A method for stochastic optimization.
2. Reddi, S. J., et al. (2018). On the convergence of Adam and beyond.
3. Balles, L., & Hennig, P. (2018). Dissecting Adam: The sign, magnitude and variance of stochastic gradients.

## AdamW（权重衰减解耦）

**核心思想**：将权重衰减与梯度更新解耦，避免Adam中L2正则化与自适应学习率的不良交互。

**公式推导**：
标准Adam + L2：$\theta_{t+1} = \theta_t - \eta (g_t + \lambda \theta_t) / \sqrt{v_t}$
AdamW：$\theta_{t+1} = \theta_t - \eta (g_t / \sqrt{v_t} + \lambda \theta_t)$

**为什么比Adam+L2好**：权重衰减独立于学习率，更符合正则化的原始意图，实验效果更好。

**PyTorch代码**：
```python
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

**推荐论文**：
1. Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization.
2. Zhang, H., et al. (2019). Lookahead optimizer: k steps forward, 1 step back.
3. Liu, Z., et al. (2020). On the variance of the adaptive learning rate and beyond.

## AdamW 8-bit

**核心思想**：用8位量化存储优化器状态（动量和方差），大幅减少显存占用。

**核心原理**：将32位浮点数压缩到8位整数，通过动态范围缩放保持精度。

**为什么省显存**：优化器状态从4字节降到1字节，显存占用减少75%。

**PyTorch代码**（需要bitsandbytes库）：
```python
import bitsandbytes as bnb
optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=0.001, weight_decay=0.01)
```

**推荐论文**：
1. Dettmers, T., et al. (2022). 8-bit optimizers via block-wise quantization.
2. Lin, X., et al. (2023). FP8 training with dynamic scaling.
3. Yao, Z., et al. (2021). ZeroQuant: Efficient and portable post-training quantization.

## LAMB / LARS（大batch分布式训练）

**核心思想**：Layer-wise Adaptive Rate Scaling，为每一层单独调整学习率，解决大batch训练不稳定问题。

**LARS公式**：
$$\eta_l = \eta \cdot \frac{\|w_l\|}{\|\nabla w_l\| + \beta \|w_l\|}$$
$$w_{l,t+1} = w_{l,t} - \eta_l \nabla w_{l,t}$$

**LAMB改进**：在LARS基础上加入Adam的自适应学习率。

**为什么有效**：大batch时梯度范数变化剧烈，LAMB/LARS通过层自适应稳定训练。

**PyTorch代码**（需要apex库）：
```python
from apex.contrib.optimizers import Lamb
optimizer = Lamb(model.parameters(), lr=0.001, betas=(0.9, 0.999))
```

**推荐论文**：
1. You, Y., et al. (2017). Large batch training of convolutional networks.
2. You, Y., et al. (2020). Large batch optimization for deep learning: Training BERT in 76 minutes.
3. Goyal, P., et al. (2017). Accurate, large minibatch SGD: Training ImageNet in 1 hour.

## AdaFactor（省显存原理）

**核心思想**：用低秩近似存储二阶矩信息，避免存储完整的$v_t$矩阵。

**省显存原理**：对于矩阵参数$W \in \mathbb{R}^{m \times n}$，不存储$m \times n$的$v_t$，而是存储行和列的统计量：
$$R_i = \sum_j v_{ij}, \quad C_j = \sum_i v_{ij}$$
然后用$v_{ij} \approx R_i C_j / \sum_k R_k$来近似。

**显存节省**：从$O(mn)$降到$O(m+n)$。

**PyTorch代码**（需要transformers库）：
```python
from transformers import Adafactor
optimizer = Adafactor(model.parameters(), lr=0.001, relative_step=False)
```

**推荐论文**：
1. Shazeer, N., & Stern, M. (2018). Adafactor: Adaptive learning rates with sublinear memory cost.
2. Anil, R., et al. (2019). Memory efficient adaptive optimization.
3. Chen, T., et al. (2020). Training language models with memory-efficient optimizers.

## Lion（符号优化器）

**核心思想**：只使用梯度的符号（sign）而不是梯度值本身进行更新，大幅减少计算量。

**公式推导**：
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$
$$\theta_{t+1} = \theta_t - \eta \cdot \text{sign}(m_t)$$

**为什么有效**：符号操作比浮点运算快，且在某些任务上效果不输Adam。

**PyTorch代码**：
```python
class Lion(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99)):
        defaults = dict(lr=lr, betas=betas)
        super().__init__(params, defaults)
    
    @torch.no_grad()
    def step(self):
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None: continue
                grad = p.grad
                state = self.state[p]
                if len(state) == 0:
                    state['exp_avg'] = torch.zeros_like(p)
                exp_avg = state['exp_avg']
                beta1, beta2 = group['betas']
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                p.add_(torch.sign(exp_avg), alpha=-group['lr'])
```

**推荐论文**：
1. Chen, X., et al. (2023). Symbolic discovery of optimization algorithms.
2. Bernstein, J., et al. (2018). signSGD: Compressed optimisation for non-convex problems.
3. Karimi, H., et al. (2020). Deep learning with signed gradients.

## Sophia（二阶优化器）

**核心思想**：用对角Hessian近似作为曲率信息，实现二阶优化效果。

**公式推导**：
$$\theta_{t+1} = \theta_t - \eta \cdot \text{clip}\left(\frac{m_t}{h_t + \epsilon}, -\rho, \rho\right)$$
其中$h_t$是对角Hessian的指数移动平均，$\rho$是裁剪阈值。

**为什么有效**：二阶信息能更好地处理病态条件数问题，收敛更快。

**PyTorch代码**：
```python
# 需要计算Hessian向量积，示例简化版
class SophiaG(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-4, betas=(0.965, 0.99), rho=0.04):
        defaults = dict(lr=lr, betas=betas, rho=rho)
        super().__init__(params, defaults)
    
    @torch.no_grad()
    def step(self, hessian):
        for group in self.param_groups:
            for p, h in zip(group['params'], hessian):
                if p.grad is None: continue
                grad, state = p.grad, self.state[p]
                if len(state) == 0:
                    state['exp_avg'] = torch.zeros_like(p)
                    state['hessian_exp'] = torch.zeros_like(p)
                exp_avg = state['exp_avg'].mul_(group['betas'][0]).add_(grad, alpha=1-group['betas'][0])
                hessian_exp = state['hessian_exp'].mul_(group['betas'][1]).add_(h, alpha=1-group['betas'][1])
                p.addcdiv_(exp_avg, hessian_exp + 1e-8, value=-group['lr']).clamp_(-group['rho'], group['rho'])
```

**推荐论文**：
1. Liu, M., et al. (2023). Sophia: A scalable stochastic second-order optimizer.
2. Martens, J. (2010). Deep learning via Hessian-free optimization.
3. Yao, Z., et al. (2021). AdaHessian: An adaptive second order optimizer.

## CAME（省显存优化器）

**核心思想**：结合AdamW的解耦权重衰减和8-bit量化，进一步优化显存效率。

**省显存原理**：在AdamW基础上应用块状量化（block-wise quantization），每个参数块独立量化。

**显存优势**：比普通AdamW节省75%显存，训练更大模型。

**PyTorch代码**（需要特定库）：
```python
# 目前PyTorch官方未集成，需第三方实现
# 参考: https://github.com/gxai/CAME
```

**推荐论文**：
1. Ma, X., et al. (2023). CAME: Consistent adaptive momentum estimation.
2. Dettmers, T., et al. (2022). 8-bit optimizers via block-wise quantization.
3. Zhang, H., et al. (2023). Memory-efficient optimizers for large language models.

## Adan（Adam+Nesterov）

**核心思想**：结合Adam的自适应学习率和Nesterov加速梯度，提升收敛速度。

**公式推导**：
1. 计算Nesterov梯度：$g_t = \nabla_\theta J(\theta_t - \beta_1 m_{t-1})$
2. 更新一阶矩：$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$
3. 更新二阶矩：$v_t = \beta_2 v_{t-1} + (1-\beta_2) (g_t + (1-\beta_1)(g_t - g_{t-1}))^2$
4. 参数更新：$\theta_{t+1} = \theta_t - \eta m_t / (\sqrt{v_t} + \epsilon)$

**为什么有效**：Nesterov提供更好的梯度估计，收敛更快更稳定。

**PyTorch代码**：
```python
# 需要第三方实现
class Adan(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.98, 0.92, 0.99), eps=1e-8):
        defaults = dict(lr=lr, betas=betas, eps=eps)
        super().__init__(params, defaults)
    
    @torch.no_grad()
    def step(self):
        # 实现略，参考官方代码
        pass
```

**推荐论文**：
1. Xie, X., et al. (2022). Adan: Adaptive Nesterov momentum algorithm.
2. Dozat, T. (2016). Incorporating Nesterov momentum into Adam.
3. Sutskever, I., et al. (2013). On the importance of initialization and momentum in deep learning.

## Schedule-Free Optimizer（不需要学习率调度）

**核心思想**：维护两个参数副本，通过插值自动实现学习率调度效果。

**核心公式**：
$$\theta_t = (1-\alpha_t) z_t + \alpha_t \bar{z}_t$$
其中$z_t$是主参数，$\bar{z}_t$是平均参数，$\alpha_t$随时间变化。

**为什么不需要调度**：算法内部自动实现了warmup和decay的效果。

**PyTorch代码**：
```python
# 需要schedule_free库
from schedulefree import ScheduleFreeAdamW
optimizer = ScheduleFreeAdamW(model.parameters(), lr=0.001)
optimizer.train()  # 训练模式
# optimizer.eval()   # 评估模式
```

**推荐论文**：
1. Defazio, A., & Jelassi, S. (2023). Schedule-free learning: A new baseline for adaptive optimization.
2. Mai, V., & Johansson, M. (2023). Accelerated first-order methods without a priori knowledge of smoothness.
3. Cutkosky, A., & Orabona, F. (2019). Momentumbased variance reduction in non-convex SGD.