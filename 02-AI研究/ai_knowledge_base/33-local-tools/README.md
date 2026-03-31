# 33. 本地运行工具

> 一句话：本地运行工具让你在自家电脑上就能跑大模型，Ollama最简单、llama.cpp最轻量、LM Studio图形化最友好。

---

## Ollama

### 这玩意儿到底是啥？

Ollama是目前最流行的本地大模型运行工具，由开发者Jeffrey Morgan创建。它的核心理念是**让本地运行大模型像安装App一样简单**。你不需要懂CUDA、不需要配置环境、不需要下载几十GB的模型文件——一条命令就搞定。

**为什么Ollama这么火？**
- **安装简单**：一行命令安装，自动下载模型
- **跨平台**：macOS、Linux、Windows都支持
- **模型丰富**：内置模型库，支持Llama、Qwen、Mistral、DeepSeek等
- **API兼容**：提供OpenAI兼容的API接口
- **硬件友好**：自动检测GPU/CPU，智能分配资源

### 核心概念

**Modelfile（模型配置文件）：**
```
FROM llama3.2                    # 基础模型
PARAMETER temperature 0.7        # 采样参数
PARAMETER top_p 0.9
SYSTEM You are a helpful assistant.  # 系统提示词
```

**量化格式：**
Ollama默认使用4-bit量化（Q4_0），在保持精度的同时大幅减少显存占用：

| 量化格式 | 显存占用 | 精度损失 | 适用场景 |
|----------|----------|----------|----------|
| Q4_0 | 最小 | ~2-3% | 消费级显卡 |
| Q5_0 | 中等 | ~1-2% | 平衡选择 |
| Q8_0 | 较大 | <1% | 追求精度 |
| FP16 | 最大 | 0% | 研究/训练 |

### 安装与使用

```bash
# macOS/Linux 安装
curl -fsSL https://ollama.com/install.sh | sh

# Windows 直接下载安装包
# https://ollama.com/download

# 运行模型（自动下载）
ollama run llama3.2

# 常用命令
ollama list              # 列出已下载模型
ollama pull qwen2.5      # 下载模型
ollama rm llama3.2       # 删除模型
ollama show llama3.2     # 查看模型信息
ollama ps                # 查看运行中的模型
```

### Python SDK

```python
import ollama

# 同步调用
response = ollama.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': '为什么天空是蓝色的？'},
])
print(response['message']['content'])

# 流式输出
for chunk in ollama.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': '写一首关于AI的诗'}],
    stream=True,
):
    print(chunk['message']['content'], end='', flush=True)

# 多模态（图片理解）
response = ollama.chat(model='llava', messages=[
    {
        'role': 'user',
        'content': '这张图片里有什么？',
        'images': ['image.jpg'],
    },
])

# 自定义模型参数
response = ollama.generate(
    model='llama3.2',
    prompt='解释一下量子计算',
    options={
        'temperature': 0.7,
        'top_p': 0.9,
        'num_predict': 512,  # 最大生成token数
        'num_ctx': 4096,     # 上下文长度
    },
)

# 创建自定义模型
modelfile = '''
FROM llama3.2
PARAMETER temperature 0.5
SYSTEM 你是一个专业的Python编程助手，用中文回答问题。
'''
ollama.create(model='my-python-assistant', modelfile=modelfile)
```

### OpenAI兼容API

```python
from openai import OpenAI

# 连接本地Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # 任意值
)

response = client.chat.completions.create(
    model='llama3.2',
    messages=[
        {'role': 'user', 'content': 'Hello!'},
    ],
)
print(response.choices[0].message.content)
```

### 推荐论文

1. **Ollama Team, 2023** - "Ollama: Get up and running with LLMs locally" - 官方文档
2. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication for Transformers" - 量化技术基础
3. **Frantar et al., 2023** - "GPTQ: Accurate Post-Training Quantization" - 量化算法

---

## llama.cpp

### 这玩意儿到底是啥？

llama.cpp是Georgi Gerganov开源的纯C/C++实现的LLM推理框架。它的最大特点是**零依赖、极致轻量**——不需要Python、不需要PyTorch、不需要CUDA，只要有C++编译器就能跑。

**为什么llama.cpp这么重要？**
- **纯C/C++实现**：无任何外部依赖
- **CPU优先设计**：在各种CPU上都能高效运行
- **量化支持**：GGUF格式，支持多种量化方案
- **跨平台**：Linux、macOS、Windows、Android、iOS
- **低内存占用**：在普通笔记本上也能运行70B模型

### GGUF格式详解

GGUF（GGML Universal Format）是llama.cpp使用的模型格式：

```
GGUF文件结构：
┌─────────────────────────────┐
│ Header (魔数、版本、架构信息) │
├─────────────────────────────┤
│ Metadata (KV键值对)          │
│  - general.architecture      │
│  - general.name              │
│  - llama.context_length      │
│  - ...                       │
├─────────────────────────────┤
│ Tensor Info (张量元信息)     │
│  - 每个张量的名称、维度、类型 │
├─────────────────────────────┤
│ Tensor Data (量化后的权重)   │
│  - Q4_0, Q5_0, Q8_0等格式    │
└─────────────────────────────┘
```

**量化类型对比：**

| 类型 | 比特数 | 压缩比 | 质量损失 |
|------|--------|--------|----------|
| Q4_0 | 4bit | 8x | 中等 |
| Q4_K_M | 4bit | 8x | 较低 |
| Q5_K_M | 5bit | 6.4x | 很低 |
| Q6_K | 6bit | 5.3x | 极低 |
| Q8_0 | 8bit | 4x | 几乎无 |

### 安装与使用

```bash
# 克隆并编译
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 启用CUDA支持
make LLAMA_CUDA=1

# 下载GGUF模型（从HuggingFace）
# 例如：https://huggingface.co/TheBloke/Llama-2-7B-GGUF

# 命令行推理
./llama-cli -m llama-2-7b.Q4_K_M.gguf -p "解释一下Transformer" -n 256

# 启动服务器
./llama-server -m llama-2-7b.Q4_K_M.gguf --host 0.0.0.0 --port 8080

# 批量处理
./llama-batched -m model.gguf -c 4096 -b 512
```

### Python绑定

```python
from llama_cpp import Llama

# 加载模型
llm = Llama(
    model_path="llama-2-7b.Q4_K_M.gguf",
    n_ctx=4096,           # 上下文长度
    n_gpu_layers=32,      # GPU层数（0=纯CPU）
    n_threads=8,          # CPU线程数
    verbose=False,
)

# 基本推理
output = llm(
    "Q: 什么是机器学习？A:",
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
    stop=["Q:", "\n"],
)
print(output['choices'][0]['text'])

# 聊天模式
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "解释一下神经网络。"},
    ],
)
print(response['choices'][0]['message']['content'])

# 流式输出
for chunk in llm(
    "讲一个短故事",
    max_tokens=100,
    stream=True,
):
    print(chunk['choices'][0]['text'], end='', flush=True)

# 函数调用（Function Calling）
llm = Llama(
    model_path="model.gguf",
    chat_format="chatml-function-calling",
)

response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
        },
    }],
)
```

### 模型转换与量化

```bash
# 从HuggingFace下载模型后转换为GGUF
python convert-hf-to-gguf.py /path/to/model --outfile model.gguf --outtype q4_K_M

# 量化已有GGUF模型
./llama-quantize model.gguf model-q4_K_M.gguf q4_K_M

# 量化类型选项：
# q4_0, q4_1, q5_0, q5_1, q8_0
# q2_k, q3_k, q4_k_s, q4_k_m, q5_k_s, q5_k_m, q6_k
```

### 推荐论文

1. **Gerganov, 2023** - "llama.cpp: A C++ Implementation of LLaMA" - 项目文档
2. **Frantar & Alistarh, 2023** - "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers"
3. **Dettmers et al., 2022** - "LLM.int8(): 8-bit Matrix Multiplication for Transformers"

---

## LM Studio

### 这玩意儿到底是啥？

LM Studio是一个带图形界面的本地大模型运行工具，适合不想折腾命令行的用户。它提供了类似ChatGPT的聊天界面，支持从HuggingFace一键下载模型，还提供了本地API服务器功能。

**核心特点：**
- **图形化界面**：像使用ChatGPT一样简单
- **模型管理**：内置HuggingFace模型搜索和下载
- **多模型支持**：同时加载多个模型切换使用
- **API服务器**：提供OpenAI兼容的本地API
- **跨平台**：macOS、Windows、Linux

### 使用流程

```
1. 下载安装 LM Studio
   ↓
2. 搜索并下载模型（如 Llama-3-8B-Instruct）
   ↓
3. 选择模型并配置参数
   ↓
4. 开始聊天
```

### 配置参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| GPU Offload | GPU加速层数 | 全部（如果有GPU） |
| Context Length | 上下文长度 | 4096-8192 |
| Temperature | 采样温度 | 0.7 |
| Top P | 核采样 | 0.9 |
| Max Tokens | 最大生成长度 | 512-2048 |

### 本地API服务器

LM Studio可以启动一个OpenAI兼容的本地服务器：

```
设置 → Developer → Enable Local Server
默认端口：1234
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)

response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

---

## GPT4All

### 这玩意儿到底是啥？

GPT4All是一个开源的本地大模型运行工具，由Nomic AI开发。它的特点是**完全免费开源、注重隐私、跨平台**，特别适合在无网络环境下使用。

**核心特点：**
- **完全离线**：无需联网即可运行
- **隐私优先**：所有数据都在本地处理
- **模型丰富**：内置多种开源模型
- **Python SDK**：方便集成到应用中

### Python SDK

```python
from gpt4all import GPT4All

# 加载模型（首次会自动下载）
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# 生成文本
response = model.generate("什么是深度学习？", max_tokens=256)
print(response)

# 聊天模式
with model.chat_session():
    response = model.generate("你好！", temp=0.7)
    print(response)

# 流式输出
for chunk in model.generate("讲个故事", streaming=True):
    print(chunk, end='', flush=True)
```

---

## LocalAI

### 这玩意儿到底是啥？

LocalAI是一个OpenAI API兼容的本地服务，让你可以把任何OpenAI SDK的调用无缝切换到本地模型。它支持多种后端（包括llama.cpp），适合需要本地部署OpenAI兼容API的场景。

**核心特点：**
- **OpenAI API兼容**：无缝替换OpenAI API
- **多后端支持**：llama.cpp、whisper、stable diffusion等
- **Docker部署**：一键启动服务
- **多模态支持**：文本、图像、音频

### Docker部署

```bash
# 启动LocalAI
docker run -p 8080:8080 \
    -v $PWD/models:/models \
    -e MODELS_PATH=/models \
    localai/localai:latest

# 下载模型
curl http://localhost:8080/models/apply \
    -H "Content-Type: application/json" \
    -d '{"name": "llama-2-7b-chat"}'

# 测试API
curl http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama-2-7b-chat",
        "messages": [{"role": "user", "content": "Hello"}]
    }'
```

---

## MLC LLM

### 这玩意儿到底是啥？

MLC LLM是专门为移动端和边缘设备设计的大模型部署方案，由CMU的研究团队开发。它让你能在手机、平板上本地运行大模型。

**核心特点：**
- **移动端优先**：iOS、Android原生支持
- **高效推理**：针对移动GPU优化
- **模型压缩**：专为移动设备优化
- **跨平台**：iOS、Android、Web、桌面

### iOS部署

```swift
// Swift iOS 示例
import MLCEngine

let engine = MLCEngine(model: "Llama-2-7b-chat-q4f16_1")

let response = engine.chat.completions.create(
    messages: [.user("Hello!")],
    stream: false
)
```

---

## 对比总结

| 工具 | 易用性 | 跨平台 | API兼容 | 移动端 | 推荐场景 |
|------|--------|--------|---------|--------|----------|
| Ollama | ★★★★★ | ★★★★☆ | OpenAI | ✗ | 快速上手、开发测试 |
| llama.cpp | ★★★☆☆ | ★★★★★ | ✓ | ✓ | 极致轻量、嵌入式 |
| LM Studio | ★★★★★ | ★★★★☆ | OpenAI | ✗ | 非技术用户、图形化 |
| GPT4All | ★★★★☆ | ★★★★☆ | ✓ | ✗ | 离线使用、隐私优先 |
| LocalAI | ★★★☆☆ | ★★★★☆ | OpenAI | ✗ | API服务部署 |
| MLC LLM | ★★★☆☆ | ★★★★★ | ✓ | ✓ | 移动端部署 |

### 选择建议

```
新手入门 → Ollama 或 LM Studio
追求极致性能/轻量 → llama.cpp
移动端部署 → MLC LLM
生产环境API服务 → LocalAI 或 Ollama
完全离线使用 → GPT4All
```

---

> 本地运行工具让大模型走进千家万户！Ollama适合快速上手，llama.cpp追求极致轻量，LM Studio适合图形化使用。选择适合自己的工具，享受本地大模型带来的便利！