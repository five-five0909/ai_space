# 22. KV缓存

> 师弟师妹们好！KV缓存就是让大模型推理时不用重复计算，大幅加速生成速度。今天咱们用大白话+公式+代码，彻底搞懂各种KV缓存技术！

---

## Standard KV Cache（标准KV缓存）

### 这玩意儿到底是啥？
标准KV缓存就是在自回归生成时，把之前计算过的Key和Value缓存起来，避免重复计算。就像做数学题时把中间结果记下来一样。

### 核心公式推导
**自回归生成**：
$$
y_t = \text{Transformer}(x_{1:t})
$$

**KV缓存机制**：
- 第t步：$K_t = K(x_{1:t})$, $V_t = V(x_{1:t})$
- 第t+1步：$K_{t+1} = [K_t, K(x_{t+1})]$, $V_{t+1} = [V_t, V(x_{t+1})]$

**内存复杂度**：
- 无缓存：$O(t^2)$
- 有缓存：$O(t)$

**为什么有效？**
- 避免重复计算历史token的K和V
- 推理速度从$O(n^2)$降到$O(n)$
- 特别适合长序列生成

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class KVCacheAttention(nn.Module):
    def __init__(self, d_model, nhead):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
    def forward(self, x, past_kv=None):
        batch_size, seq_len, _ = x.shape
        
        # 计算当前的Q, K, V
        q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        
        # 处理KV缓存
        if past_kv is not None:
            past_k, past_v = past_kv
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)
            
        # 计算注意力
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = torch.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_weights, v)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.out_proj(output)
        
        # 返回当前KV用于下一次缓存
        return output, (k, v)

class TransformerWithKVCaching(nn.Module):
    def __init__(self, d_model=512, nhead=8, num_layers=6):
        super().__init__()
        self.layers = nn.ModuleList([
            KVCacheAttention(d_model, nhead) for _ in range(num_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, x, past_kvs=None):
        if past_kvs is None:
            past_kvs = [None] * len(self.layers)
            
        new_kvs = []
        for i, layer in enumerate(self.layers):
            x, kv = layer(x, past_kvs[i])
            new_kvs.append(kv)
            
        return self.layer_norm(x), new_kvs

# 使用示例
model = TransformerWithKVCaching()
input_token = torch.randn(1, 1, 512)  # 单个token

# 第一个token
output1, kvs1 = model(input_token)

# 第二个token（使用KV缓存）
next_token = torch.randn(1, 1, 512)
output2, kvs2 = model(next_token, kvs1)

print(f"First output shape: {output1.shape}")
print(f"Second output shape: {output2.shape}")
print(f"KV cache size: {kvs2[0][0].shape}")  # [batch, nhead, seq_len, head_dim]
```

### 推荐论文
1. Vaswani et al., "Attention is All You Need", NeurIPS 2017
2. Shoeybi et al., "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", arXiv 2019
3. Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", NeurIPS 2022

---

## Streaming KV Cache（流式KV缓存）

### 这玩意儿到底是啥？
流式KV缓存就是处理超长序列时，只保留最近的KV对，丢弃远古的历史。就像聊天机器人只记住最近几轮对话一样。

### 核心公式推导
**滑动窗口机制**：
$$
K_t^{\text{cache}} = K(x_{\max(1, t-w+1):t})
$$
$$
V_t^{\text{cache}} = V(x_{\max(1, t-w+1):t})
$$

其中$w$是窗口大小。

**动态窗口调整**：
- 固定窗口：$w = \text{constant}$
- 自适应窗口：$w_t = f(\text{context importance})$
- 分层窗口：不同层用不同窗口大小

**内存优化**：
- 内存占用从$O(n)$降到$O(w)$
- 推理延迟保持恒定

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class StreamingKVCache(nn.Module):
    def __init__(self, d_model, nhead, max_cache_size=2048):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        self.max_cache_size = max_cache_size
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
    def forward(self, x, past_kv=None):
        batch_size, seq_len, _ = x.shape
        
        # 计算当前的Q, K, V
        q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        
        # 处理流式KV缓存
        if past_kv is not None:
            past_k, past_v = past_kv
            
            # 拼接新旧KV
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)
            
            # 如果超过最大缓存大小，截断最旧的部分
            if k.size(2) > self.max_cache_size:
                start_idx = k.size(2) - self.max_cache_size
                k = k[:, :, start_idx:, :]
                v = v[:, :, start_idx:, :]
                
        # 计算注意力
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = torch.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_weights, v)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.out_proj(output)
        
        return output, (k, v)

class StreamingTransformer(nn.Module):
    def __init__(self, d_model=512, nhead=8, num_layers=6, max_cache_size=2048):
        super().__init__()
        self.layers = nn.ModuleList([
            StreamingKVCache(d_model, nhead, max_cache_size) for _ in range(num_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model)
        self.max_cache_size = max_cache_size
        
    def forward(self, x, past_kvs=None):
        if past_kvs is None:
            past_kvs = [None] * len(self.layers)
            
        new_kvs = []
        for i, layer in enumerate(self.layers):
            x, kv = layer(x, past_kvs[i])
            new_kvs.append(kv)
            
        return self.layer_norm(x), new_kvs

# 使用示例
model = StreamingTransformer(max_cache_size=1024)
cache = None

# 模拟长序列生成
for i in range(2000):  # 生成2000个token
    token = torch.randn(1, 1, 512)
    output, cache = model(token, cache)
    
    if i % 500 == 0:
        print(f"Generated token {i}, cache size: {cache[0][0].shape[2]}")
        # cache size should be min(i+1, 1024)
```

### 推荐论文
1. Dai et al., "Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context", ACL 2019
2. Beltagy et al., "Longformer: The Long-Document Transformer", arXiv 2020
3. Zhang et al., "Efficient Streaming Language Models with Attention Sinks", ICLR 2024

---

## Quantized KV Cache（量化KV缓存）

### 这玩意儿到底是啥？
量化KV缓存就是把KV缓存从FP16/F32压缩到INT8/INT4，大幅减少内存占用。就像把高清图片压缩成低清图片一样。

### 核心公式推导
**量化映射**：
$$
K_{\text{int}} = \text{round}\left(\frac{K_{\text{float}}}{s_K} + z_K\right)
$$
$$
V_{\text{int}} = \text{round}\left(\frac{V_{\text{float}}}{s_V} + z_V\right)
$$

**反量化映射**：
$$
K_{\text{float}} = s_K \cdot (K_{\text{int}} - z_K)
$$
$$
V_{\text{float}} = s_V \cdot (V_{\text{int}} - z_V)
$$

**逐通道量化**：
- 每个attention head有自己的scale和zero_point
- $s_K^{(h)} = \frac{\max(|K^{(h)}|)}{127}$ （INT8对称量化）

**内存节省**：
- FP16 → INT8：内存减半
- FP16 → INT4：内存减少75%

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class QuantizedKVCache(nn.Module):
    def __init__(self, d_model, nhead, bits=8):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        self.bits = bits
        self.qmin = -(2**(bits-1))
        self.qmax = 2**(bits-1) - 1
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
    def quantize_tensor(self, x):
        """量化张量"""
        x_min = x.min(dim=-1, keepdim=True)[0]
        x_max = x.max(dim=-1, keepdim=True)[0]
        
        scale = (x_max - x_min) / (self.qmax - self.qmin)
        zero_point = self.qmin - torch.round(x_min / scale)
        zero_point = torch.clamp(zero_point, self.qmin, self.qmax)
        
        x_int = torch.round(x / scale + zero_point)
        x_int = torch.clamp(x_int, self.qmin, self.qmax)
        
        return x_int.to(torch.int8 if self.bits == 8 else torch.int8), scale, zero_point
    
    def dequantize_tensor(self, x_int, scale, zero_point):
        """反量化张量"""
        x_float = scale * (x_int.float() - zero_point)
        return x_float
    
    def forward(self, x, past_kv_quantized=None):
        batch_size, seq_len, _ = x.shape
        
        # 计算当前的Q, K, V
        q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1,  2)
        v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        
        # 处理量化KV缓存
        if past_kv_quantized is not None:
            past_k_int, past_k_scale, past_k_zero, past_v_int, past_v_scale, past_v_zero = past_kv_quantized
            
            # 反量化过去的KV
            past_k = self.dequantize_tensor(past_k_int, past_k_scale, past_k_zero)
            past_v = self.dequantize_tensor(past_v_int, past_v_scale, past_v_zero)
            
            # 拼接
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)
            
        # 量化当前的KV用于缓存
        k_int, k_scale, k_zero = self.quantize_tensor(k)
        v_int, v_scale, v_zero = self.quantize_tensor(v)
        
        # 计算注意力（使用完整的K,V）
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = torch.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_weights, v)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.out_proj(output)
        
        # 返回量化后的KV缓存
        return output, (k_int, k_scale, k_zero, v_int, v_scale, v_zero)

# 使用示例
model = QuantizedKVCache(d_model=512, nhead=8, bits=8)
input_token = torch.randn(1, 1, 512)

# 第一个token
output1, kv_cache1 = model(input_token)
print(f"Quantized KV cache types: {[type(x) for x in kv_cache1]}")

# 第二个token
next_token = torch.randn(1, 1, 512)
output2, kv_cache2 = model(next_token, kv_cache1)

# 内存比较
k_full = torch.randn(1, 8, 1024, 64)  # FP16
k_quant = torch.randint(-128, 127, (1, 8, 1024, 64), dtype=torch.int8)  # INT8

print(f"Full precision memory: {k_full.element_size() * k_full.numel()} bytes")
print(f"Quantized memory: {k_quant.element_size() * k_quant.numel()} bytes")
print(f"Memory reduction: {k_full.element_size() / k_quant.element_size():.1f}x")
```

### 推荐论文
1. Dettmers et al., "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", NeurIPS 2022
2. Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", ICLR 2024
3. Frantar et al., "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", ICLR 2023

---

## Paged KV Cache（分页KV缓存）

### 这玩意儿到底是啥？
分页KV缓存就是把KV缓存分成固定大小的页面，像操作系统管理内存一样，可以动态分配和释放，避免内存碎片。

### 核心公式推导
**分页机制**：
- 页面大小：$p = 16$ 或 $32$ tokens
- KV缓存被分成多个页面：$\{P_1, P_2, ..., P_m\}$
- 每个页面存储固定数量的KV对

**虚拟到物理映射**：
$$
\text{physical\_page}[i] = \text{page\_table}[\text{virtual\_page}[i]]
$$

**内存连续性**：
- 逻辑上连续的KV缓存
- 物理上可以分散存储
- 通过页表管理映射关系

**优势**：
- 减少内存碎片
- 支持动态批处理
- 提高GPU内存利用率

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class PagedKVCache:
    def __init__(self, page_size=16, max_pages=1024, d_model=512, nhead=8):
        self.page_size = page_size
        self.max_pages = max_pages
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        
        # 预分配页面池
        self.k_pages = torch.zeros(max_pages, nhead, page_size, self.head_dim)
        self.v_pages = torch.zeros(max_pages, nhead, page_size, self.head_dim)
        
        # 页面分配状态
        self.free_pages = list(range(max_pages))
        self.allocated_pages = {}
        
        # 页表（虚拟页面 -> 物理页面）
        self.page_table = {}
        
    def allocate_page(self):
        """分配一个新页面"""
        if not self.free_pages:
            raise RuntimeError("No free pages available")
        page_id = self.free_pages.pop()
        return page_id
        
    def free_page(self, page_id):
        """释放页面"""
        self.free_pages.append(page_id)
        
    def append_to_cache(self, k_new, v_new, sequence_id):
        """向缓存中添加新的KV"""
        batch_size, nhead, seq_len, head_dim = k_new.shape
        
        if sequence_id not in self.allocated_pages:
            self.allocated_pages[sequence_id] = []
            
        pages = self.allocated_pages[sequence_id]
        
        # 计算需要多少个新页面
        tokens_per_page = self.page_size
        new_tokens = seq_len
        total_tokens = len(pages) * tokens_per_page + new_tokens
        
        # 分配新页面
        new_pages_needed = (total_tokens + tokens_per_page - 1) // tokens_per_page - len(pages)
        for _ in range(new_pages_needed):
            page_id = self.allocate_page()
            pages.append(page_id)
            
        # 将新KV写入页面
        current_token = len(pages) * tokens_per_page - new_tokens
        for i in range(seq_len):
            page_idx = current_token // tokens_per_page
            token_in_page = current_token % tokens_per_page
            physical_page = pages[page_idx]
            
            self.k_pages[physical_page, :, token_in_page, :] = k_new[0, :, i, :]
            self.v_pages[physical_page, :, token_in_page, :] = v_new[0, :, i, :]
            
            current_token += 1
            
        return pages
        
    def get_kv_for_sequence(self, sequence_id, max_tokens=None):
        """获取序列的完整KV"""
        if sequence_id not in self.allocated_pages:
            return None, None
            
        pages = self.allocated_pages[sequence_id]
        if max_tokens is None:
            max_tokens = len(pages) * self.page_size
            
        actual_tokens = min(max_tokens, len(pages) * self.page_size)
        k_full = torch.zeros(self.nhead, actual_tokens, self.head_dim)
        v_full = torch.zeros(self.nhead, actual_tokens, self.head_dim)
        
        for i in range(actual_tokens):
            page_idx = i // self.page_size
            token_in_page = i % self.page_size
            physical_page = pages[page_idx]
            
            k_full[:, i, :] = self.k_pages[physical_page, :, token_in_page, :]
            v_full[:, i, :] = self.v_pages[physical_page, :, token_in_page, :]
            
        return k_full.unsqueeze(0), v_full.unsqueeze(0)

class PagedAttention(nn.Module):
    def __init__(self, d_model, nhead):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
    def forward(self, x, paged_kv_cache=None, sequence_id=None):
        batch_size, seq_len, _ = x.shape
        
        q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        
        if paged_kv_cache is not None and sequence_id is not None:
            # 从分页缓存中获取KV
            k_full, v_full = paged_kv_cache.get_kv_for_sequence(sequence_id)
            if k_full is not None:
                k = torch.cat([k_full, self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)], dim=2)
                v = torch.cat([v_full, self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)], dim=2)
            else:
                k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
                v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
                
            # 更新分页缓存
            paged_kv_cache.append_to_cache(k[:, :, -seq_len:, :], v[:, :, -seq_len:, :], sequence_id)
        else:
            k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
            v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
            
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = torch.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_weights, v)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.out_proj(output)
        
        return output

# 使用示例
paged_cache = PagedKVCache(page_size=16, max_pages=64, d_model=512, nhead=8)
attention = PagedAttention(d_model=512, nhead=8)

# 模拟多轮生成
sequence_id = 0
for i in range(100):  # 生成100个token
    token = torch.randn(1, 1, 512)
    output = attention(token, paged_cache, sequence_id)
    
    if i % 20 == 0:
        print(f"Generated token {i}, allocated pages: {len(paged_cache.allocated_pages.get(sequence_id, []))}")

# 查看内存使用情况
print(f"Free pages: {len(paged_cache.free_pages)}")
print(f"Used pages: {len(paged_cache.allocated_pages.get(sequence_id, []))}")
```

### 推荐论文
1. Kwon et al., "vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention", arXiv 2023
2. Yu et al., "Orca: A Distributed Serving System for Transformer-Based Generative Models", OSDI 2022
3. Peng et al., "Serving Large Language Models Efficiently with Paged KV Caches", MLSys 2024

---
> KV缓存是大模型推理的核心优化！标准缓存提升基础性能，流式缓存处理长序列，量化缓存节省内存，分页缓存提高利用率。记住：好的KV缓存策略能让推理速度快10倍，内存省一半！