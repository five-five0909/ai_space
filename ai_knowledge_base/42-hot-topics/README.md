# 42. 其他热词

> 一句话：AI领域热词层出不穷，Mamba挑战Transformer、长上下文突破100万token、多模态成为标配、推理时计算新范式正在崛起。

---

## State Space Models (SSM)

### 这玩意儿到底是啥？

状态空间模型（SSM）是2023-2024年最火的新架构，代表作品是**Mamba**。核心思想是用线性递归替代二次复杂度的注意力，实现O(n)复杂度的序列建模。

**为什么SSM突然火了？**
- **线性复杂度**：Transformer是O(n²)，SSM是O(n)
- **长序列友好**：百万token不再是梦
- **推理高效**：不像KV Cache那样占内存
- **效果逼近Transformer**：在某些任务上已经持平

**主流SSM架构：**

| 架构 | 时间 | 核心创新 | 复杂度 |
|------|------|----------|--------|
| S4 | 2021 | HiPPO矩阵初始化 | O(n log n) |
| S5 | 2023 | 并行扫描 | O(n) |
| Mamba | 2023 | 选择性机制 | O(n) |
| Mamba-2 | 2024 | SSD对偶性 | O(n) |

**选择建议：**
```
追求效果 → Mamba-2
追求速度 → Mamba
研究学习 → S4/S5
```

详见 [01-mamba](../01-mamba/README.md)

---

## 长上下文技术

### 这玩意儿到底是啥？

长上下文就是让大模型能"记住"更长的对话历史或文档。GPT-4 Turbo支持128K，Claude 3支持200K，Gemini 1.5 Pro支持**100万token**！

**核心挑战：**
- **KV Cache爆炸**：每个token都要缓存，长度翻倍内存翻倍
- **注意力计算**：O(n²)复杂度，长度增加计算量爆炸
- **位置编码**：训练时的长度限制怎么突破

### 主流技术方案

**1. 稀疏注意力（Longformer、BigBird）**

```python
# 滑动窗口 + 全局token
# 复杂度从O(n²)降到O(n)
class SparseAttention(nn.Module):
    def __init__(self, window_size=256, num_global_tokens=1):
        super().__init__()
        self.window_size = window_size
        self.num_global_tokens = num_global_tokens

    def forward(self, x):
        # 局部注意力：每个token只看周围window_size个token
        # 全局注意力：特殊token（如[CLS]）看所有token
        pass
```

**2. 线性注意力（Linear Transformer、RWKV、Mamba）**

```python
# 用核函数近似softmax
# O(n²) → O(n)
def linear_attention(Q, K, V):
    # Q, K, V: (B, L, D)
    # 核函数phi
    Q_prime = elu(Q) + 1
    K_prime = elu(K) + 1
    # 线性复杂度计算
    KV = torch.einsum('bld,ble->bde', K_prime, V)
    out = torch.einsum('bld,bde->ble', Q_prime, KV)
    return out
```

**3. 上下文扩展技术**

| 技术 | 原理 | 训练长度 | 推理长度 |
|------|------|----------|----------|
| ALiBi | 相对位置偏置 | 2K | 任意 |
| RoPE外推 | NTK插值 | 4K | 64K+ |
| YaRN | 改进的RoPE外推 | 4K | 128K+ |
| LongLoRA | Shifted Sparse Attention | 8K | 100K+ |

**4. KV Cache优化**

```python
# PagedAttention (vLLM)
# 把KV Cache分成固定大小的block，按需分配
# 类似操作系统的虚拟内存

# FlashAttention
# 把注意力计算融合，减少HBM访问
# 内存从O(n²)降到O(n)

# MQA/GQA
# 多个Query共享一组KV
# KV Cache减少数倍
```

### 推荐论文

1. **Su et al., 2021** - "RoFormer: Enhanced Transformer with Rotary Position Embedding" - RoPE
2. **Press et al., 2021** - "Train Short, Test Long" - ALiBi
3. **Chen et al., 2023** - "Extending Context Window of LLMs via Positional Interpolation" - 位置插值

---

## 多模态大模型

### 这玩意儿到底是啥？

多模态大模型就是让AI同时理解文字、图片、视频、音频。GPT-4V、Gemini、Claude 3都是多模态的。

**核心架构：**

```
图像 → 视觉编码器(ViT) → 视觉tokens →
                                  → 融合 → 大语言模型 → 输出
文本 → 文本tokenizer → 文本tokens →
```

### 主流架构

**1. 早期融合（LLaVA、MiniGPT-4）**

```python
# 视觉特征直接投影到语言空间
class LlavaModel(nn.Module):
    def __init__(self, vision_encoder, projector, llm):
        super().__init__()
        self.vision_encoder = vision_encoder  # CLIP ViT
        self.projector = nn.Linear(768, 4096)  # 视觉→语言
        self.llm = llm  # Llama/Vicuna

    def forward(self, images, text_tokens):
        # 提取视觉特征
        vision_feats = self.vision_encoder(images)  # (B, N, 768)
        # 投影到语言空间
        vision_tokens = self.projector(vision_feats)  # (B, N, 4096)
        # 与文本拼接
        inputs = torch.cat([vision_tokens, text_tokens], dim=1)
        # 送入LLM
        return self.llm(inputs)
```

**2. 原生多模态（Gemini、GPT-4V）**

```python
# 从头训练多模态模型，视觉和语言端到端联合训练
# 具体架构未公开，但通常涉及：
# - 统一的token表示
# - 跨模态注意力
# - 大规模多模态预训练
```

**3. 多模态对齐**

| 方法 | 描述 | 代表模型 |
|------|------|----------|
| CLIP | 图文对比学习 | CLIP, SigLIP |
| BLIP | 引导式图文对齐 | BLIP-2, InstructBLIP |
| Flamingo | 交叉注意力融合 | Flamingo, IDEFICS |

### 推荐论文

1. **Radford et al., 2021** - "Learning Transferable Visual Models From Natural Language Supervision" - CLIP
2. **Liu et al., 2023** - "Visual Instruction Tuning" - LLaVA
3. **Li et al., 2023** - "BLIP-2: Bootstrapping Language-Image Pre-training" - BLIP-2

---

## 推理时计算

### 这玩意儿到底是啥？

推理时计算（Test-Time Compute）是2024年的新热点：与其训练更大的模型，不如在推理时花更多计算来提升效果。OpenAI的o1就是典型代表。

**核心思想：**
```
传统：训练时堆算力，推理时一次输出
推理时计算：推理时多思考几步，效果更好
```

### 主流方法

**1. 思维链（Chain-of-Thought）**

```python
# 让模型一步步思考
prompt = """
Q: 小明有15个苹果，给了小红3个，又买了5个。现在有多少个？
请一步步思考：
"""

# 模型输出：
# 1. 小明原有15个苹果
# 2. 给了小红3个，剩下15-3=12个
# 3. 又买了5个，现在有12+5=17个
# 答案：17个
```

**2. 自我一致性（Self-Consistency）**

```python
# 多次采样，取多数
def self_consistency(model, prompt, n_samples=10):
    answers = []
    for _ in range(n_samples):
        response = model.generate(prompt, temperature=0.7)
        answer = extract_answer(response)
        answers.append(answer)
    # 投票
    from collections import Counter
    most_common = Counter(answers).most_common(1)[0][0]
    return most_common
```

**3. 树搜索（Tree of Thoughts）**

```python
# 探索多个推理路径，选择最优
class TreeOfThoughts:
    def __init__(self, model, beam_width=3):
        self.model = model
        self.beam_width = beam_width

    def search(self, problem, max_depth=5):
        # BFS搜索推理树
        beam = [{"state": problem, "path": []}]
        for _ in range(max_depth):
            candidates = []
            for node in beam:
                # 生成多个下一步思考
                thoughts = self.model.generate_thoughts(node["state"])
                for thought in thoughts:
                    new_state = f"{node['state']}\n{thought}"
                    score = self.model.evaluate(new_state)
                    candidates.append({
                        "state": new_state,
                        "path": node["path"] + [thought],
                        "score": score
                    })
            # 保留top-k
            beam = sorted(candidates, key=lambda x: x["score"])[:self.beam_width]
        return beam[0]["path"]
```

**4. 最佳N选一（Best-of-N）**

```python
# 生成N个候选，用奖励模型选最好的
def best_of_n(model, reward_model, prompt, n=10):
    candidates = []
    for _ in range(n):
        response = model.generate(prompt, temperature=1.0)
        score = reward_model.score(prompt, response)
        candidates.append((response, score))
    # 选得分最高的
    best = max(candidates, key=lambda x: x[1])
    return best[0]
```

### 推荐论文

1. **Wei et al., 2022** - "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" - CoT
2. **Wang et al., 2022** - "Self-Consistency Improves Chain of Thought Reasoning" - 自我一致性
3. **Yao et al., 2023** - "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" - ToT

---

## 世界模型

### 这玩意儿到底是啥？

世界模型（World Model）是让AI学会理解物理世界的运作规律。比如：如果你把杯子推倒，杯子会掉下去、水会洒出来。这是通往AGI的关键能力。

**核心思想：**
```
世界模型 = 预测下一帧/下一个状态
学会了预测 → 就理解了世界规律
```

### 主流方法

**1. 视频预测（Video Prediction）**

```python
# 预测视频的下一帧
class VideoWorldModel(nn.Module):
    def __init__(self, latent_dim=256):
        super().__init__()
        # 编码器：把帧压缩成latent
        self.encoder = Encoder()
        # 动态模型：预测下一个latent
        self.dynamics = nn.GRU(latent_dim, latent_dim)
        # 解码器：从latent重建帧
        self.decoder = Decoder()

    def forward(self, frames):
        # frames: (B, T, C, H, W)
        latents = [self.encoder(f) for f in frames.unbind(1)]
        # 自回归预测
        predictions = []
        h = torch.zeros(latents[0].shape[0], self.latent_dim)
        for lat in latents[:-1]:
            h = self.dynamics(lat.unsqueeze(1), h)
            pred_frame = self.decoder(h.squeeze(1))
            predictions.append(pred_frame)
        return predictions
```

**2. 世界模型用于RL（Dreamer）**

```python
# 在想象中训练策略
class Dreamer:
    def __init__(self, world_model, policy):
        self.world_model = world_model  # 世界模型
        self.policy = policy  # 策略网络

    def train(self, real_experience):
        # 1. 用真实经验训练世界模型
        self.world_model.train(real_experience)
        # 2. 在想象中训练策略
        imagined_trajectories = self.world_model.imagine(initial_state, horizon=50)
        self.policy.update(imagined_trajectories)
```

**3. Sora**

Sora是OpenAI的视频生成模型，本质上是学习了视觉世界的大模型：
- 用Transformer处理时空patches
- 大规模视频数据训练
- 能生成1分钟连贯视频

### 推荐论文

1. **Ha & Schmidhuber, 2018** - "World Models" - 世界模型开创性工作
2. **Hafner et al., 2020** - "Dream to Control: Learning Behaviors by Latent Imagination" - Dreamer
3. **Brooks et al., 2024** - "Video Generation Models as World Simulators" - Sora技术报告

---

## 开源生态

### 主流开源模型

| 模型 | 参数量 | 特点 | 许可证 |
|------|--------|------|--------|
| Llama 3.1 | 8B/70B/405B | 最强开源模型 | Llama License |
| Qwen 2.5 | 0.5B-72B | 中英双语最强 | Apache 2.0 |
| Mistral | 7B | 小而精 | Apache 2.0 |
| Mixtral | 8x7B/8x22B | MoE架构 | Apache 2.0 |
| DeepSeek V2 | 236B | MoE，极低成本 | MIT |
| Yi | 6B/34B | 零一万物 | Apache 2.0 |
| Gemma 2 | 9B/27B | Google开源 | Gemma License |

### 模型选择建议

```
追求效果 → Llama 3.1 70B / Qwen 2.5 72B
追求速度 → Llama 3.1 8B / Mistral 7B
中文场景 → Qwen 2.5
代码能力 → DeepSeek Coder
低成本部署 → 量化后的7B/8B模型
```

---

## 研究趋势

### 高效大模型

**方向：**
- **量化**：4bit推理，精度损失<2%
- **剪枝**：移除冗余参数
- **蒸馏**：小模型学大模型
- **MoE**：稀疏激活，参数大但计算少

### 边缘AI

**方向：**
- **端侧部署**：手机、IoT设备运行大模型
- **模型压缩**：适配边缘设备的算力
- **NPU加速**：利用专用硬件

### AI安全

**方向：**
- **对齐技术**：RLHF、Constitutional AI
- **红队测试**：发现模型漏洞
- **可解释性**：理解模型决策过程

### 可解释性

**方向：**
- **机械可解释**：理解神经元功能
- **因果分析**：干预实验
- **概念发现**：自动发现模型学到的概念

---

## 热词速查表

| 热词 | 含义 | 相关论文/项目 |
|------|------|---------------|
| RAG | 检索增强生成 | [36-rag-frameworks](../36-rag-frameworks/README.md) |
| LoRA | 低秩适配微调 | [40-training-frameworks](../40-training-frameworks/README.md) |
| MoE | 混合专家 | [23-moe](../23-moe/README.md) |
| KV Cache | 键值缓存 | [22-kv-cache](../22-kv-cache/README.md) |
| FlashAttention | 高效注意力 | [03-attention](../03-attention/README.md) |
| Speculative Decoding | 推测解码 | [26-training-inference](../26-training-inference/README.md) |
| Function Calling | 函数调用 | [29-agent](../29-agent/README.md) |
| Constitutional AI | 宪法AI | [16-rlhf-alignment](../16-rlhf-alignment/README.md) |
| PPO | 近端策略优化 | [16-rlhf-alignment](../16-rlhf-alignment/README.md) |
| DPO | 直接偏好优化 | [16-rlhf-alignment](../16-rlhf-alignment/README.md) |
| Scaling Laws | 缩放定律 | [26-training-inference](../26-training-inference/README.md) |
| Emergent Abilities | 涌现能力 | 大模型特有的能力突现现象 |
| Hallucination | 幻觉 | 模型生成虚假信息 |
| In-context Learning | 上下文学习 | 不更新参数，通过示例学习 |
| Instruction Tuning | 指令微调 | 用指令数据微调模型 |
| RLHF | 人类反馈强化学习 | [16-rlhf-alignment](../16-rlhf-alignment/README.md) |

---

> AI领域日新月异，热词背后是真正的技术创新。Mamba挑战Transformer霸权，长上下文突破百万token，推理时计算开启新范式。保持学习，拥抱变化！