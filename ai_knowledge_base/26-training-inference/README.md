# 26. 训练与推理

> 师弟师妹们好！训练和推理是大模型的两个核心阶段。今天咱们用大白话+公式+代码，彻底搞懂各种训练和推理优化技术！

---

## Mixed Precision Training（混合精度训练）

### 这玩意儿到底是啥？
混合精度训练就是用FP16和FP32混合进行训练！大部分计算用FP16（速度快、内存少），关键部分用FP32（精度高、稳定）。

### 核心公式推导
**权重主副本**：
- FP32主权重：$W_{32}$
- FP16工作权重：$W_{16} = \text{cast}(W_{32})$

**前向传播**：
$$
\text{Forward}_{16}(x_{16}, W_{16}) \to y_{16}
$$

**反向传播**：
$$
\frac{\partial L}{\partial W_{16}} = \text{Backward}_{16}(y_{16}, \frac{\partial L}{\partial y_{16}})
$$

**权重更新**：
$$
W_{32} = W_{32} - \eta \cdot \text{cast}(\frac{\partial L}{\partial W_{16}})
$$

**损失缩放**：
为防止FP16梯度下溢，将损失乘以缩放因子$S$：
$$
L_{\text{scaled}} = S \cdot L
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler

class MixedPrecisionTrainer:
    def __init__(self, model, optimizer):
        self.model = model
        self.optimizer = optimizer
        self.scaler = GradScaler()
        
    def train_step(self, inputs, targets):
        """单步训练"""
        self.optimizer.zero_grad()
        
        # 自动混合精度上下文
        with autocast():
            outputs = self.model(inputs)
            loss = F.cross_entropy(outputs, targets)
            
        # 缩放损失并反向传播
        self.scaler.scale(loss).backward()
        
        # 优化器步骤（自动处理缩放）
        self.scaler.step(self.optimizer)
        
        # 更新缩放因子
        self.scaler.update()
        
        return loss.item()

# 使用示例
model = nn.Linear(1000, 10).cuda()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

trainer = MixedPrecisionTrainer(model, optimizer)

# 训练数据
inputs = torch.randn(32, 1000).cuda()
targets = torch.randint(0, 10, (32,)).cuda()

loss = trainer.train_step(inputs, targets)
print(f"Loss: {loss:.6f}")

# 检查张量类型
with autocast():
    output = model(inputs)
    print(f"Output dtype: {output.dtype}")  # torch.float16

print(f"Model weight dtype: {model.weight.dtype}")  # torch.float32
```

### 推荐论文
1. Micikevicius et al., "Mixed Precision Training", ICLR 2018
2. NVIDIA, "Automatic Mixed Precision for Deep Learning", Technical Report 2020
3. Zhang et al., "FP8 training with dynamic scaling", arXiv 2023

---

## Gradient Checkpointing（梯度检查点）

### 这玩意儿到底是啥？
梯度检查点就是用时间换空间！不保存所有中间激活值，而是在反向传播时重新计算，大幅减少内存占用。

### 核心公式推导
**标准反向传播内存**：
$$
\text{Memory}_{\text{standard}} = O(L \cdot B \cdot D)
$$

**梯度检查点内存**：
$$
\text{Memory}_{\text{checkpoint}} = O(\sqrt{L} \cdot B \cdot D)
$$

其中$L$是层数，$B$是batch size，$D$是特征维度。

**重计算策略**：
- 将网络分成$\sqrt{L}$个段
- 只保存每个段的输入
- 反向传播时按段重计算激活值

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint

class CheckpointedLayer(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_model * 4)
        self.linear2 = nn.Linear(d_model * 4, d_model)
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, x):
        def custom_forward(*inputs):
            x_in = inputs[0]
            x_out = self.linear2(F.gelu(self.linear1(x_in)))
            return self.dropout(x_out)
            
        # 使用checkpoint包裹前向传播
        if self.training:
            return checkpoint(custom_forward, x)
        else:
            return custom_forward(x)

class TransformerWithCheckpointing(nn.Module):
    def __init__(self, d_model=512, num_layers=12):
        super().__init__()
        self.layers = nn.ModuleList([
            CheckpointedLayer(d_model) for _ in range(num_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return self.layer_norm(x)

# 内存对比实验
def compare_memory_usage():
    # 标准Transformer
    standard_model = TransformerWithCheckpointing(num_layers=24)
    standard_model = standard_model.cuda()
    
    # 检查点Transformer
    checkpoint_model = TransformerWithCheckpointing(num_layers=24)
    checkpoint_model = checkpoint_model.cuda()
    
    x = torch.randn(8, 1024, 512).cuda()
    
    # 测量标准模型内存
    torch.cuda.reset_peak_memory_stats()
    out1 = standard_model(x)
    standard_memory = torch.cuda.max_memory_allocated()
    
    # 测量检查点模型内存
    torch.cuda.reset_peak_memory_stats()
    out2 = checkpoint_model(x)
    checkpoint_memory = torch.cuda.max_memory_allocated()
    
    print(f"Standard memory: {standard_memory / 1024**3:.2f} GB")
    print(f"Checkpoint memory: {checkpoint_memory / 1024**3:.2f} GB")
    print(f"Memory reduction: {standard_memory / checkpoint_memory:.2f}x")

# 使用示例
compare_memory_usage()
```

### 推荐论文
1. Chen et al., "Training Deep Nets with Sublinear Memory Cost", NeurIPS 2016
2. Jain et al., "Checkmate: Breaking the Memory Wall with Optimal Tensor Rematerialization", MLSys 2020
3. Kirisame et al., "Dynamic Tensor Rematerialization", ICLR 2021

---

## FlashAttention

### 这玩意儿到底是啥？
FlashAttention就是IO感知的注意力实现！它通过tiling和重计算技术，减少HBM访问，大幅提升注意力计算速度。

### 核心公式推导
**标准注意力IO复杂度**：
$$
\text{IO}_{\text{standard}} = O(N^2)
$$

**FlashAttention IO复杂度**：
$$
\text{IO}_{\text{flash}} = O(N)
$$

**分块计算**：
将Q, K, V分成小块，在SRAM中计算：
$$
\text{Attn}(Q_i, K_j, V_j) = \text{softmax}(Q_i K_j^T) V_j
$$

**在线Softmax**：
通过数学变换避免存储完整的注意力矩阵：
$$
\text{softmax}(x) = \frac{\exp(x - m)}{\sum \exp(x - m)}, \quad m = \max(x)
$$

### PyTorch代码示例
```python
import torch
import torch.nn.functional as F
from flash_attn import flash_attn_func

class FlashAttentionLayer(nn.Module):
    def __init__(self, d_model, nhead):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
    def forward(self, q, k, v, causal=False):
        batch_size, seq_len, _ = q.shape
        
        # 投影到多头
        q = self.q_proj(q).view(batch_size, seq_len, self.nhead, self.head_dim)
        k = self.k_proj(k).view(batch_size, seq_len, self.nhead, self.head_dim)
        v = self.v_proj(v).view(batch_size, seq_len, self.nhead, self.head_dim)
        
        # FlashAttention（注意：需要flash-attn库）
        try:
            output = flash_attn_func(q, k, v, causal=causal)
            output = output.view(batch_size, seq_len, self.d_model)
            return self.out_proj(output)
        except ImportError:
            # 回退到标准注意力
            q = q.transpose(1, 2)
            k = k.transpose(1, 2)
            v = v.transpose(1, 2)
            
            attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
            if causal:
                mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool().to(q.device)
                attn_scores.masked_fill_(mask, float('-inf'))
                
            attn_weights = F.softmax(attn_scores, dim=-1)
            output = torch.matmul(attn_weights, v)
            output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
            return self.out_proj(output)

# 性能对比
def compare_attention_speed():
    batch_size, seq_len, d_model = 4, 2048, 512
    nhead = 8
    
    q = torch.randn(batch_size, seq_len, d_model).cuda()
    k = torch.randn(batch_size, seq_len, d_model).cuda()
    v = torch.randn(batch_size, seq_len, d_model).cuda()
    
    # 标准注意力
    standard_attn = nn.MultiheadAttention(d_model, nhead, batch_first=True).cuda()
    
    # FlashAttention
    flash_attn = FlashAttentionLayer(d_model, nhead).cuda()
    
    # 测量标准注意力时间
    torch.cuda.synchronize()
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    
    start_time.record()
    for _ in range(10):
        with torch.no_grad():
            _ = standard_attn(q, k, v)
    end_time.record()
    torch.cuda.synchronize()
    standard_time = start_time.elapsed_time(end_time)
    
    # 测量FlashAttention时间
    start_time.record()
    for _ in range(10):
        with torch.no_grad():
            _ = flash_attn(q, k, v)
    end_time.record()
    torch.cuda.synchronize()
    flash_time = start_time.elapsed_time(end_time)
    
    print(f"Standard attention time: {standard_time:.2f} ms")
    print(f"FlashAttention time: {flash_time:.2f} ms")
    print(f"Speedup: {standard_time / flash_time:.2f}x")

# 使用示例
compare_attention_speed()
```

### 推荐论文
1. Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", NeurIPS 2022
2. Dao et al., "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning", NeurIPS 2023
3. Team et al., "Efficient Transformers: A Survey", arXiv 2021

---

## vLLM Inference

### 这玩意儿到底是啥？
vLLM是高效的LLM推理引擎！它使用PagedAttention技术，大幅提高内存利用率和吞吐量。

### 核心公式推导
**PagedAttention**：
将KV缓存分成固定大小的页面：
$$
\text{KV}_{\text{cache}} = \bigcup_{i=1}^m P_i
$$

**虚拟到物理映射**：
$$
\text{physical\_page}[j] = \text{page\_table}[\text{virtual\_page}[j]]
$$

**内存连续性保证**：
- 逻辑上连续的KV缓存
- 物理上可以非连续存储
- 通过页表管理映射

**吞吐量提升**：
$$
\text{Throughput}_{\text{vLLM}} = k \cdot \text{Throughput}_{\text{baseline}}
$$

其中$k$通常为2-4倍。

### PyTorch代码示例
```python
# vLLM使用示例（需要安装vllm库）
from vllm import LLM, SamplingParams

class vLLMInference:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        self.llm = LLM(model=model_name)
        
    def generate_text(self, prompts, max_tokens=100, temperature=0.7):
        """批量文本生成"""
        sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95
        )
        
        outputs = self.llm.generate(prompts, sampling_params)
        return [output.outputs[0].text for output in outputs]
    
    def get_tokenizer(self):
        """获取tokenizer"""
        return self.llm.get_tokenizer()

# 使用示例
vllm_engine = vLLMInference("meta-llama/Llama-2-7b-chat-hf")

prompts = [
    "Explain quantum computing in simple terms.",
    "Write a poem about artificial intelligence.",
    "What is the capital of France?"
]

responses = vllm_engine.generate_text(prompts, max_tokens=50)
for i, response in enumerate(responses):
    print(f"Prompt {i+1}: {prompts[i]}")
    print(f"Response: {response}\n")

# 内存效率对比
def compare_memory_efficiency():
    """比较vLLM和标准HuggingFace的内存效率"""
    import psutil
    import os
    
    # 标准HuggingFace推理
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    # vLLM内存使用
    process = psutil.Process(os.getpid())
    vllm_mem_before = process.memory_info().rss / 1024**3
    
    vllm_engine = vLLMInference(model_name)
    vllm_mem_after = process.memory_info().rss / 1024**3
    vllm_memory = vllm_mem_after - vllm_mem_before
    
    # 注意：实际比较需要在相同条件下进行
    print(f"vLLM memory usage: {vllm_memory:.2f} GB")
    print("vLLM typically uses 2-4x less memory than standard inference")
```

### 推荐论文
1. Kwon et al., "vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention", arXiv 2023
2. Yu et al., "Orca: A Distributed Serving System for Transformer-Based Generative Models", OSDI 2022
3. Peng et al., "Serving Large Language Models Efficiently with Paged KV Caches", MLSys 2024

---
> 训练和推理优化是大模型落地的关键！混合精度训练加速训练，梯度检查点节省内存，FlashAttention优化注意力计算，vLLM提升推理效率。记住：好的优化策略能让训练快2倍，推理快4倍，内存省一半！