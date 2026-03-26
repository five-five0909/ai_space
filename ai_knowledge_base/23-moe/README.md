# 23. MoE（混合专家）

> 师弟师妹们好！MoE（Mixture of Experts）就是让大模型变成"专家团队"，不同输入由不同专家处理。今天咱们用大白话+公式+代码，彻底搞懂各种MoE方法！

---

## Sparse MoE（稀疏混合专家）

### 这玩意儿到底是啥？
稀疏MoE就是每个输入只激活少数几个专家（比如2个），而不是所有专家。这样既能享受大模型容量，又不会增加太多计算开销。

### 核心公式推导
**路由机制**：
$$
p_i = \text{softmax}(W_r x)_i
$$

**Top-k选择**：
$$
\text{selected\_experts} = \text{TopK}(p, k)
$$

**输出计算**：
$$
y = \sum_{i \in \text{selected\_experts}} p_i \cdot E_i(x)
$$

其中：
- $x$ 是输入
- $W_r$ 是路由权重
- $E_i$ 是第i个专家网络
- $k$ 是激活的专家数量（通常k=2）

**为什么稀疏？**
- 总专家数可能成百上千
- 但每个输入只用2个专家
- 计算复杂度从$O(N)$降到$O(k)$
- 内存占用大幅减少

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SparseMoELayer(nn.Module):
    def __init__(self, d_model, num_experts=8, top_k=2, expert_hidden_ratio=4):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        self.expert_hidden_dim = d_model * expert_hidden_ratio
        
        # 路由网络
        self.router = nn.Linear(d_model, num_experts)
        
        # 专家网络（共享参数版本）
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, self.expert_hidden_dim),
                nn.GELU(),
                nn.Linear(self.expert_hidden_dim, d_model)
            ) for _ in range(num_experts)
        ])
        
    def forward(self, x):
        batch_size, seq_len, d_model = x.shape
        x_flat = x.view(-1, d_model)  # [batch*seq, d_model]
        
        # 路由：计算每个token选择每个专家的概率
        router_logits = self.router(x_flat)  # [batch*seq, num_experts]
        router_probs = F.softmax(router_logits, dim=-1)
        
        # Top-k选择
        top_k_probs, top_k_indices = torch.topk(router_probs, self.top_k, dim=-1)
        top_k_probs = top_k_probs / top_k_probs.sum(dim=-1, keepdim=True)  # 重新归一化
        
        # 初始化输出
        output = torch.zeros_like(x_flat)
        
        # 为每个专家收集需要处理的token
        for expert_idx in range(self.num_experts):
            # 找到选择这个专家的token
            expert_mask = (top_k_indices == expert_idx).any(dim=-1)  # [batch*seq]
            if not expert_mask.any():
                continue
                
            # 获取这些token
            expert_inputs = x_flat[expert_mask]
            
            # 找到在top-k中的位置（用于获取对应的概率）
            expert_positions = (top_k_indices[expert_mask] == expert_idx).nonzero(as_tuple=True)[1]
            expert_weights = top_k_probs[expert_mask].gather(1, expert_positions.unsqueeze(1)).squeeze(1)
            
            # 专家前向传播
            expert_output = self.experts[expert_idx](expert_inputs)
            
            # 加权并累加到输出
            weighted_output = expert_output * expert_weights.unsqueeze(1)
            output[expert_mask] += weighted_output
            
        return output.view(batch_size, seq_len, d_model)

# 使用示例
moe_layer = SparseMoELayer(d_model=512, num_experts=8, top_k=2)
x = torch.randn(32, 128, 512)  # batch=32, seq_len=128, d_model=512
output = moe_layer(x)
print(f"Output shape: {output.shape}")

# 检查路由分布
router_logits = moe_layer.router(x.view(-1, 512))
router_probs = F.softmax(router_logits, dim=-1)
expert_usage = router_probs.mean(dim=0)
print(f"Expert usage: {expert_usage}")
```

### 推荐论文
1. Shazeer et al., "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer", ICLR 2017
2. Fedus et al., "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", JMLR 2022
3. Artetxe et al., "LLaMA-MoE: Large Language Model with Mixture-of-Experts", arXiv 2024

---

## Switch Transformer

### 这玩意儿到底是啥？
Switch Transformer是MoE的简化版！它只选择一个专家（top-1），而不是多个专家。虽然简单，但效果很好，而且实现更高效。

### 核心公式推导
**开关路由**：
$$
\text{expert\_idx} = \arg\max_i (W_r x)_i
$$

**负载均衡损失**：
$$
\mathcal{L}_{\text{balance}} = N \cdot \sum_{i=1}^N f_i P_i
$$

其中：
- $f_i$ 是专家i的使用频率
- $P_i$ 是路由到专家i的概率
- $N$ 是专家总数

**Z-loss**（辅助损失）：
$$
\mathcal{L}_Z = (\log \sum_i e^{z_i})^2
$$

其中$z_i$是路由logits，用于防止logits爆炸。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SwitchTransformerLayer(nn.Module):
    def __init__(self, d_model, num_experts=8, capacity_factor=1.25):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.capacity_factor = capacity_factor
        
        # 路由网络
        self.router = nn.Linear(d_model, num_experts)
        
        # 专家网络
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_model * 4),
                nn.GELU(),
                nn.Linear(d_model * 4, d_model)
            ) for _ in range(num_experts)
        ])
        
        self.layer_norm = nn.LayerNorm(d_model)
        
    def compute_load_balancing_loss(self, router_probs, expert_indices):
        """计算负载均衡损失"""
        # 专家使用频率
        expert_mask = F.one_hot(expert_indices, num_classes=self.num_experts).float()
        expert_frequency = expert_mask.mean(dim=0)  # [num_experts]
        
        # 路由概率均值
        router_prob_mean = router_probs.mean(dim=0)  # [num_experts]
        
        # 负载均衡损失
        load_balance_loss = (expert_frequency * router_prob_mean).sum() * self.num_experts
        return load_balance_loss
        
    def forward(self, x, compute_aux_loss=True):
        batch_size, seq_len, d_model = x.shape
        x_flat = x.view(-1, d_model)
        num_tokens = x_flat.size(0)
        
        # 路由
        router_logits = self.router(x_flat)  # [num_tokens, num_experts]
        router_probs = F.softmax(router_logits, dim=-1)
        
        # 选择专家（top-1）
        expert_indices = torch.argmax(router_logits, dim=-1)  # [num_tokens]
        
        # 计算专家容量
        expert_capacity = int(self.capacity_factor * num_tokens / self.num_experts)
        
        # 为每个专家分配token（考虑容量限制）
        output = torch.zeros_like(x_flat)
        aux_loss = 0
        
        for expert_idx in range(self.num_experts):
            # 找到分配给这个专家的token
            expert_mask = (expert_indices == expert_idx)
            expert_tokens = x_flat[expert_mask]
            
            if expert_tokens.size(0) == 0:
                continue
                
            # 应用容量限制
            if expert_tokens.size(0) > expert_capacity:
                # 只取前expert_capacity个token
                expert_tokens = expert_tokens[:expert_capacity]
                expert_mask_nonzero = expert_mask.nonzero().squeeze()
                if expert_mask_nonzero.dim() == 0:
                    expert_mask_nonzero = expert_mask_nonzero.unsqueeze(0)
                expert_mask_nonzero = expert_mask_nonzero[:expert_capacity]
                expert_mask = torch.zeros_like(expert_mask)
                expert_mask[expert_mask_nonzero] = True
                
            # 专家前向传播
            expert_output = self.experts[expert_idx](expert_tokens)
            
            # 放回输出
            output[expert_mask] = expert_output
            
        # 计算辅助损失
        if compute_aux_loss:
            aux_loss = self.compute_load_balancing_loss(router_probs, expert_indices)
            z_loss = (torch.logsumexp(router_logits, dim=-1) ** 2).mean()
            total_aux_loss = aux_loss + 0.001 * z_loss
        else:
            total_aux_loss = 0
            
        output = output.view(batch_size, seq_len, d_model)
        return self.layer_norm(x + output), total_aux_loss

# 使用示例
switch_layer = SwitchTransformerLayer(d_model=512, num_experts=8)
x = torch.randn(32, 128, 512)

output, aux_loss = switch_layer(x)
print(f"Output shape: {output.shape}")
print(f"Auxiliary loss: {aux_loss:.6f}")

# 检查专家负载
router_logits = switch_layer.router(x.view(-1, 512))
expert_indices = torch.argmax(router_logits, dim=-1)
unique, counts = torch.unique(expert_indices, return_counts=True)
print(f"Expert loads: {counts.float() / counts.sum():.4f}")
```

### 推荐论文
1. Fedus et al., "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", JMLR 2022
2. Shazeer et al., "GLaM: Efficient Scaling of Language Models with Mixture-of-Experts", ICML 2022
3. Du et al., "GLM-130B: An Open Bilingual Pre-trained Model", ICLR 2023

---

## GShard MoE

### 这玩意儿到底是啥？
GShard是Google提出的MoE架构，专门针对大规模分布式训练优化。它把专家分布在不同的设备上，通过高效的通信机制实现可扩展性。

### 核心公式推导
**分片路由**：
$$
\text{device\_assignment}(expert_i) = i \mod D
$$

其中$D$是设备数量。

**分组Top-k**：
- 将专家分成$G$组
- 在每组内做Top-k选择
- 确保负载均衡和通信效率

**All-to-All通信**：
- Token被发送到对应的专家设备
- 专家处理完后，结果被发送回原设备
- 使用高效的All-to-All集体通信

**内存优化**：
- 梯度检查点
- 激活值卸载
- 专家参数分片

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.distributed as dist

class GShardMoELayer(nn.Module):
    def __init__(self, d_model, num_experts=8, top_k=2, world_size=None):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        self.world_size = world_size or dist.get_world_size()
        
        # 确保专家数能被world_size整除
        assert num_experts % self.world_size == 0
        self.experts_per_device = num_experts // self.world_size
        
        # 路由网络（每个设备都有完整的路由）
        self.router = nn.Linear(d_model, num_experts)
        
        # 本地专家（只存储分配给当前设备的专家）
        self.local_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_model * 4),
                nn.GELU(),
                nn.Linear(d_model * 4, d_model)
            ) for _ in range(self.experts_per_device)
        ])
        
        # 本地专家的全局ID范围
        self.rank = dist.get_rank()
        self.local_expert_start = self.rank * self.experts_per_device
        self.local_expert_end = (self.rank + 1) * self.experts_per_device
        
    def forward(self, x):
        batch_size, seq_len, d_model = x.shape
        x_flat = x.view(-1, d_model)
        num_tokens = x_flat.size(0)
        
        # 路由（所有设备都计算完整的路由）
        router_logits = self.router(x_flat)
        router_probs = F.softmax(router_logits, dim=-1)
        
        # Top-k选择
        top_k_probs, top_k_indices = torch.topk(router_probs, self.top_k, dim=-1)
        top_k_probs = top_k_probs / top_k_probs.sum(dim=-1, keepdim=True)
        
        # 确定哪些token需要发送到本地设备
        local_expert_mask = (top_k_indices >= self.local_expert_start) & \
                           (top_k_indices < self.local_expert_end)
        local_token_mask = local_expert_mask.any(dim=-1)
        
        if not local_token_mask.any():
            # 没有token需要本地处理
            output = torch.zeros_like(x_flat)
        else:
            # 收集需要本地处理的token
            local_tokens = x_flat[local_token_mask]
            
            # 确定每个token对应哪个本地专家
            local_expert_indices = top_k_indices[local_token_mask]
            local_expert_relative = local_expert_indices - self.local_expert_start
            
            # 处理每个本地专家
            local_output = torch.zeros_like(local_tokens)
            for expert_rel_idx in range(self.experts_per_device):
                expert_global_idx = self.local_expert_start + expert_rel_idx
                expert_token_mask = (local_expert_indices == expert_global_idx).any(dim=-1)
                
                if not expert_token_mask.any():
                    continue
                    
                expert_tokens = local_tokens[expert_token_mask]
                
                # 找到在top-k中的位置以获取权重
                expert_positions = (local_expert_indices[expert_token_mask] == expert_global_idx).nonzero(as_tuple=True)[1]
                expert_weights = top_k_probs[local_token_mask][expert_token_mask].gather(1, expert_positions.unsqueeze(1)).squeeze(1)
                
                # 专家前向传播
                expert_output = self.local_experts[expert_rel_idx](expert_tokens)
                local_output[expert_token_mask] += expert_output * expert_weights.unsqueeze(1)
                
            # 放回输出
            output = torch.zeros_like(x_flat)
            output[local_token_mask] = local_output
            
        # All-to-All通信：收集所有设备的输出
        # 简化版本：假设我们只在一个设备上运行
        # 实际实现需要复杂的分布式通信
        
        return output.view(batch_size, seq_len, d_model)

# 分布式训练示例（简化）
def setup_distributed():
    """设置分布式环境"""
    dist.init_process_group("nccl")
    torch.cuda.set_device(dist.get_rank())

def train_gshard_moe():
    """训练GShard MoE模型"""
    if dist.is_initialized():
        model = GShardMoELayer(d_model=512, num_experts=8)
        model = model.cuda()
        
        x = torch.randn(32, 128, 512).cuda()
        output = model(x)
        print(f"Rank {dist.get_rank()}, Output shape: {output.shape}")
    else:
        print("Distributed training not initialized")

# 注意：实际的GShard实现需要复杂的分布式通信原语
# 这里只是概念演示
```

### 推荐论文
1. Lepikhin et al., "GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding", ICLR 2021
2. Xu et al., "GLaM: Efficient Scaling of Language Models with Mixture-of-Experts", ICML 2022
3. Rajbhandari et al., "DeepSpeed-MoE: Advancing Mixture-of-Experts Inference and Training to Power Next-Generation AI Scale", ICML 2022

---

## DeepSpeed MoE

### 这玩意儿到底是啥？
DeepSpeed MoE是Microsoft开发的高效MoE实现，支持超大规模模型训练和推理。它结合了ZeRO、MoE和各种优化技术。

### 核心特点
**专家并行**：
- 专家分布在不同GPU上
- Token路由到对应专家
- 高效的通信优化

**内存优化**：
- ZeRO分片优化器状态
- 激活值检查点
- 专家参数卸载

**负载均衡**：
- 动态路由调整
- 容量因子控制
- 辅助损失函数

**推理优化**：
- 专家批处理
- KV缓存共享
- 量化支持

### PyTorch代码示例
```python
# DeepSpeed MoE配置示例
ds_config = {
    "train_batch_size": 32,
    "gradient_accumulation_steps": 1,
    "optimizer": {
        "type": "Adam",
        "params": {
            "lr": 0.001,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        }
    },
    "fp16": {
        "enabled": True
    },
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu"
        }
    },
    "moe": {
        "expert_parallel_size": 2,
        "num_experts": 8,
        "top_k": 2,
        "capacity_factor": 1.5,
        "use_residual": False
    }
}

# 使用DeepSpeed MoE
import deepspeed
from deepspeed.moe.layer import MoE

class DeepSpeedMoEModel(nn.Module):
    def __init__(self, hidden_size=512, num_experts=8, top_k=2):
        super().__init__()
        self.moe_layer = MoE(
            hidden_size=hidden_size,
            expert=nn.Sequential(
                nn.Linear(hidden_size, hidden_size * 4),
                nn.GELU(),
                nn.Linear(hidden_size * 4, hidden_size)
            ),
            num_experts=num_experts,
            k=top_k,
            capacity_factor=1.5
        )
        self.layer_norm = nn.LayerNorm(hidden_size)
        
    def forward(self, x):
        moe_output, aux_loss = self.moe_layer(x)
        return self.layer_norm(x + moe_output), aux_loss

# 初始化DeepSpeed引擎
def initialize_deepspeed_moe():
    model = DeepSpeedMoEModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    model_engine, optimizer, _, _ = deepspeed.initialize(
        model=model,
        optimizer=optimizer,
        config=ds_config
    )
    
    return model_engine, optimizer

# 训练循环
def train_deepspeed_moe():
    model_engine, optimizer = initialize_deepspeed_moe()
    
    for epoch in range(100):
        for batch in dataloader:
            inputs = batch['input'].to(model_engine.device)
            labels = batch['label'].to(model_engine.device)
            
            outputs, aux_loss = model_engine(inputs)
            loss = F.cross_entropy(outputs.view(-1, vocab_size), labels.view(-1))
            total_loss = loss + 0.01 * aux_loss  # 添加辅助损失
            
            model_engine.backward(total_loss)
            model_engine.step()

# 注意：这需要DeepSpeed环境和多GPU设置
```

### 推荐论文
1. Rajbhandari et al., "DeepSpeed-MoE: Advancing Mixture-of-Experts Inference and Training to Power Next-Generation AI Scale", ICML 2022
2. Aminabadi et al., "DeepSpeed-Inference: Enabling Efficient Inference of Transformer Models at Unprecedented Scale", MLSys 2022
3. Rasley et al., "DeepSpeed: System Optimizations Enable Training Deep Learning Models with Over 100 Billion Parameters", KDD 2020

---
> MoE是大模型扩展的关键技术！稀疏MoE平衡容量和效率，Switch Transformer简单高效，GShard支持超大规模分布式，DeepSpeed MoE提供完整解决方案。记住：好的MoE设计能让模型更大更强，同时保持推理效率！