# 34. API聚合/路由平台

> 一句话：API聚合平台让你用一套API访问几十种大模型，OpenRouter最全面、Together AI最快、国内平台更懂中文。

---

## OpenRouter

### 这玩意儿到底是啥？

OpenRouter是一个统一的LLM API聚合平台，它让你通过一个API接口访问OpenAI、Anthropic、Google、Meta等几十家公司的模型。不用在每个平台注册账号、不用管理多套API密钥——一个OpenRouter账号搞定所有。

**为什么OpenRouter这么好用？**
- **模型齐全**：支持100+模型，包括GPT-4、Claude、Gemini、Llama等
- **价格透明**：按实际token计费，自动选择最便宜的提供商
- **统一API**：OpenAI兼容格式，零改动迁移
- **Fallback机制**：一个提供商挂了自动切换到备用
- **免费模型**：部分模型免费使用

### 核心概念

**路由策略：**
```
OpenRouter 路由逻辑：
用户请求 → 选择模型 → 选择提供商 → 转发请求 → 返回结果
                    ↓
            自动选择：
            - 价格最低
            - 响应最快
            - 可用性最高
```

**定价模式：**
OpenRouter提供三种定价模式：
- **按token计费**：实际使用多少付多少
- **提供商选择**：指定使用某个提供商
- **自动优化**：系统自动选择最优提供商

### 使用方法

```python
from openai import OpenAI

# 连接OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

# 调用任意模型
response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",  # 或 openai/gpt-4-turbo
    messages=[
        {"role": "user", "content": "Hello!"},
    ],
)

# 使用免费模型
response = client.chat.completions.create(
    model="meta-llama/llama-3.2-3b-instruct:free",
    messages=[{"role": "user", "content": "Hello!"}],
)

# 指定提供商
response = client.chat.completions.create(
    model="openai/gpt-4-turbo",
    provider={
        "only": ["openai"],  # 只使用OpenAI官方
    },
    messages=[{"role": "user", "content": "Hello!"}],
)

# 启用Fallback
response = client.chat.completions.create(
    model="anthropic/claude-3-opus",
    provider={
        "order": ["anthropic", "together", "deepinfra"],
        "allow_fallbacks": True,
    },
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### 获取模型列表

```python
import requests

# 获取所有可用模型
response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
)

models = response.json()["data"]
for model in models:
    print(f"{model['id']}: ${model['pricing']['prompt']}/1K tokens")
```

### 推荐论文

1. **OpenRouter Team, 2023** - "OpenRouter: A Unified API for LLMs" - 官方文档
2. **Chen et al., 2023** - "FrugalGPT: How to Use Large Language Models While Reducing Cost" - 成本优化
3. **Sheng et al., 2023** - "Flexible LLM Routing" - 模型路由策略

---

## Together AI

### 这玩意儿到底是啥？

Together AI是一个专注于开源大模型的API平台，提供极快的推理速度和低廉的价格。它由Stanford和Berkeley的研究人员创立，核心优势是对开源模型（如Llama、Mistral）的极致优化。

**核心特点：**
- **速度快**：推理延迟行业领先，首token时间<100ms
- **价格低**：比OpenAI便宜50-90%
- **开源优先**：第一时间支持最新开源模型
- **微调支持**：支持自定义模型微调和部署

### 使用方法

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="YOUR_TOGETHER_API_KEY",
)

# 使用Llama 3
response = client.chat.completions.create(
    model="meta-llama/Llama-3-70b-chat-hf",
    messages=[{"role": "user", "content": "Hello!"}],
)

# 使用Mixtral
response = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[{"role": "user", "content": "Hello!"}],
)

# 代码生成
response = client.chat.completions.create(
    model="codellama/CodeLlama-70b-Instruct-hf",
    messages=[{"role": "user", "content": "Write a Python function to sort a list"}],
)

# 流式输出
for chunk in client.chat.completions.create(
    model="meta-llama/Llama-3-8b-chat-hf",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
):
    print(chunk.choices[0].delta.content, end="")
```

### 模型微调

```python
import together

# 上传训练数据
together.Files.upload("train.jsonl")

# 创建微调任务
fine_tune = together.Finetune.create(
    training_file="file-abc123",
    model="meta-llama/Llama-3-8b-chat-hf",
    n_epochs=3,
    learning_rate=1e-5,
)

# 查看状态
print(fine_tune.status)

# 使用微调后的模型
client.chat.completions.create(
    model=fine_tune.model_name,
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### 推荐论文

1. **Together AI Team, 2023** - "Together Inference Engine" - 官方技术博客
2. **Pope et al., 2022** - "Efficiently Scaling Transformer Inference" - 推理优化
3. **Kwon et al., 2023** - "Efficient Memory Management for LLM Serving" - vLLM论文

---

## Replicate

### 这玩意儿到底是啥？

Replicate是一个模型部署和API服务平台，让你可以运行各种AI模型（不只是LLM），包括图像生成、音频处理、视频分析等。它的特点是**零运维**——你只需要指定模型，剩下的都交给Replicate。

**核心特点：**
- **模型丰富**：Stable Diffusion、LLaVA、Whisper、MusicGen等
- **按秒计费**：模型运行时间计费，不用时不花钱
- **一键部署**：自定义模型一键部署为API
- **冷启动优化**：模型预加载，快速响应

### 使用方法

```python
import replicate

# 运行LLaMA
output = replicate.run(
    "meta/llama-2-70b-chat",
    input={
        "prompt": "Write a poem about AI",
        "max_tokens": 256,
    },
)
print(output)

# 运行Stable Diffusion
output = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7d3705113c9f0f3b3d3d3d3d3d3d3",
    input={
        "prompt": "A beautiful sunset over mountains",
        "width": 1024,
        "height": 1024,
    },
)
print(output[0])

# 运行LLaVA（多模态）
output = replicate.run(
    "yorickvp/llava-13b",
    input={
        "image": open("image.jpg", "rb"),
        "prompt": "What's in this image?",
    },
)

# 异步运行（适合长时间任务)
model = replicate.models.get("meta/llama-2-70b-chat")
prediction = model.predict(prompt="Long story...", async=True)
prediction.wait()
print(prediction.output)
```

### 部署自定义模型

```python
# 使用Cog打包模型
# cog.yaml
"""
build:
  gpu: true
  python_version: "3.11"
  python_packages:
    - torch
    - transformers
predict: predict.py:Predictor
"""

# predict.py
"""
from cog import BasePredictor, Input
from transformers import AutoModelForCausalLM, AutoTokenizer

class Predictor(BasePredictor):
    def setup(self):
        self.model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")

    def predict(self, prompt: str = Input(description="Input prompt")) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=256)
        return self.tokenizer.decode(outputs[0])
"""

# 部署
# cog push r8.im/username/model-name
```

### 推荐论文

1. **Replicate Team, 2023** - "Replicate: Run AI Models in the Cloud" - 官方文档
2. **Chen et al., 2023** - "Serverless Machine Learning" - 无服务器ML
3. **HuggingFace, 2023** - "Model Deployment Best Practices" - 模型部署

---

## 国内平台

### 智谱AI（GLM）

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="glm-4",  # 或 glm-4-flash（更快更便宜）
    messages=[
        {"role": "user", "content": "你好！"},
    ],
)
print(response.choices[0].message.content)

# 流式输出
for chunk in client.chat.completions.create(
    model="glm-4",
    messages=[{"role": "user", "content": "写一首诗"}],
    stream=True,
):
    print(chunk.choices[0].delta.content, end="")

# 函数调用
response = client.chat.completions.create(
    model="glm-4",
    messages=[{"role": "user", "content": "北京天气怎么样？"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                },
            },
        },
    }],
)
```

### 百川智能（Baichuan）

```python
import requests

response = requests.post(
    "https://api.baichuan-ai.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json",
    },
    json={
        "model": "Baichuan4",
        "messages": [{"role": "user", "content": "你好！"}],
    },
)
print(response.json()["choices"][0]["message"]["content"])
```

### Moonshot（Kimi）

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key="YOUR_MOONSHOT_API_KEY",
)

# Kimi支持超长上下文（200K tokens）
with open("long_document.txt", "r") as f:
    document = f.read()

response = client.chat.completions.create(
    model="moonshot-v1-128k",
    messages=[
        {"role": "system", "content": "你是Kimi，一个有帮助的助手。"},
        {"role": "user", "content": f"总结这篇文档：\n{document}"},
    ],
)
```

### DeepSeek

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key="YOUR_DEEPSEEK_API_KEY",
)

response = client.chat.completions.create(
    model="deepseek-chat",  # 或 deepseek-coder
    messages=[{"role": "user", "content": "Hello!"}],
)

# DeepSeek Coder 代码专用
response = client.chat.completions.create(
    model="deepseek-coder",
    messages=[{
        "role": "user",
        "content": "Write a Python function to merge two sorted lists",
    }],
)
```

---

## API网关

### LiteLLM

### 这玩意儿到底是啥？

LiteLLM是一个Python库，让你用统一的方式调用100+种LLM API。它不仅支持OpenAI兼容格式，还提供了负载均衡、Fallback、成本追踪等企业级功能。

**核心特点：**
- **统一接口**：所有LLM都用OpenAI格式调用
- **负载均衡**：自动在多个提供商之间分配请求
- **Fallback**：一个模型失败自动切换到备用模型
- **成本追踪**：实时追踪每个请求的成本

### 使用方法

```python
from litellm import completion

# 统一调用方式
response = completion(
    model="gpt-4",  # OpenAI
    messages=[{"role": "user", "content": "Hello!"}],
)

response = completion(
    model="claude-3-sonnet-20240229",  # Anthropic
    messages=[{"role": "user", "content": "Hello!"}],
)

response = completion(
    model="ollama/llama3",  # 本地Ollama
    messages=[{"role": "user", "content": "Hello!"}],
)

response = completion(
    model="huggingface/meta-llama/Llama-2-7b-chat-hf",  # HuggingFace
    messages=[{"role": "user", "content": "Hello!"}],
)

# 设置环境变量
import os
os.environ["OPENAI_API_KEY"] = "..."
os.environ["ANTHROPIC_API_KEY"] = "..."
os.environ["HUGGINGFACE_API_KEY"] = "..."
```

### 负载均衡与Fallback

```python
from litellm import completion

# Fallback配置
response = completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    fallbacks=[{"model": "claude-3-sonnet"}, {"model": "gpt-3.5-turbo"}],
)

# 负载均衡
from litellm import Router

router = Router(
    model_list=[
        {"model_name": "gpt-4", "litellm_params": {"model": "gpt-4"}},
        {"model_name": "gpt-4", "litellm_params": {"model": "azure/gpt-4"}},
        {"model_name": "gpt-4", "litellm_params": {"model": "gpt-4-turbo"}},
    ],
    num_retries=3,
    timeout=60,
)

response = router.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### 成本追踪

```python
from litellm import completion, cost_tracking

# 开启成本追踪
with cost_tracking() as tracker:
    response = completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(f"Cost: ${tracker.get_total_cost()}")

# 查看详细成本
print(tracker.get_model_costs())
```

### 推荐论文

1. **LiteLLM Team, 2023** - "LiteLLM: Unified API for LLMs" - 官方文档
2. **Sheng et al., 2023** - "Flexible LLM Routing" - 路由策略
3. **Chen et al., 2023** - "FrugalGPT" - 成本优化

---

## one-api

### 这玩意儿到底是啥？

one-api是一个开源的OpenAI API管理网关，支持多渠道管理、负载均衡、令牌管理等功能。适合企业内部部署，统一管理多个API密钥。

**核心特点：**
- **多渠道管理**：支持OpenAI、Azure、Anthropic等多种渠道
- **令牌管理**：生成和管理API令牌，控制访问权限
- **计费统计**：详细的用量统计和成本分析
- **Docker部署**：一键部署，开箱即用

### Docker部署

```bash
# 使用Docker部署
docker run --name one-api \
    -p 3000:3000 \
    -v /path/to/data:/data \
    -e SESSION_SECRET=your-secret \
    -d justsong/one-api:latest

# 访问管理界面
# http://localhost:3000
# 默认账号：root，密码：123456
```

---

## 对比总结

| 平台 | 模型数量 | 价格 | 中文支持 | 特点 |
|------|----------|------|----------|------|
| OpenRouter | 100+ | 中等 | 一般 | 模型最全，Fallback |
| Together AI | 50+ | 低 | 一般 | 开源模型，速度快 |
| Replicate | 100+ | 中等 | 一般 | 多模态，自定义部署 |
| 智谱AI | 5+ | 中等 | 优秀 | 中文能力强 |
| Moonshot | 3+ | 中等 | 优秀 | 超长上下文 |
| DeepSeek | 5+ | 低 | 优秀 | 代码能力强 |

### 选择建议

```
需要多种模型 → OpenRouter
追求速度和低价 → Together AI
需要多模态 → Replicate
中文场景 → 智谱AI / Moonshot / DeepSeek
代码生成 → DeepSeek Coder
企业内部管理 → one-api + LiteLLM
```

---

> API聚合平台让你不再被单一厂商绑定！OpenRouter模型最全，Together AI最快最便宜，国内平台更懂中文。选择适合自己的平台，灵活切换，降低成本！