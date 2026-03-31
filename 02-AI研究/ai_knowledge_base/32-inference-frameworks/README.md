# 32. 推理服务框架

> 一句话：推理框架就是让大模型跑得又快又省显存的工具，vLLM、TensorRT-LLM、TGI是三大主流选择。

---

## vLLM

### 这玩意儿到底是啥？

vLLM是加州大学伯克利分校开源的大模型推理框架，核心创新是**PagedAttention**技术。它把KV Cache的管理方式从"连续分配"改成了"分页管理"，就像操作系统的虚拟内存一样，大大减少了显存碎片和浪费。

**为什么vLLM这么快？**
- **PagedAttention**：KV Cache分页管理，显存利用率接近100%
- **连续批处理**：动态调度请求，不用等所有请求都完成
- **高效CUDA内核**：优化的注意力计算内核
- **吞吐量提升**：比HuggingFace Transformers高14-24倍

### 核心技术：PagedAttention

**传统KV Cache的问题：**
```
传统方式：每个请求预分配最大长度的连续显存
问题1：预分配浪费（实际序列往往比最大长度短）
问题2：内存碎片（频繁分配释放导致）
问题3：无法共享（相同前缀无法复用）
```

**PagedAttention解决方案：**
```
1. 将KV Cache分成固定大小的block（比如16个token一块）
2. 用Block表管理物理block和逻辑block的映射
3. 支持Copy-on-Write，相同前缀的请求共享block
4. 类似操作系统的虚拟内存管理
```

**核心公式：**

传统注意力：
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) V
$$

PagedAttention：
$$
\text{Attention}(Q, K_{blocks}, V_{blocks}) = \sum_{i} \text{softmax}\left(\frac{QK_{block_i}^T}{\sqrt{d}}\right) V_{block_i}
$$

**内存效率对比：**

| 方法 | 显存利用率 | 支持共享 | 碎片问题 |
|------|------------|----------|----------|
| 传统预分配 | 20-40% | 否 | 严重 |
| PagedAttention | >95% | 是 | 几乎无 |

### PyTorch代码示例

```python
from vllm import LLM, SamplingParams

# 初始化模型
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    tensor_parallel_size=1,  # GPU数量
    gpu_memory_utilization=0.9,  # GPU显存利用率
    max_model_len=4096,  # 最大序列长度
)

# 采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
    n=1,  # 每个prompt生成几个回复
)

# 批量推理
prompts = [
    "解释一下什么是Transformer",
    "写一首关于春天的诗",
    "如何学习机器学习？",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt}")
    print(f"Generated: {generated_text}\n")

# 使用OpenAI兼容API
from vllm import AsyncLLMEngine
import asyncio

async def stream_generation():
    from vllm.engine.arg_utils import AsyncEngineArgs
    from vllm.engine.async_llm_engine import AsyncLLMEngine

    engine_args = AsyncEngineArgs(
        model="meta-llama/Llama-2-7b-hf",
        tensor_parallel_size=1,
    )
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    from vllm import SamplingParams, RequestOutput
    from vllm.inputs import TextPrompt

    request_id = "test-request"
    sampling_params = SamplingParams(temperature=0.7, max_tokens=100)

    async for output in engine.generate(
        TextPrompt(prompt="你好，请介绍一下自己"),
        sampling_params,
        request_id,
    ):
        if output.finished:
            print(output.outputs[0].text)

# asyncio.run(stream_generation())
```

### 高级功能

**前缀缓存（Prefix Caching）：**
```python
# 开启前缀缓存，复用相同前缀的KV Cache
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    enable_prefix_caching=True,  # 开启前缀缓存
)

# 相同前缀的多个请求会自动共享KV Cache
system_prompt = "你是一个专业的AI助手，请用中文回答问题。"
prompts = [
    f"{system_prompt}\n用户：什么是机器学习？",
    f"{system_prompt}\n用户：什么是深度学习？",
    f"{system_prompt}\n用户：什么是强化学习？",
]
# system_prompt的KV Cache只会计算一次
```

**张量并行：**
```python
from vllm import LLM

# 多GPU张量并行
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,  # 使用4个GPU
    gpu_memory_utilization=0.9,
)
```

### 推荐论文

1. **Kwon et al., 2023** - "Efficient Memory Management for Large Language Model Serving with PagedAttention" - vLLM原论文，SOSP 2023最佳论文
2. **Yu et al., 2022** - "Orca: A Distributed Serving System for Transformer-Based Generative Models" - 连续批处理的早期工作
3. **Pope et al., 2022** - "Efficiently Scaling Transformer Inference" - Google的大规模推理优化

---

## TensorRT-LLM

### 这玩意儿到底是啥？

TensorRT-LLM是NVIDIA推出的高性能大模型推理框架，专门针对NVIDIA GPU优化。它结合了TensorRT的深度学习推理能力和LLM特定的优化技术，是目前最快的推理方案之一。

**核心优势：**
- **深度硬件优化**：针对NVIDIA GPU的每一个细节优化
- **多GPU支持**：张量并行、流水线并行
- **量化支持**：INT8、INT4、FP8量化
- **内核融合**：算子融合减少显存访问

### 核心技术

**1. 算子融合（Kernel Fusion）：**
```
传统方式：
LayerNorm → 单独kernel → Attention → 单独kernel → FFN

TensorRT-LLM：
LayerNorm + Attention + FFN → 融合成一个kernel

好处：
- 减少显存读写次数
- 减少kernel launch开销
- 提高GPU利用率
```

**2. 量化推理：**
```
FP16：标准精度
INT8：量化后精度下降<1%，速度提升2-3倍
INT4：量化后精度下降2-3%，速度提升3-4倍
FP8：H100支持的新格式，精度接近FP16
```

**3. 动态批处理：**
```
支持in-flight batching：
- 新请求动态加入batch
- 完成的请求立即移除
- 最大化GPU利用率
```

### 代码示例

```python
# TensorRT-LLM 使用流程

# Step 1: 构建引擎（只需要执行一次）
import tensorrt_llm
from tensorrt_llm.builder import Builder, BuilderConfig
from tensorrt_llm.models import LLaMAForCausalLM

def build_engine(model_dir, output_dir, tp_size=1):
    """构建TensorRT-LLM引擎"""
    builder = Builder()

    # 配置
    config = BuilderConfig(
        max_batch_size=32,
        max_input_len=2048,
        max_output_len=512,
        max_beam_width=1,
        tp_size=tp_size,  # 张量并行度
    )

    # 加载模型
    model = LLaMAForCausalLM.from_hugging_face(
        model_dir,
        tensor_parallel=tp_size,
    )

    # 构建引擎
    engine = builder.create_engine(model, config)
    engine.save(output_dir)

# Step 2: 运行推理
from tensorrt_llm.runtime import ModelRunner

runner = ModelRunner(
    engine_dir="llama-7b-trt-llm",
    lora_dir=None,
    rank=0,
)

# 生成
output = runner.generate(
    input_ids=input_ids,
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.9,
)
```

### 与vLLM对比

| 特性 | vLLM | TensorRT-LLM |
|------|------|--------------|
| 开发者 | UC Berkeley | NVIDIA |
| 硬件支持 | 多种GPU | NVIDIA专用 |
| 显存效率 | PagedAttention优秀 | 优秀 |
| 推理速度 | 快 | 更快（硬件优化） |
| 易用性 | 高 | 中（需要构建引擎） |
| 量化支持 | 支持 | 全面支持 |

### 推荐论文

1. **NVIDIA, 2023** - "TensorRT-LLM: High-Performance Inference for Large Language Models" - 官方白皮书
2. **Shazeer, 2019** - "Fast Transformer Decoding: One Write-Head is All You Need" - MQA/MLA技术
3. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication for Transformers" - 量化技术

---

## TGI (Text Generation Inference)

### 这玩意儿到底是啥？

TGI是HuggingFace推出的生产级大模型推理服务框架。它提供了完整的REST API接口，支持模型量化、流式生成、token流等特性，是部署大模型API服务的首选方案之一。

**核心特点：**
- **生产就绪**：完整的API服务器，支持负载均衡
- **流式生成**：Server-Sent Events实时输出
- **量化支持**：bitsandbytes、GPTQ、AWQ
- **多GPU支持**：张量并行和流水线并行
- **安全特性**：水印、敏感词过滤

### 核心技术

**1. 连续批处理（Continuous Batching）：**
```
传统批处理：
Batch 1: [等待所有请求完成] → Batch 2: [等待...] → ...

连续批处理：
请求A: ████░░░░░░ → 完成
请求B: ████████░░ → 完成
请求C: ██████████ → 完成
           ↑ 新请求可以随时加入
```

**2. 量化推理：**
```python
# bitsandbytes量化
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=quantization_config,
    device_map="auto",
)
```

### 部署示例

```bash
# 使用Docker部署TGI
docker run --gpus all \
    --shm-size 1g \
    -p 8080:80 \
    -v $PWD/data:/data \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id meta-llama/Llama-2-7b-hf \
    --quantize bitsandbytes-nf4 \
    --max-total-tokens 4096

# 使用Python客户端
from text_generation import Client

client = Client("http://localhost:8080")

# 流式生成
for response in client.generate_stream(
    "解释一下什么是Transformer",
    max_new_tokens=256,
    temperature=0.7,
):
    if not response.token.special:
        print(response.token.text, end="", flush=True)
```

### Python服务端示例

```python
from text_generation_server import server

# 启动服务器
server.serve(
    model_id="meta-llama/Llama-2-7b-hf",
    revision="main",
    sharded=False,
    num_shard=1,
    quantize="bitsandbytes-nf4",
    dtype="float16",
    trust_remote_code=False,
)
```

### 推荐论文

1. **HuggingFace, 2023** - "Text Generation Inference" - 官方文档
2. **Dettmers et al., 2023** - "QLoRA: Efficient Finetuning of Quantized LLMs" - bitsandbytes量化
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" - GPTQ量化

---

## LMDeploy

### 这玩意儿到底是啥？

LMDeploy是上海人工智能实验室开源的大模型推理部署工具，特别针对国产GPU和NVIDIA GPU都有良好支持。它的核心创新是**TurboMind推理引擎**，在保持高精度的同时实现了极快的推理速度。

**核心特点：**
- **TurboMind引擎**：自研高性能推理引擎
- **多后端支持**：Turbomind、PyTorch、TensorRT
- **量化支持**：Weight-only INT4/INT8、KV Cache量化
- **长文本支持**：支持32K+上下文
- **多模态支持**：支持LLaVA等多模态模型

### 核心技术

**1. TurboMind引擎：**
```
TurboMind优化：
- FlashAttention集成
- 算子融合优化
- 高效KV Cache管理
- 动态批处理
```

**2. 量化技术：**
```
Weight-only量化：
- INT4量化：权重4bit，激活16bit
- INT8量化：权重8bit，激活16bit
- KV Cache量化：KV Cache压缩到INT8

性能：
- INT4量化后推理速度提升约2倍
- 显存占用减少约60%
- 精度损失<2%
```

### 代码示例

```python
from lmdeploy import pipeline, TurbomindEngineConfig

# 加载模型
pipe = pipeline(
    "meta-llama/Llama-2-7b-hf",
    backend_config=TurbomindEngineConfig(
        tp=1,  # 张量并行度
        model_name="llama2",
        cache_max_entry_count=0.8,  # KV Cache显存比例
    )
)

# 批量推理
prompts = [
    "什么是深度学习？",
    "如何学习编程？",
    "AI的发展前景如何？",
]
responses = pipe(prompts)
for prompt, response in zip(prompts, responses):
    print(f"Q: {prompt}")
    print(f"A: {response.text}\n")

# 流式推理
for response in pipe.stream_infer("写一首关于AI的诗"):
    print(response.text, end="", flush=True)
```

### 量化示例

```python
from lmdeploy import pipeline, TurbomindEngineConfig
from lmdeploy.turbomind import TurbomindModelConfig

# INT4量化配置
config = TurbomindModelConfig(
    weight_type="int4",  # INT4量化
    group_size=128,  # 量化分组大小
)

pipe = pipeline(
    "meta-llama/Llama-2-7b-hf",
    backend_config=TurbomindEngineConfig(model_config=config),
)
```

### 推荐论文

1. **Shanghai AI Lab, 2023** - "LMDeploy: A Toolkit for Compressing, Deploying, and Serving LLMs" - 官方文档
2. **Xiao et al., 2023** - "SmoothQuant: Accurate and Efficient Post-Training Quantization" - 量化技术
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization" - GPTQ量化

---

## ONNX Runtime

### 这玩意儿到底是啥？

ONNX Runtime是微软开源的跨平台机器学习推理引擎，支持ONNX格式的模型。虽然它不是专门为LLM设计的，但由于其广泛的硬件支持和成熟的生态系统，仍然是部署小到中型模型的重要选择。

**核心特点：**
- **跨平台**：Windows、Linux、macOS、Android、iOS
- **多硬件支持**：CPU、GPU、NPU、FPGA
- **多语言API**：Python、C++、C#、Java、JavaScript
- **优化执行**：图优化、算子融合

### 代码示例

```python
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

# 加载ONNX模型
session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'],
)

# 获取输入输出信息
input_names = [inp.name for inp in session.get_inputs()]
output_names = [out.name for out in session.get_outputs()]

# 准备输入
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
inputs = tokenizer("Hello, world!", return_tensors="np")

# 推理
outputs = session.run(output_names, dict(inputs))

# 使用IO Binding优化（减少数据拷贝）
io_binding = session.io_binding()
for name, value in inputs.items():
    io_binding.bind_input(
        name=name,
        device_type="cuda",
        device_id=0,
        element_type=np.int64,
        shape=value.shape,
        buffer_ptr=value.ctypes.data,
    )
io_binding.synchronize_inputs()

for name in output_names:
    io_binding.bind_output(name, "cuda")

session.run_with_iobinding(io_binding)
outputs = io_binding.copy_outputs_to_cpu()
```

### 转换模型到ONNX

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# 导出为ONNX
class ONNXModel(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        return self.model(input_ids=input_ids, attention_mask=attention_mask)

onnx_model = ONNXModel(model)
onnx_model.eval()

dummy_input = tokenizer("Hello", return_tensors="pt")
torch.onnx.export(
    onnx_model,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "gpt2.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch", 1: "seq"},
        "attention_mask": {0: "batch", 1: "seq"},
        "logits": {0: "batch", 1: "seq"},
    },
    opset_version=14,
)
```

### 推荐论文

1. **Microsoft, 2019** - "ONNX Runtime: A High-Performance Inference Engine" - 官方文档
2. **Bai et al., 2021** - "ONNX: Open Neural Network Exchange" - ONNX格式
3. **ONNX Community, 2023** - "ONNX Runtime Performance Tuning" - 性能优化指南

---

## OpenVINO

### 这玩意儿到底是啥？

OpenVINO是Intel开源的AI推理优化工具包，专门针对Intel硬件（CPU、GPU、VPU）进行深度优化。它特别适合在边缘设备和Intel服务器上部署AI模型。

**核心特点：**
- **Intel硬件优化**：针对Intel CPU/GPU/VPU深度优化
- **模型优化**：量化、剪枝、算子融合
- **边缘部署**：支持各种边缘设备
- **易用性**：支持PyTorch、TensorFlow等框架直接导入

### 代码示例

```python
from openvino.runtime import Core
import numpy as np

# 初始化OpenVINO核心
core = Core()

# 列出可用设备
print("Available devices:", core.available_devices)

# 加载模型
model = core.read_model(model="model.xml")
compiled_model = core.compile_model(model=model, device_name="CPU")

# 获取输入输出
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)

# 创建推理请求
infer_request = compiled_model.create_infer_request()

# 准备输入数据
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)

# 执行推理
infer_request.infer({input_layer.any_name: input_data})

# 获取输出
output = infer_request.get_output_tensor().data

# 使用OpenVINO的PyTorch前端
import torch
import openvino.torch

model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
model.eval()

# 自动转换为OpenVINO
ov_model = openvino.torch.convert(model)

# 使用NNCF进行量化
import nncf

calibration_dataset = ...  # 校准数据集
quantized_model = nncf.quantize(
    model,
    calibration_dataset,
    preset=nncf.QuantizationPreset.MIXED,
)
```

### 推荐论文

1. **Intel, 2018** - "OpenVINO Toolkit: Deep Learning Deployment Toolkit" - 官方文档
2. **Kuzmin et al., 2019** - "NNCF: Neural Network Compression Framework" - 量化框架
3. **Zhou et al., 2021** - "Incremental Network Quantization" - 量化算法

---

## llama.cpp

### 这玩意儿到底是啥？

llama.cpp是Georgi Gerganov开源的纯C/C++实现的LLM推理框架，无需任何外部依赖，可以在CPU上高效运行大模型。它是目前最轻量、最便携的LLM推理方案。

**核心特点：**
- **纯C/C++实现**：无任何外部依赖
- **CPU优化**：针对各种CPU架构优化
- **量化支持**：GGUF格式，支持4-bit、5-bit、8-bit量化
- **跨平台**：Linux、macOS、Windows、Android、iOS
- **低内存占用**：在普通笔记本上也能运行7B模型

### 代码示例

```bash
# 安装
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 下载模型并转换为GGUF
python convert.py /path/to/llama-2-7b --outfile llama-2-7b.gguf --outtype q4_0

# 运行推理
./main -m llama-2-7b.gguf -p "解释一下什么是Transformer" -n 256

# 启动服务器
./server -m llama-2-7b.gguf --host 0.0.0.0 --port 8080
```

```python
# Python绑定
from llama_cpp import Llama

llm = Llama(
    model_path="llama-2-7b.gguf",
    n_ctx=2048,  # 上下文长度
    n_gpu_layers=32,  # GPU层数（0=纯CPU）
    n_threads=8,  # CPU线程数
)

output = llm(
    "解释一下什么是Transformer",
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
)
print(output['choices'][0]['text'])
```

### 推荐论文

1. **Gerganov, 2023** - "llama.cpp: A C++ Implementation of LLaMA" - 项目文档
2. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication" - 量化技术
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization" - GPTQ量化

---

## 对比总结

| 框架 | 开发者 | 硬件支持 | 核心优势 | 适用场景 |
|------|--------|----------|----------|----------|
| vLLM | UC Berkeley | 多种GPU | PagedAttention，高吞吐 | 服务端高并发 |
| TensorRT-LLM | NVIDIA | NVIDIA GPU | 极致性能，深度优化 | NVIDIA服务器 |
| TGI | HuggingFace | 多种GPU | 生产就绪，完整API | API服务部署 |
| LMDeploy | 上海AI Lab | 多种GPU+国产 | 国产GPU支持，TurboMind | 国产硬件部署 |
| ONNX Runtime | Microsoft | 全平台 | 跨平台，多硬件 | 通用部署 |
| OpenVINO | Intel | Intel硬件 | Intel优化，边缘部署 | Intel设备 |
| llama.cpp | 社区 | 全平台 | 轻量便携，CPU友好 | 边缘设备、个人使用 |

### 选择建议

```
高并发服务端 → vLLM 或 TGI
NVIDIA服务器追求极致性能 → TensorRT-LLM
国产GPU部署 → LMDeploy
边缘设备/Intel硬件 → OpenVINO 或 llama.cpp
快速原型/研究 → vLLM
```

---

> 推理框架是大模型落地的关键！vLLM适合高并发场景，TensorRT-LLM追求极致性能，TGI适合生产部署，llama.cpp适合个人使用。选择合适的框架能让你的模型跑得更快、更省、更稳！