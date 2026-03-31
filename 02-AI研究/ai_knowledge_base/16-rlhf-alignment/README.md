# 16. RLHF对齐

> 师弟师妹们好！RLHF（基于人类反馈的强化学习）就是让大模型学会"说人话"，按照人类的喜好来回答问题。今天咱们用大白话+公式+代码，彻底搞懂各种对齐方法！

---

## PPO（近端策略优化）

### 这玩意儿到底是啥？
PPO是RLHF中最常用的强化学习算法！它通过限制策略更新的幅度，让训练更稳定。简单说就是：别一下子改太多，慢慢调，这样不容易崩。

### 核心公式推导
**策略梯度目标**：
$$
L^{CLIP}(\theta) = \mathbb{E}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

其中：
- $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ 是重要性采样比率
- $\hat{A}_t$ 是优势函数（advantage）
- $\epsilon$ 是裁剪参数（通常0.1-0.2）

**为什么需要裁剪？**
- 如果$r_t(\theta)$太大，说明新策略和旧策略差别很大
- 裁剪可以防止策略更新过激，保证训练稳定
- min操作确保我们总是取保守的更新方向

**价值函数损失**：
$$
L^{VF}(\theta) = \mathbb{E}_t \left[ (V_\theta(s_t) - V_t^{target})^2 \right]
$$

**总损失**：
$$
L^{PPO} = L^{CLIP} - c_1 L^{VF} + c_2 S[\pi_\theta](s_t)
$$

其中$S[\pi_\theta]$是熵正则项，鼓励探索。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class PPO:
    def __init__(self, actor, critic, lr=3e-4, eps_clip=0.2, vf_coef=0.5, ent_coef=0.01):
        self.actor = actor
        self.critic = critic
        self.eps_clip = eps_clip
        self.vf_coef = vf_coef
        self.ent_coef = ent_coef
        
        self.actor_optimizer = torch.optim.Adam(actor.parameters(), lr=lr)
        self.critic_optimizer = torch.optim.Adam(critic.parameters(), lr=lr)
        
    def compute_advantages(self, rewards, values, dones, gamma=0.99, gae_lambda=0.95):
        """计算GAE优势函数"""
        batch_size = len(rewards)
        advantages = torch.zeros(batch_size)
        gae = 0
        
        for t in reversed(range(batch_size)):
            if t == batch_size - 1:
                next_value = 0
                next_non_terminal = 1 - dones[t]
            else:
                next_value = values[t + 1]
                next_non_terminal = 1 - dones[t + 1]
                
            delta = rewards[t] + gamma * next_value * next_non_terminal - values[t]
            gae = delta + gamma * gae_lambda * next_non_terminal * gae
            advantages[t] = gae
            
        return advantages
    
    def update(self, states, actions, old_log_probs, rewards, dones, num_epochs=4):
        """PPO更新"""
        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.long)
        old_log_probs = torch.tensor(old_log_probs, dtype=torch.float32)
        
        # 计算价值函数
        values = self.critic(states).squeeze()
        advantages = self.compute_advantages(rewards, values.detach(), dones)
        returns = advantages + values.detach()
        
        for _ in range(num_epochs):
            # 计算新的log概率
            logits = self.actor(states)
            new_log_probs = F.log_softmax(logits, dim=-1).gather(1, actions.unsqueeze(1)).squeeze()
            
            # 计算重要性采样比率
            ratio = torch.exp(new_log_probs - old_log_probs)
            
            # PPO-Clip损失
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            
            # 熵正则项
            entropy = -(F.softmax(logits, dim=-1) * F.log_softmax(logits, dim=-1)).sum(dim=-1).mean()
            
            # 价值函数损失
            values_pred = self.critic(states).squeeze()
            critic_loss = F.mse_loss(values_pred, returns)
            
            # 总损失
            total_loss = actor_loss - self.ent_coef * entropy + self.vf_coef * critic_loss
            
            # 更新
            self.actor_optimizer.zero_grad()
            self.critic_optimizer.zero_grad()
            total_loss.backward()
            self.actor_optimizer.step()
            self.critic_optimizer.step()
            
        return total_loss.item()
```

### 推荐论文
1. Schulman et al., "Proximal Policy Optimization Algorithms", arXiv 2017
2. Ouyang et al., "Training language models to follow instructions with human feedback", NeurIPS 2022
3. Stiennon et al., "Learning to summarize from human feedback", NeurIPS 2020

---

## DPO（直接偏好优化）

### 这玩意儿到底是啥？
DPO是PPO的替代方案！它绕过强化学习，直接用偏好数据来优化策略。核心思想是：好的回答应该比坏的回答有更高的概率。

### 核心公式推导
**Bradley-Terry偏好模型**：
假设人类偏好$y_w \succ y_l$（$y_w$比$y_l$好），那么：
$$
P(y_w \succ y_l | x) = \frac{\exp(r(x, y_w))}{\exp(r(x, y_w)) + \exp(r(x, y_l))}
$$

**DPO的目标函数**：
$$
\mathcal{L}_{DPO} = -\mathbb{E}_{(x,y_w,y_l) \sim \mathcal{D}} \left[ \log \sigma\left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} \right) \right]
$$

其中：
- $\pi_\theta$ 是要优化的策略
- $\pi_{ref}$ 是参考策略（通常是SFT后的模型）
- $\beta$ 是温度参数，控制优化强度
- $\sigma$ 是sigmoid函数

**为什么有效？**
- 避免了PPO的复杂实现和不稳定训练
- 直接优化偏好，不需要奖励模型
- 训练更稳定，效果相当甚至更好

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class DPO:
    def __init__(self, model, ref_model, beta=0.1):
        self.model = model
        self.ref_model = ref_model
        self.beta = beta
        
        # 冻结参考模型
        for param in self.ref_model.parameters():
            param.requires_grad = False
            
    def compute_log_probs(self, model, input_ids, attention_mask, labels):
        """计算序列的对数概率"""
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        logits = outputs.logits[:, :-1, :]  # 移除最后一个token
        labels = labels[:, 1:]  # 移除第一个token
        
        # 计算对数概率
        log_probs = F.log_softmax(logits, dim=-1)
        log_probs = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)
        
        # 应用mask
        mask = (labels != -100).float()
        log_probs = (log_probs * mask).sum(dim=-1)
        
        return log_probs
    
    def loss(self, input_ids, attention_mask, chosen_ids, rejected_ids):
        """DPO损失计算"""
        # 计算chosen的对数概率
        chosen_log_probs = self.compute_log_probs(
            self.model, input_ids, attention_mask, chosen_ids
        )
        chosen_ref_log_probs = self.compute_log_probs(
            self.ref_model, input_ids, attention_mask, chosen_ids
        )
        
        # 计算rejected的对数概率
        rejected_log_probs = self.compute_log_probs(
            self.model, input_ids, attention_mask, rejected_ids
        )
        rejected_ref_log_probs = self.compute_log_probs(
            self.ref_model, input_ids, attention_mask, rejected_ids
        )
        
        # 计算偏好分数
        chosen_rewards = self.beta * (chosen_log_probs - chosen_ref_log_probs)
        rejected_rewards = self.beta * (rejected_log_probs - rejected_ref_log_probs)
        
        # DPO损失
        loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
        
        return loss

# 使用示例
def train_dpo(model, ref_model, dataloader, beta=0.1, lr=1e-5):
    dpo_trainer = DPO(model, ref_model, beta=beta)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    model.train()
    for batch in dataloader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        chosen_ids = batch['chosen_ids']
        rejected_ids = batch['rejected_ids']
        
        loss = dpo_trainer.loss(input_ids, attention_mask, chosen_ids, rejected_ids)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    return loss.item()
```

### 推荐论文
1. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023
2. Azar et al., "Relative Entropy Regularized Policy Iteration", arXiv 2019
3. Xu et al., "Preference Ranking Optimization for Human Alignment", ICLR 2024

---

## ORPO（ Odds Ratio Preference Optimization）

### 这玩意儿到底是啥？
ORPO是DPO的改进版！它不仅考虑偏好，还考虑生成概率的绝对值。核心思想是：好的回答不仅要比坏的回答概率高，还要本身就有很高的生成概率。

### 核心公式推导
**ORPO的目标函数**：
$$
\mathcal{L}_{ORPO} = -\mathbb{E}_{(x,y_w,y_l) \sim \mathcal{D}} \left[ \log \sigma\left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_\theta(y_l|x)} \cdot \frac{1 - \pi_\theta(y_l|x)}{1 - \pi_\theta(y_w|x)} \right) \right]
$$

或者等价地：
$$
\mathcal{L}_{ORPO} = \mathcal{L}_{NLL} - \lambda \cdot \mathbb{E} \left[ \log \left( 1 + \frac{\pi_\theta(y_w|x)}{\pi_\theta(y_l|x)} \cdot \frac{1 - \pi_\theta(y_l|x)}{1 - \pi_\theta(y_w|x)} \right) \right]
$$

其中$\mathcal{L}_{NLL}$是负对数似然损失。

**Odds Ratio的意义**：
- $\frac{\pi_\theta(y|x)}{1 - \pi_\theta(y|x)}$ 是生成概率的odds（胜率）
- ORPO最大化好回答和坏回答的odds ratio
- 这样既保证相对偏好，又保证绝对生成质量

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class ORPO:
    def __init__(self, model, lambda_or=0.1):
        self.model = model
        self.lambda_or = lambda_or
        
    def compute_sequence_prob(self, model, input_ids, attention_mask, labels):
        """计算序列的生成概率"""
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        logits = outputs.logits[:, :-1, :]
        labels = labels[:, 1:]
        
        # 计算概率
        probs = F.softmax(logits, dim=-1)
        token_probs = torch.gather(probs, -1, labels.unsqueeze(-1)).squeeze(-1)
        
        # 序列概率（所有token概率的乘积）
        mask = (labels != -100).float()
        seq_probs = torch.prod(token_probs * mask + (1 - mask), dim=-1)
        
        return seq_probs
    
    def loss(self, input_ids, attention_mask, chosen_ids, rejected_ids):
        """ORPO损失计算"""
        # 计算序列概率
        chosen_probs = self.compute_sequence_prob(
            self.model, input_ids, attention_mask, chosen_ids
        )
        rejected_probs = self.compute_sequence_prob(
            self.model, input_ids, attention_mask, rejected_ids
        )
        
        # 计算odds ratio
        chosen_odds = chosen_probs / (1 - chosen_probs + 1e-8)
        rejected_odds = rejected_probs / (1 - rejected_probs + 1e-8)
        odds_ratio = chosen_odds / (rejected_odds + 1e-8)
        
        # ORPO损失
        orpo_loss = -torch.log(1 + odds_ratio).mean()
        
        # NLL损失（可选）
        nll_loss = F.cross_entropy(
            self.model(input_ids=input_ids, attention_mask=attention_mask).logits.view(-1, self.model.config.vocab_size),
            chosen_ids.view(-1),
            ignore_index=-100
        )
        
        total_loss = nll_loss + self.lambda_or * orpo_loss
        return total_loss

# 使用示例
def train_orpo(model, dataloader, lambda_or=0.1, lr=1e-5):
    orpo_trainer = ORPO(model, lambda_or=lambda_or)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    model.train()
    for batch in dataloader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        chosen_ids = batch['chosen_ids']
        rejected_ids = batch['rejected_ids']
        
        loss = orpo_trainer.loss(input_ids, attention_mask, chosen_ids, rejected_ids)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    return loss.item()
```

### 推荐论文
1. Hong et al., "ORPO: Monolithic Preference Optimization without Reference Model", arXiv 2024
2. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023
3. Azar et al., "Relative Entropy Regularized Policy Iteration", arXiv 2019

---

## SimPO（Simple Preference Optimization）

### 这玩意儿到底是啥？
SimPO进一步简化了偏好优化！它直接用序列长度归一化的对数概率作为奖励信号，完全不需要参考模型。

### 核心公式推导
**长度归一化的对数概率**：
$$
r_\theta(x, y) = \frac{1}{|y|^\gamma} \log \pi_\theta(y|x)
$$

其中$\gamma$是长度归一化系数（通常0.5-1.0）。

**SimPO的目标函数**：
$$
\mathcal{L}_{SimPO} = -\mathbb{E}_{(x,y_w,y_l) \sim \mathcal{D}} \left[ \log \sigma\left( \beta (r_\theta(x, y_w) - r_\theta(x, y_l) - \mu) \right) \right]
$$

其中$\mu$是margin参数，确保好回答比坏回答至少好$\mu$。

**为什么有效？**
- 完全不需要参考模型，节省显存和计算
- 长度归一化解决了长序列概率偏小的问题
- margin机制提供更强的优化信号

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SimPO:
    def __init__(self, model, beta=2.0, gamma=0.5, mu=0.5):
        self.model = model
        self.beta = beta
        self.gamma = gamma
        self.mu = mu
        
    def compute_length_normalized_logprob(self, model, input_ids, attention_mask, labels):
        """计算长度归一化的对数概率"""
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        logits = outputs.logits[:, :-1, :]
        labels = labels[:, 1:]
        
        # 计算对数概率
        log_probs = F.log_softmax(logits, dim=-1)
        token_log_probs = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)
        
        # 应用mask并求和
        mask = (labels != -100).float()
        sequence_log_probs = (token_log_probs * mask).sum(dim=-1)
        sequence_lengths = mask.sum(dim=-1)
        
        # 长度归一化
        normalized_log_probs = sequence_log_probs / (sequence_lengths ** self.gamma + 1e-8)
        
        return normalized_log_probs
    
    def loss(self, input_ids, attention_mask, chosen_ids, rejected_ids):
        """SimPO损失计算"""
        # 计算长度归一化的对数概率
        chosen_log_probs = self.compute_length_normalized_logprob(
            self.model, input_ids, attention_mask, chosen_ids
        )
        rejected_log_probs = self.compute_length_normalized_logprob(
            self.model, input_ids, attention_mask, rejected_ids
        )
        
        # 计算偏好差异
        preference_diff = chosen_log_probs - rejected_log_probs - self.mu
        
        # SimPO损失
        loss = -F.logsigmoid(self.beta * preference_diff).mean()
        
        return loss

# 使用示例
def train_simpo(model, dataloader, beta=2.0, gamma=0.5, mu=0.5, lr=1e-5):
    simpo_trainer = SimPO(model, beta=beta, gamma=gamma, mu=mu)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    model.train()
    for batch in dataloader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        chosen_ids = batch['chosen_ids']
        rejected_ids = batch['rejected_ids']
        
        loss = simpo_trainer.loss(input_ids, attention_mask, chosen_ids, rejected_ids)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    return loss.item()
```

### 推荐论文
1. Guo et al., "SimPO: Simple Preference Optimization with a Reference-Free Margin", arXiv 2024
2. Hong et al., "ORPO: Monolithic Preference Optimization without Reference Model", arXiv 2024
3. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023

---

## IPO（Identity Preference Optimization）

### 这玩意儿到底是啥？
IPO是DPO的变体，用二次损失替代sigmoid损失！核心思想是：偏好差异应该接近某个目标值，而不是无限大。

### 核心公式推导
**IPO的目标函数**：
$$
\mathcal{L}_{IPO} = \mathbb{E}_{(x,y_w,y_l) \sim \mathcal{D}} \left[ \left( \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} - \frac{1}{2\beta} \right)^2 \right]
$$

**与DPO的区别**：
- DPO：$\log \sigma(\beta \cdot \text{diff})$，鼓励diff越大越好
- IPO：$(\text{diff} - \frac{1}{2\beta})^2$，鼓励diff接近$\frac{1}{2\beta}$

**为什么用二次损失？**
- 避免过度优化，防止模型过于自信
- 训练更稳定，对超参数不敏感
- 在某些任务上表现更好

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class IPO:
    def __init__(self, model, ref_model, beta=0.1):
        self.model = model
        self.ref_model = ref_model
        self.beta = beta
        
        # 冻结参考模型
        for param in self.ref_model.parameters():
            param.requires_grad = False
            
    def compute_log_probs(self, model, input_ids, attention_mask, labels):
        """计算序列的对数概率"""
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        logits = outputs.logits[:, :-1, :]
        labels = labels[:, 1:]
        
        log_probs = F.log_softmax(logits, dim=-1)
        log_probs = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)
        
        mask = (labels != -100).float()
        log_probs = (log_probs * mask).sum(dim=-1)
        
        return log_probs
    
    def loss(self, input_ids, attention_mask, chosen_ids, rejected_ids):
        """IPO损失计算"""
        # 计算对数概率
        chosen_log_probs = self.compute_log_probs(
            self.model, input_ids, attention_mask, chosen_ids
        )
        chosen_ref_log_probs = self.compute_log_probs(
            self.ref_model, input_ids, attention_mask, chosen_ids
        )
        
        rejected_log_probs = self.compute_log_probs(
            self.model, input_ids, attention_mask, rejected_ids
        )
        rejected_ref_log_probs = self.compute_log_probs(
            self.ref_model, input_ids, attention_mask, rejected_ids
        )
        
        # 计算偏好差异
        diff = (chosen_log_probs - chosen_ref_log_probs) - (rejected_log_probs - rejected_ref_log_probs)
        target = 1.0 / (2 * self.beta)
        
        # IPO损失（二次损失）
        loss = F.mse_loss(diff, torch.full_like(diff, target))
        
        return loss

# 使用示例
def train_ipo(model, ref_model, dataloader, beta=0.1, lr=1e-5):
    ipo_trainer = IPO(model, ref_model, beta=beta)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    model.train()
    for batch in dataloader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        chosen_ids = batch['chosen_ids']
        rejected_ids = batch['rejected_ids']
        
        loss = ipo_trainer.loss(input_ids, attention_mask, chosen_ids, rejected_ids)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    return loss.item()
```

### 推荐论文
1. Azar et al., "General Theoretical Guarantees for Imitation Learning Algorithms with Preference Feedback", ICLR 2024
2. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023
3. Guo et al., "SimPO: Simple Preference Optimization with a Reference-Free Margin", arXiv 2024

---
> RLHF对齐是个热门话题！PPO是经典但复杂，DPO/ORPO/SimPO这些新方法更简单高效。选择哪种方法取决于你的需求：要稳定就用DPO，要简单就用SimPO，要理论保证就用IPO。记住：对齐不是万能的，但合理的对齐策略能让你的模型更安全、更有用！