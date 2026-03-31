# 40. 训练框架

> 一句话：训练框架让大模型训练变得高效可行，DeepSpeed显存优化最强、LLaMA-Factory微调最方便、Unsloth速度最快。

---

## DeepSpeed

### 这玩意儿到底是啥？

DeepSpeed是微软开源的深度学习优化库，专门为大模型训练设计。它的核心创新是**ZeRO（Zero Redundancy Optimizer）技术**，可以把显存占用降低到原来的1/N，让普通显卡也能训练大模型。

**为什么DeepSpeed是训练标配？**
- **显存优化**：ZeRO技术，显存占用降低8-64倍
- **训练速度**：流水线并行、张量并行
- **大模型支持**：支持千亿参数模型训练
- **易用性**：与PyTorch、HuggingFace无缝集成

### ZeRO技术详解

ZeRO通过消除数据并行中的冗余来节省显存：

```
传统数据并行：
GPU 0: 模型参数 + 梯度 + 优化器状态
GPU 1: 模型参数 + 梯度 + 优化器状态（完全相同！）
GPU 2: 模型参数 + 梯度 + 优化器状态（完全相同！）
问题：大量冗余，显存浪费严重

ZeRO优化策略：
ZeRO-1: 分片优化器状态（显存降低4x）
ZeRO-2: 分片优化器状态 + 梯度（显存降低8x）
ZeRO-3: 分片优化器状态 + 梯度 + 模型参数（显存降低N倍）
```

**显存占用公式：**
$$
\text{Memory}_{\text{ZeRO-3}} = \frac{2\psi + 2\psi + K\psi}{N_d}
$$

其中 $\psi$ 是模型参数量，$K$ 是优化器状态系数（Adam约12），$N_d$ 是GPU数量。

### 安装与使用

```bash
# 安装
pip install deepspeed

# 使用DeepSpeed启动训练
deepspeed --num_gpus=4 train.py --deepspeed ds_config.json
```

### 配置文件

```json
// ds_config.json
{
    "train_batch_size": 64,
    "gradient_accumulation_steps": 4,
    "optimizer": {
        "type": "AdamW",
        "params": {
            "lr": 1e-5,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay": 0.01
        }
    },
    "scheduler": {
        "type": "WarmupLR",
        "params": {
            "warmup_min_lr": 0,
            "warmup_max_lr": 1e-5,
            "warmup_num_steps": 1000
        }
    },
    "fp16": {
        "enabled": true,
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        },
        "overlap_comm": true,
        "contiguous_gradients": true,
        "reduce_bucket_size": 5e8,
        "stage3_prefetch_bucket_size": 5e7,
        "stage3_param_persistence_threshold": 1e5
    },
    "gradient_clipping": 1.0,
    "steps_per_print": 100
}
```

### 与HuggingFace集成

```python
from transformers import Trainer, TrainingArguments, AutoModelForCausalLM

# 加载模型
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# 训练参数
training_args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=1e-5,
    fp16=True,
    deepspeed="ds_config.json",  # DeepSpeed配置
)

# 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train()
```

### 推荐论文

1. **Rajbhandari et al., 2020** - "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" - ZeRO原论文
2. **Ren et al., 2021** - "ZeRO-Offload: Democratizing Billion-Scale Model Training" - ZeRO-Offload
3. **Microsoft, 2020** - "DeepSpeed: System Optimizations Enable Training Deep Learning Models with Over 100 Billion Parameters"

---

## Megatron-LM

### 这玩意儿到底是啥？

Megatron-LM是NVIDIA开源的大规模Transformer训练框架，专门针对NVIDIA GPU优化。它实现了**张量并行（Tensor Parallelism）**和**流水线并行（Pipeline Parallelism）**，是训练超大规模模型的首选。

**核心特点：**
- **张量并行**：单层内切分，高效利用多GPU
- **流水线并行**：层间切分，突破显存限制
- **混合精度**：FP16/BF16训练，速度翻倍
- **FlashAttention**：集成高效注意力

### 张量并行原理

```
传统计算：Y = XW，单GPU完成
张量并行：Y = X[W1|W2] = [XW1 | XW2]，多GPU并行计算

对于Transformer：
- QKV投影：按头切分
- FFN：按列切分第一层，按行切分第二层
- 层归一化：不切分
```

### 使用方法

```bash
# 克隆仓库
git clone https://github.com/NVIDIA/Megatron-LM
cd Megatron-LM

# 预训练GPT
python pretrain_gpt.py \
    --num-layers 24 \
    --hidden-size 1024 \
    --num-attention-heads 16 \
    --micro-batch-size 4 \
    --global-batch-size 256 \
    --seq-length 1024 \
    --max-position-embeddings 1024 \
    --train-samples 1000000 \
    --lr 1e-4 \
    --tensor-model-parallel-size 4 \
    --pipeline-model-parallel-size 2 \
    --fp16
```

### 与DeepSpeed结合

```python
# Megatron-DeepSpeed结合
# 可以同时使用张量并行和ZeRO优化

deepspeed pretrain_gpt.py \
    --tensor-model-parallel-size 4 \
    --deepspeed_config ds_config.json
```

### 推荐论文

1. **Shoeybi et al., 2019** - "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism" - Megatron原论文
2. **Narayanan et al., 2021** - "Efficient Large-Scale Language Model Training on GPU Clusters" - Megatron扩展
3. **Korthikanti et al., 2022** - "Reducing Activation Recomputation in Large Transformer Models" - 激活重计算

---

## LLaMA-Factory

### 这玩意儿到底是啥？

LLaMA-Factory是一个统一的大模型微调平台，支持多种模型、多种微调方法、多种训练技术。它把复杂的微调流程封装成简单的Web界面和命令行工具，让微调变得**像搭积木一样简单**。

**核心特点：**
- **模型支持广**：Llama、Qwen、ChatGLM、Baichuan等50+模型
- **微调方法全**：全参数、LoRA、QLoRA、Prefix Tuning等
- **训练技术多**：DeepSpeed、FSDP、量化训练
- **Web界面**：可视化配置，实时监控

### 安装与使用

```bash
# 安装
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"

# Web界面启动
python src/train_web.py

# 命令行微调
llamafactory-cli train config.yaml
```

### 配置文件示例

```yaml
# config.yaml
model_name_or_path: meta-llama/Llama-2-7b-hf
stage: sft
do_train: true
finetuning_type: lora
lora_target: all

# 数据配置
dataset: identity,alpaca
template: llama2
cutoff_len: 1024
max_samples: 10000
overwrite_cache: true
preprocessing_num_workers: 16

# 训练配置
output_dir: saves/llama2-7b/lora/sft
logging_steps: 10
save_steps: 500
plot_loss: true
overwrite_output_dir: true

# 超参数
per_device_train_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 5.0e-5
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true

# LoRA配置
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.05

# 评估
val_size: 0.1
per_device_eval_batch_size: 1
eval_strategy: steps
eval_steps: 500
```

### Python API

```python
from llamafactory.train.tuner import run_exp

args = {
    "model_name_or_path": "meta-llama/Llama-2-7b-hf",
    "stage": "sft",
    "do_train": True,
    "finetuning_type": "lora",
    "dataset": "alpaca",
    "output_dir": "./output",
    "per_device_train_batch_size": 4,
    "num_train_epochs": 3,
    "learning_rate": 5e-5,
}
run_exp(args)
```

### 推荐论文

1. **LLaMA-Factory Team, 2024** - "LLaMA-Factory: Unified Efficient Fine-Tuning of 100+ Language Models" - 官方论文
2. **Hu et al., 2021** - "LoRA: Low-Rank Adaptation of Large Language Models" - LoRA
3. **Dettmers et al., 2023** - "QLoRA: Efficient Finetuning of Quantized LLMs" - QLoRA

---

## Unsloth

### 这玩意儿到底是啥？

Unsloth是一个专门优化Llama、Mistral系列模型微调速度的框架。它的核心创新是**手写CUDA内核**，让微调速度提升2-5倍，显存占用减少50%。

**核心特点：**
- **速度快**：比HuggingFace快2-5倍
- **显存省**：减少50%显存占用
- **支持广**：Llama、Mistral、Gemma、Qwen等
- **易用**：与HuggingFace完全兼容

### 安装与使用

```bash
# 安装
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps trl peft accelerate bitsandbytes
```

### 代码示例

```python
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# 加载模型（4bit量化）
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,  # 自动检测
    load_in_4bit=True,  # 4bit量化加载
)

# 添加LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# 加载数据集
dataset = load_dataset("yahma/alpaca-cleaned", split="train")

# 训练参数
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    max_steps=60,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    output_dir="outputs",
)

# 训练
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=training_args,
)
trainer.train()

# 保存模型
model.save_pretrained_ggml("llama-2-7b-finetuned", tokenizer)
```

### 推荐论文

1. **Unsloth Team, 2024** - "Unsloth: Fast & Memory Efficient LLM Finetuning" - 官方文档
2. **Dettmers et al., 2023** - "QLoRA: Efficient Finetuning of Quantized LLMs" - 量化微调
3. **Hu et al., 2021** - "LoRA: Low-Rank Adaptation of Large Language Models" - LoRA

---

## FSDP（Fully Sharded Data Parallel）

### 这玩意儿到底是啥？

FSDP是PyTorch原生支持的分片数据并行技术，与DeepSpeed ZeRO-3类似。它的优势是**无需额外依赖**，PyTorch原生支持。

**核心特点：**
- **PyTorch原生**：无需安装额外库
- **ZeRO-3类似**：分片参数、梯度、优化器状态
- **CPU Offload**：支持卸载到CPU
- **易用性**：简单的配置即可启用

### 使用方法

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, CPUOffload
from transformers import AutoModelForCausalLM

# 初始化分布式
import torch.distributed as dist
dist.init_process_group(backend="nccl")

# 加载模型
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# FSDP包装
model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # 类似ZeRO-3
    cpu_offload=CPUOffload(offload_params=True),
    device_id=torch.cuda.current_device(),
)

# 训练
for batch in dataloader:
    loss = model(**batch).loss
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

### 与HuggingFace集成

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./output",
    fsdp="full_shard auto_wrap",
    fsdp_config={
        "fsdp_auto_wrap_policy": "TRANSFORMER_BASED_WRAP",
        "fsdp_sharding_strategy": "FULL_SHARD",
        "fsdp_cpu_ram_efficient_loading": True,
    },
)
```

---

## Axolotl

### 这玩意儿到底是啥？

Axolotl是一个简化大模型微调的工具，通过YAML配置文件定义训练参数，支持各种微调方法和训练技术。

**核心特点：**
- **配置驱动**：YAML配置，无需写代码
- **方法全面**：LoRA、QLoRA、全参数等
- **数据处理**：自动处理各种数据格式
- **集成丰富**：DeepSpeed、FSDP、Unsloth

### 配置示例

```yaml
# axolotl config.yaml
base_model: meta-llama/Llama-2-7b-hf
model_type: LlamaForCausalLM
tokenizer_type: LlamaTokenizer

load_in_8bit: true
adapter: lora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05

datasets:
  - path: yahma/alpaca-cleaned
    type: alpaca

output_dir: ./output
sequence_len: 2048
sample_packing: true

gradient_accumulation_steps: 4
micro_batch_size: 4
num_epochs: 3
learning_rate: 2e-4

bf16: true
flash_attention: true

deepspeed: ds_config.json
```

---

## 对比总结

| 框架 | 核心优势 | 显存优化 | 易用性 | 适用场景 |
|------|----------|----------|--------|----------|
| DeepSpeed | ZeRO显存优化 | ★★★★★ | ★★★☆☆ | 大规模分布式训练 |
| Megatron-LM | 张量/流水线并行 | ★★★★☆ | ★★☆☆☆ | 超大模型预训练 |
| LLaMA-Factory | 统一微调平台 | ★★★★☆ | ★★★★★ | 模型微调 |
| Unsloth | 速度最快 | ★★★★★ | ★★★★☆ | 快速微调 |
| FSDP | PyTorch原生 | ★★★★☆ | ★★★★☆ | 标准分布式训练 |
| Axolotl | 配置驱动 | ★★★☆☆ | ★★★★★ | 简单微调 |

### 选择建议

```
预训练大模型 → DeepSpeed + Megatron-LM
模型微调 → LLaMA-Factory 或 Unsloth
追求速度 → Unsloth
追求显存效率 → DeepSpeed ZeRO-3
PyTorch原生 → FSDP
快速实验 → Axolotl
```

---

> 训练框架是大模型落地的基石！DeepSpeed让普通显卡也能训练大模型，LLaMA-Factory让微调变得简单，Unsloth让训练速度飞起来。选对工具，事半功倍！