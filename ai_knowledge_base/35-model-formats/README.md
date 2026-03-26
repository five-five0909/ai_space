# 35. 模型格式与量化工具

> 一句话：模型格式决定了模型怎么存、怎么加载；量化工具决定了模型能压缩多小、跑多快。GGUF、safetensors是主流格式，GPTQ、AWQ是主流量化方法。

---

## GGUF/GGML

### 这玩意儿到底是啥？

GGUF（GGML Universal Format）是llama.cpp项目定义的模型格式，专门用于存储量化后的大语言模型。它是GGML格式的继任者，解决了GGML的一些设计问题，现在已成为本地运行大模型的事实标准。

**为什么需要GGUF？**
- HuggingFace的模型通常是FP16或FP32，太大
- GGUF支持各种量化（Q4_0、Q4_K_M、Q5_K_M等）
- 单文件存储，方便分发和加载
- llama.cpp原生支持，无需额外转换

### 量化类型详解

**量化类型命名规则：**
```
Q = Quantized（量化）
数字 = 比特数（4、5、8等）
K = K-quant（K量化，更精细）
M/S = Medium/Small（中等/小型）
_0 = 不使用缩放因子
```

**常见量化类型对比：**

| 类型 | 比特数 | 模型大小（7B） | 精度损失 | 速度 |
|------|--------|----------------|----------|------|
| FP16 | 16 | 14GB | 无 | 基准 |
| Q8_0 | 8 | 7GB | <1% | 快 |
| Q6_K | 6 | 5.5GB | ~1% | 较快 |
| Q5_K_M | 5 | 4.8GB | ~2% | 快 |
| Q4_K_M | 4 | 4.1GB | ~3% | 最快 |
| Q4_0 | 4 | 3.9GB | ~5% | 最快 |
| Q3_K_M | 3 | 3.2GB | ~8% | 快 |
| Q2_K | 2 | 2.6GB | ~15% | 快 |

**K量化的优势：**
```
传统Q4_0：所有层都用相同的4-bit量化
Q4_K_M：
  - 注意力层：使用更精细的量化
  - FFN层：使用标准量化
  - 关键层：使用更高的比特数

结果：相同平均比特数下，K量化精度更高
```

### GGUF文件结构

```
GGUF文件结构：
┌─────────────────────────────┐
│ Header                      │
│  - Magic Number (GGUF)      │
│  - Version                  │
│  - Tensor Count             │
│  - Metadata Count           │
├─────────────────────────────┤
│ Metadata KV Pairs           │
│  - general.name             │
│  - general.architecture     │
│  - llama.context_length     │
│  - llama.embedding_length   │
│  - ...                      │
├─────────────────────────────┤
│ Tensor Info                 │
│  - Name, Dimensions, Type   │
│  - Offset                   │
├─────────────────────────────┤
│ Tensor Data                 │
│  - Quantized Weights        │
└─────────────────────────────┘
```

### 代码示例

```python
# 从HuggingFace下载并转换为GGUF
# 使用llama.cpp的convert脚本

# Step 1: 下载原始模型
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="meta-llama/Llama-2-7b-hf",
    local_dir="./llama-2-7b",
)

# Step 2: 转换为GGUF（命令行）
# python convert.py ./llama-2-7b --outfile llama-2-7b-f16.gguf --outtype f16

# Step 3: 量化（命令行）
# ./quantize llama-2-7b-f16.gguf llama-2-7b-q4_k_m.gguf q4_k_m

# Python读取GGUF文件
import struct
from typing import Dict, Any

def read_gguf_header(filepath: str) -> Dict[str, Any]:
    """读取GGUF文件头"""
    with open(filepath, 'rb') as f:
        # Magic number
        magic = f.read(4)
        if magic != b'GGUF':
            raise ValueError("Not a valid GGUF file")

        # Version
        version = struct.unpack('<I', f.read(4))[0]

        # Tensor count
        tensor_count = struct.unpack('<Q', f.read(8))[0]

        # Metadata count
        metadata_kv_count = struct.unpack('<Q', f.read(8))[0]

        return {
            'version': version,
            'tensor_count': tensor_count,
            'metadata_count': metadata_kv_count,
        }

# 使用llama-cpp-python加载
from llama_cpp import Llama

llm = Llama(
    model_path="llama-2-7b-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=32,  # 0 = CPU only
    verbose=False,
)

response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "你好，介绍一下自己"}],
    max_tokens=256,
)
print(response['choices'][0]['message']['content'])
```

### 推荐论文

1. **Gerganov, 2023** - "llama.cpp: A C++ Implementation of LLaMA" - GGUF格式定义
2. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication" - 量化基础
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization" - GPTQ量化

---

## safetensors

### 这玩意儿到底是啥？

safetensors是HuggingFace推出的安全、快速的模型存储格式。相比于PyTorch的`.pt`/`.bin`格式（基于pickle），safetensors避免了pickle反序列化的安全风险，并且支持零拷贝加载。

**为什么safetensors比pickle安全？**
```
Pickle反序列化漏洞：
- pickle可以执行任意Python代码
- 恶意模型可以在加载时执行攻击代码
- 历史上有很多pickle相关的CVE

safetensors安全性：
- 纯数据存储，不包含可执行代码
- 只存储张量的数值和形状
- 反序列化不会执行任何代码
```

### 文件格式

```
safetensors文件结构：
┌──────────────────────────────┐
│ Header (JSON, 8 bytes size)  │
│  {                           │
│    "tensor1": {              │
│      "dtype": "F16",         │
│      "shape": [4096, 4096],  │
│      "data_offsets": [0, N]  │
│    },                        │
│    ...                       │
│  }                           │
├──────────────────────────────┤
│ Tensor Data                  │
│  - Raw bytes of tensors      │
│  - Contiguous memory layout  │
└──────────────────────────────┘
```

### 代码示例

```python
from safetensors import safe_open
from safetensors.torch import save_file, load_file
import torch

# 保存模型到safetensors
tensors = {
    "weight1": torch.randn(1024, 1024),
    "weight2": torch.randn(2048, 2048),
    "bias": torch.randn(1024),
}
save_file(tensors, "model.safetensors")

# 加载整个模型
loaded = load_file("model.safetensors")
print(loaded.keys())  # dict_keys(['weight1', 'weight2', 'bias'])

# 零拷贝加载（大文件推荐）
with safe_open("model.safetensors", framework="pt", device="cpu") as f:
    # 只加载需要的张量
    weight1 = f.get_tensor("weight1")
    print(weight1.shape)

# 内存映射加载（超大模型）
with safe_open("model.safetensors", framework="pt", device="cpu") as f:
    # 数据不加载到内存，只在需要时读取
    for key in f.keys():
        tensor = f.get_tensor(key)
        # 处理tensor
        pass

# 从HuggingFace模型转换
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")
model.save_pretrained("./gpt2", safe_serialization=True)  # 使用safetensors

# 验证safetensors文件
from safetensors import safe_open

def validate_safetensors(filepath):
    try:
        with safe_open(filepath, framework="pt") as f:
            metadata = f.metadata()
            print(f"Metadata: {metadata}")
            for key in f.keys():
                tensor = f.get_tensor(key)
                print(f"  {key}: shape={tensor.shape}, dtype={tensor.dtype}")
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False

validate_safetensors("model.safetensors")
```

### 与其他格式对比

| 格式 | 安全性 | 加载速度 | 零拷贝 | 跨平台 |
|------|--------|----------|--------|--------|
| safetensors | 高 | 快 | 支持 | 是 |
| PyTorch (.pt) | 低 | 中 | 不支持 | 是 |
| HDF5 | 高 | 快 | 支持 | 是 |
| ONNX | 高 | 快 | 部分 | 是 |
| GGUF | 高 | 快 | 支持 | 是 |

### 推荐论文

1. **HuggingFace, 2023** - "safetensors: A Safe and Fast Tensor Storage Format" - 官方文档
2. **Paszke et al., 2019** - "PyTorch: An Imperative Style Deep Learning Library" - PyTorch存储
3. **OWASP, 2020** - "Pickle Deserialization Security Risks" - 安全风险分析

---

## ONNX

### 这玩意儿到底是啥？

ONNX（Open Neural Network Exchange）是微软和Facebook联合推出的开放式神经网络交换格式。它定义了一套通用的算子规范，让模型可以在不同框架之间转换和部署。

**核心价值：**
- 框架互操作：PyTorch → ONNX → TensorRT
- 统一部署：一套格式，多种推理引擎
- 算子标准化：通用的计算图表示

### ONNX模型结构

```
ONNX Model结构：
┌─────────────────────────────┐
│ ModelProto                  │
│  - ir_version               │
│  - opset_import             │
│  - producer_name            │
│  - GraphProto (graph)       │
│    ├── NodeProto (nodes)    │
│    │    ├── Conv            │
│    │    ├── MatMul          │
│    │    └── ...             │
│    ├── ValueInfoProto       │
│    ├── TensorProto          │
│    └── ...                  │
└─────────────────────────────┘
```

### 代码示例

```python
import torch
import torch.onnx
import onnx
import onnxruntime as ort

# 定义模型
class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(3, 64, 3, padding=1)
        self.bn1 = torch.nn.BatchNorm2d(64)
        self.relu = torch.nn.ReLU()
        self.fc = torch.nn.Linear(64 * 32 * 32, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

model = SimpleModel()
model.eval()

# 导出为ONNX
dummy_input = torch.randn(1, 3, 32, 32)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"},
    },
    opset_version=17,
)

# 验证ONNX模型
onnx_model = onnx.load("model.onnx")
onnx.checker.check_model(onnx_model)
print("ONNX model is valid!")

# 查看模型信息
print(f"Ir version: {onnx_model.ir_version}")
print(f"Opset version: {onnx_model.opset_import[0].version}")
print(f"Inputs: {[inp.name for inp in onnx_model.graph.input]}")
print(f"Outputs: {[out.name for out in onnx_model.graph.output]}")

# 使用ONNX Runtime推理
session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name
output = session.run(None, {input_name: dummy_input.numpy()})
print(f"Output shape: {output[0].shape}")

# 模型优化
from onnxruntime.transformers import optimizer
optimized_model = optimizer.optimize_model(
    "model.onnx",
    model_type="bert",
    num_heads=12,
    hidden_size=768,
)
optimized_model.save_model_to_file("model_optimized.onnx")
```

### 大模型ONNX导出

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载模型
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model.eval()

# 准备输入
dummy_input = tokenizer("Hello world", return_tensors="pt")

# 导出（需要处理动态形状）
class GPT2Wrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        return self.model(input_ids=input_ids, attention_mask=attention_mask)

wrapped_model = GPT2Wrapper(model)

torch.onnx.export(
    wrapped_model,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "gpt2.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch", 1: "sequence"},
        "attention_mask": {0: "batch", 1: "sequence"},
        "logits": {0: "batch", 1: "sequence"},
    },
    opset_version=14,
)
```

### 推荐论文

1. **Bai et al., 2019** - "ONNX: Open Neural Network Exchange" - ONNX白皮书
2. **Microsoft, 2019** - "ONNX Runtime" - ONNX Runtime文档
3. **ONNX Community, 2023** - "ONNX Operator Specification" - 算子规范

---

## GPTQ

### 这玩意儿到底是啥？

GPTQ（Accurate Post-Training Quantization）是一种训练后量化方法，专门为大语言模型设计。它通过逐层量化，在保持模型精度的同时将权重量化到4-bit，是目前最流行的LLM量化方法之一。

**GPTQ核心思想：**
```
传统量化：直接对权重进行量化，精度损失大
GPTQ：
1. 逐层量化，考虑量化误差对后续层的影响
2. 使用Hessian矩阵（二阶梯度信息）优化量化
3. 最小化量化前后的输出差异
```

### 核心公式推导

**量化目标：**
$$
\arg\min_{\hat{W}} \| WX - \hat{W}X \|^2
$$

其中$W$是原始权重，$\hat{W}$是量化后的权重，$X$是输入激活。

**逐层量化：**
对于每一层，GPTQ按列量化权重：
$$
\hat{w}_j = Q(w_j) = \text{round}\left(\frac{w_j}{s}\right) \cdot s
$$

**误差补偿：**
量化第$j$列后，更新剩余权重以补偿误差：
$$
W_{:,j+1:} \leftarrow W_{:,j+1:} - \frac{w_j - \hat{w}_j}{[H^{-1}]_{jj}} \cdot [H^{-1}]_{j,j+1:}
$$

其中$H = 2X X^T$是Hessian矩阵。

**Act-Order（激活顺序）优化：**
```
传统顺序：按权重列顺序量化
Act-Order：按Hessian对角线元素大小排序后量化
效果：更重要的权重先量化，精度损失更小
```

### 代码示例

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig

# 配置GPTQ量化
quantization_config = GPTQConfig(
    bits=4,  # 4-bit量化
    dataset="c4",  # 校准数据集
    group_size=128,  # 量化分组大小
    desc_act=True,  # 启用Act-Order
    sym=False,  # 非对称量化
    true_sequential=True,  # 逐层顺序量化
    use_exllama=True,  # 使用ExLlama推理优化
)

# 加载并量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=quantization_config,
    device_map="auto",
)

# 保存量化后的模型
model.save_pretrained("./llama-2-7b-gptq")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.save_pretrained("./llama-2-7b-gptq")

# 加载已量化的模型
from auto_gptq import AutoGPTQForCausalLM

model = AutoGPTQForCausalLM.from_quantized(
    "./llama-2-7b-gptq",
    device="cuda:0",
    use_safetensors=True,
)

# 推理
tokenizer = AutoTokenizer.from_pretrained("./llama-2-7b-gptq")
inputs = tokenizer("Hello, how are you?", return_tensors="pt").to("cuda:0")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0]))
```

### AutoGPTQ完整示例

```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

# 准备校准数据
def get_calibration_data(tokenizer, n_samples=512, seq_len=512):
    from datasets import load_dataset
    dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
    samples = []
    for i, item in enumerate(dataset):
        if i >= n_samples:
            break
        text = item["text"][:seq_len]
        tokens = tokenizer(text, return_tensors="pt", max_length=seq_len, truncation=True)
        samples.append(tokens["input_ids"])
    return samples

# 量化配置
quantize_config = BaseQuantizeConfig(
    bits=4,  # 4-bit
    group_size=128,  # 分组大小
    desc_act=True,  # Act-Order
    sym=False,  # 非对称
    true_sequential=True,
    model_name_or_path="llama-2-7b-gptq",
)

# 加载模型
model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantize_config,
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 准备校准数据
calibration_data = get_calibration_data(tokenizer)

# 执行量化
model.quantize(calibration_data)

# 保存
model.save_quantized("./llama-2-7b-gptq")
tokenizer.save_pretrained("./llama-2-7b-gptq")
```

### 推荐论文

1. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" - GPTQ原论文
2. **Nagel et al., 2020** - "Up or Down? Adaptive Rounding for Post-Training Quantization" - 量化优化
3. **Yao et al., 2022** - "ZeroQuant: Efficient and Affordable Post-Training Quantization" - ZeroQuant

---

## AWQ

### 这玩意儿到底是啥？

AWQ（Activation-aware Weight Quantization）是一种激活感知的权重量化方法。它的核心发现是：**只有约1%的权重对模型输出影响最大**，这些"显著权重"需要保持更高精度。

**AWQ vs GPTQ：**
```
GPTQ：
- 基于Hessian矩阵优化
- 需要校准数据
- 量化过程较慢

AWQ：
- 基于激活幅度识别显著权重
- 不需要反向传播
- 量化过程更快
- 精度相当或更好
```

### 核心公式推导

**显著权重识别：**
$$
\text{importance}_j = \max_i |X_{i,j}|
$$

其中$X$是激活值，第$j$列权重的显著性由对应激活的最大幅度决定。

**通道缩放：**
AWQ通过缩放权重来保护显著权重：
$$
s = \arg\min_s \text{Quant}(s \cdot W) \cdot (s^{-1} \cdot X)
$$

通过找到最优缩放因子$s$，使得量化误差最小。

**量化公式：**
$$
\hat{W} = \text{round}\left(\frac{W}{\Delta}\right) \cdot \Delta
$$

其中$\Delta$是量化步长：
$$
\Delta = \frac{\max(|W|) - \min(|W|)}{2^{\text{bits}} - 1}
$$

### 代码示例

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

# 加载模型
model = AutoAWQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 量化配置
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM",
}

# 准备校准数据
from datasets import load_dataset
dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
calibration_data = [item["text"] for i, item in enumerate(dataset) if i < 512]

# 执行量化
model.quantize(
    tokenizer,
    quant_config=quant_config,
    calib_data=calibration_data,
)

# 保存
model.save_quantized("./llama-2-7b-awq")
tokenizer.save_pretrained("./llama-2-7b-awq")

# 加载量化模型推理
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer, TextStreamer

model = AutoAWQForCausalLM.from_quantized(
    "./llama-2-7b-awq",
    device_map="auto",
    fuse_layers=True,  # 融合层加速
)
tokenizer = AutoTokenizer.from_pretrained("./llama-2-7b-awq")

prompt = "Explain the theory of relativity in simple terms"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
streamer = TextStreamer(tokenizer)

output = model.generate(
    **inputs,
    streamer=streamer,
    max_new_tokens=256,
    temperature=0.7,
)
```

### 与GPTQ对比

| 特性 | AWQ | GPTQ |
|------|-----|------|
| 量化速度 | 快（~10分钟） | 慢（~1小时） |
| 精度 | 相当或更好 | 好 |
| 显存需求 | 较低 | 较高 |
| 校准数据 | 需要 | 需要 |
| 推理框架 | vLLM, LMDeploy | AutoGPTQ, ExLlamaV2 |

### 推荐论文

1. **Lin et al., 2023** - "AWQ: Activation-aware Weight Quantization for LLM Compression" - AWQ原论文，MLSys 2024
2. **Xiao et al., 2023** - "SmoothQuant: Accurate and Efficient Post-Training Quantization" - SmoothQuant
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization" - GPTQ对比

---

## bitsandbytes

### 这玩意儿到底是啥？

bitsandbytes是Tim Dettmers开发的量化库，它提供了8-bit和4-bit矩阵乘法运算，让大模型可以在消费级GPU上运行。它是HuggingFace Transformers原生支持的量化方案。

**核心优势：**
- 开箱即用：直接与Transformers集成
- 无需校准：训练后直接量化
- 灵活：支持混合精度
- 兼容性好：与LoRA等微调方法兼容

### 量化类型

**8-bit量化：**
```
LLM.int8() 方法：
- 大部分权重用8-bit量化
- 异常值（outliers）保持FP16
- 精度损失极小

Vector-wise量化：
- 每列独立量化
- 使用缩放因子
```

**4-bit量化（QLoRA）：**
```
NF4（NormalFloat4）：
- 针对正态分布权重设计
- 比标准4-bit更精确

Double Quantization：
- 量化常数也被量化
- 进一步减少显存
```

### 代码示例

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 8-bit量化配置
bnb_8bit_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,  # 异常值阈值
    llm_int8_has_fp16_weight=False,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_8bit_config,
    device_map="auto",
)

# 4-bit量化配置（QLoRA）
bnb_4bit_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # NF4量化
    bnb_4bit_use_double_quant=True,  # 双重量化
    bnb_4bit_compute_dtype=torch.float16,  # 计算精度
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_4bit_config,
    device_map="auto",
)

# 查看量化后的大小
def print_model_size(model):
    total_params = sum(p.numel() for p in model.parameters())
    total_size = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"Total parameters: {total_params / 1e9:.2f}B")
    print(f"Model size: {total_size / 1e9:.2f} GB")

print_model_size(model)

# QLoRA微调
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 准备模型
model = prepare_model_for_kbit_training(model)

# LoRA配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# 添加LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 输出: trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06%

# 直接使用8-bit推理
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
inputs = tokenizer("Hello, how are you?", return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0]))
```

### 显存占用对比

| 模型 | FP16 | 8-bit | 4-bit |
|------|------|-------|-------|
| 7B | 14GB | 7GB | 4GB |
| 13B | 26GB | 13GB | 8GB |
| 70B | 140GB | 70GB | 40GB |

### 推荐论文

1. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale" - 8-bit量化
2. **Dettmers et al., 2023** - "QLoRA: Efficient Finetuning of Quantized LLMs" - 4-bit量化
3. **Dettmers & Zettlemoyer, 2023** - "The Case for 4-bit Precision: k-bit Inference Scaling Laws" - 量化缩放定律

---

## 对比总结

### 模型格式对比

| 格式 | 主要用途 | 优点 | 缺点 |
|------|----------|------|------|
| GGUF | 本地推理 | 单文件、量化支持好 | 只支持llama.cpp生态 |
| safetensors | 安全存储 | 安全、快速、零拷贝 | 不包含量化 |
| ONNX | 跨框架部署 | 标准化、生态好 | 不支持动态图 |
| PyTorch (.pt) | 研究、训练 | 灵活 | 不安全（pickle） |

### 量化方法对比

| 方法 | 比特数 | 精度 | 速度 | 显存减少 | 适用场景 |
|------|--------|------|------|----------|----------|
| bitsandbytes 8-bit | 8 | 极高 | 快 | ~50% | 快速部署 |
| bitsandbytes 4-bit | 4 | 高 | 快 | ~75% | 微调 |
| GPTQ | 4 | 高 | 快 | ~75% | 生产部署 |
| AWQ | 4 | 高 | 最快 | ~75% | 高性能推理 |
| GGUF Q4_K_M | 4 | 高 | 快 | ~70% | 本地部署 |

### 选择建议

```
选择模型格式：
- 本地运行大模型 → GGUF
- 安全存储和分发 → safetensors
- 跨框架部署 → ONNX

选择量化方法：
- 快速验证/微调 → bitsandbytes 4-bit
- 生产部署高性能 → AWQ
- 平衡精度和速度 → GPTQ
- CPU推理 → GGUF量化
```

---

> 模型格式和量化是大模型部署的核心技术！GGUF适合本地部署，safetensors适合安全存储，ONNX适合跨框架。量化方面，AWQ速度快、GPTQ精度高、bitsandbytes易用。选择合适的组合，让你的模型跑得更快、更省、更稳！