# 10. 学习率调度

## StepLR（固定步长衰减）

**核心思想**：每隔固定epoch数，将学习率乘以衰减因子。

**公式**：
$$\eta_t = \eta_0 \cdot \gamma^{\lfloor t / \text{step\_size} \rfloor}$$

其中$\eta_0$是初始学习率，$\gamma$是衰减因子（如0.1），$t$是当前epoch。

**为什么有效**：训练后期需要更小的学习率来精细调整参数。

**PyTorch代码**：
```python
import torch.optim.lr_scheduler as lr_scheduler

optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
scheduler = lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

for epoch in range(100):
    train(...)
    scheduler.step()
```

**推荐论文**：
1. He, K., et al. (2016). Deep residual learning for image recognition.
2. Simonyan, K., & Zisserman, A. (2015). Very deep convolutional networks for large-scale image recognition.
3. Szegedy, C., et al. (2015). Going deeper with convolutions.

## CosineAnnealing（余弦退火）

**核心思想**：学习率按余弦函数从最大值衰减到最小值。

**公式**：
$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})(1 + \cos(\frac{T_{cur}}{T_{max}} \pi))$$

其中$T_{cur}$是当前epoch，$T_{max}$是总epoch数。

**为什么有效**：平滑衰减，避免StepLR的突变，有助于跳出局部最优。

**PyTorch代码**：
```python
scheduler = lr_scheduler.CosineAnnealingLR(optimizer, T_max=100, eta_min=0.001)
```

**推荐论文**：
1. Loshchilov, I., & Hutter, F. (2017). SGDR: Stochastic gradient descent with warm restarts.
2. Smith, L. N. (2017). Cyclical learning rates for training neural networks.
3. Huang, G., et al. (2017). Snapshot ensembles: Train 1, get M for free.

## Warmup + Cosine（LLM标配）

**核心思想**：先线性warmup到最大学习率，再余弦退火到0。

**为什么要warmup**：大模型训练初期梯度不稳定，小学习率让模型稳定后再增大。

**公式**：
$$\eta_t = \begin{cases}
\eta_{\max} \cdot \frac{t}{T_{warm}} & \text{if } t \leq T_{warm} \\
\eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})(1 + \cos(\frac{t - T_{warm}}{T_{total} - T_{warm}} \pi)) & \text{otherwise}
\end{cases}$$

**PyTorch代码**：
```python
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, SequentialLR

warmup_scheduler = LinearLR(optimizer, start_factor=0.01, total_iters=1000)
cosine_scheduler = CosineAnnealingLR(optimizer, T_max=9000, eta_min=0)
scheduler = SequentialLR(optimizer, [warmup_scheduler, cosine_scheduler], [1000])
```

**推荐论文**：
1. Vaswani, A., et al. (2017). Attention is all you need.
2. Brown, T., et al. (2020). Language models are few-shot learners.
3. Liu, Y., et al. (2019). RoBERTa: A robustly optimized BERT pretraining approach.

## OneCycleLR（一个周期）

**核心思想**：学习率先线性增加到最大学习率，再线性减少到最小学习率。

**公式**：
$$\eta_t = \begin{cases}
\eta_{\min} + (\eta_{\max} - \eta_{\min}) \cdot \frac{t}{T/2} & \text{if } t \leq T/2 \\
\eta_{\max} - (\eta_{\max} - \eta_{\min}) \cdot \frac{t - T/2}{T/2} & \text{otherwise}
\end{cases}$$

**为什么有效**：Super-convergence现象，能在更少epoch内达到更好效果。

**PyTorch代码**：
```python
scheduler = lr_scheduler.OneCycleLR(optimizer, max_lr=0.1, total_steps=10000)
```

**推荐论文**：
1. Smith, L. N. (2018). A disciplined approach to neural network hyper-parameters.
2. Smith, L. N., & Topin, N. (2019). Super-convergence: Very fast training of neural networks using large learning rates.
3. Gotmare, A., et al. (2019). A closer look at deep learning heuristics: Learning rate restarts, warmup and distillation.

## Linear Warmup + Linear Decay

**核心思想**：线性增加到最大学习率，再线性衰减到0。

**公式**：
$$\eta_t = \begin{cases}
\eta_{\max} \cdot \frac{t}{T_{warm}} & \text{if } t \leq T_{warm} \\
\eta_{\max} \cdot \frac{T_{total} - t}{T_{total} - T_{warm}} & \text{otherwise}
\end{cases}$$

**应用场景**：BERT等Transformer模型的标配调度策略。

**PyTorch代码**：
```python
from transformers import get_linear_schedule_with_warmup

scheduler = get_linear_schedule_with_warmup(
    optimizer, 
    num_warmup_steps=1000, 
    num_training_steps=10000
)
```

**推荐论文**：
1. Devlin, J., et al. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding.
2. Liu, Y., et al. (2019). RoBERTa: A robustly optimized BERT pretraining approach.
3. Clark, K., et al. (2020). ELECTRA: Pre-training text encoders as discriminators rather than generators.

## ReduceOnPlateau

**核心思想**：当验证损失不再下降时，降低学习率。

**触发条件**：如果连续`patience`个epoch验证损失没有改善，则学习率乘以`factor`。

**为什么有效**：自适应调整，避免过早或过晚衰减学习率。

**PyTorch代码**：
```python
scheduler = lr_scheduler.ReduceLROnPlateau(
    optimizer, 
    mode='min', 
    factor=0.1, 
    patience=10, 
    verbose=True
)

for epoch in range(100):
    train_loss = train(...)
    val_loss = validate(...)
    scheduler.step(val_loss)  # 注意：传入验证损失
```

**推荐论文**：
1. Bengio, Y. (2012). Practical recommendations for gradient-based training of deep architectures.
2. Goodfellow, I., et al. (2016). Deep learning.
3. Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization.

## Warmup-Stable-Decay (WSD)

**核心思想**：三阶段调度：warmup → stable → decay。

**公式**：
$$\eta_t = \begin{cases}
\eta_{\max} \cdot \frac{t}{T_{warm}} & \text{if } t \leq T_{warm} \\
\eta_{\max} & \text{if } T_{warm} < t \leq T_{stable} \\
\eta_{\max} \cdot \frac{T_{total} - t}{T_{total} - T_{stable}} & \text{otherwise}
\end{cases}$$

**为什么有效**：在stable阶段充分训练，在decay阶段精细调整。

**PyTorch代码**：
```python
def wsd_scheduler(optimizer, warmup_steps, stable_steps, total_steps, max_lr):
    def lr_lambda(current_step):
        if current_step < warmup_steps:
            return float(current_step) / float(max(1, warmup_steps))
        elif current_step < stable_steps:
            return 1.0
        else:
            return max(0.0, float(total_steps - current_step) / float(max(1, total_steps - stable_steps)))
    
    return lr_scheduler.LambdaLR(optimizer, lr_lambda)

scheduler = wsd_scheduler(optimizer, 1000, 8000, 10000, 0.001)
```

**推荐论文**：
1. Chinchilla paper: Hoffmann, J., et al. (2022). Training compute-optimal large language models.
2. Kaplan, J., et al. (2020). Scaling laws for neural language models.
3. Touvron, H., et al. (2023). Llama 2: Open foundation and fine-tuned chat models.