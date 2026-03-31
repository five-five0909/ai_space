# 24. 视觉多模态

> 师弟师妹们好！视觉多模态就是让AI既能看图又能理解文字，像人一样处理多种信息。今天咱们用大白话+公式+代码，彻底搞懂各种视觉多模态方法！

---

## CLIP（对比语言-图像预训练）

### 这玩意儿到底是啥？
CLIP就是同时训练图像编码器和文本编码器，让它们能相互理解。核心思想是：把图像和对应的文字描述映射到同一个向量空间。

### 核心公式推导
**对比学习目标**：
$$
\mathcal{L}_{\text{CLIP}} = -\frac{1}{N} \sum_{i=1}^N \left[ \log \frac{\exp(I_i \cdot T_i / \tau)}{\sum_{j=1}^N \exp(I_i \cdot T_j / \tau)} + \log \frac{\exp(I_i \cdot T_i / \tau)}{\sum_{j=1}^N \exp(I_j \cdot T_i / \tau)} \right]
$$

其中：
- $I_i$ 是第i个图像的编码
- $T_i$ 是第i个文本的编码
- $\tau$ 是温度参数
- 分子是正样本对，分母包含所有样本对

**零样本分类**：
给定新类别名称$\{c_1, c_2, ..., c_k\}$，计算相似度：
$$
p(y=c_j | I) = \frac{\exp(I \cdot T_{c_j} / \tau)}{\sum_{l=1}^k \exp(I \cdot T_{c_l} / \tau)}
$$

**为什么有效？**
- 大规模数据训练（4亿图像-文本对）
- 对比学习让模型学会语义对齐
- 零样本迁移能力强

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

class CLIPWrapper:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
        
    def encode_image(self, images):
        """编码图像"""
        inputs = self.processor(images=images, return_tensors="pt")
        image_features = self.model.get_image_features(**inputs)
        return image_features
    
    def encode_text(self, texts):
        """编码文本"""
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        text_features = self.model.get_text_features(**inputs)
        return text_features
    
    def compute_similarity(self, image_features, text_features):
        """计算相似度"""
        # 归一化特征
        image_features = F.normalize(image_features, dim=-1)
        text_features = F.normalize(text_features, dim=-1)
        
        # 计算余弦相似度
        similarity = torch.matmul(image_features, text_features.t())
        return similarity
    
    def zero_shot_classification(self, images, class_names):
        """零样本分类"""
        image_features = self.encode_image(images)
        text_features = self.encode_text(class_names)
        similarity = self.compute_similarity(image_features, text_features)
        probabilities = F.softmax(similarity * 100, dim=-1)  # 温度=0.01
        return probabilities

# 使用示例
clip = CLIPWrapper()

# 图像和文本编码
images = ["cat.jpg", "dog.jpg"]  # 实际使用PIL.Image对象
texts = ["a photo of a cat", "a photo of a dog"]

image_features = clip.encode_image(images)
text_features = clip.encode_text(texts)

print(f"Image features shape: {image_features.shape}")
print(f"Text features shape: {text_features.shape}")

# 相似度计算
similarity = clip.compute_similarity(image_features, text_features)
print(f"Similarity matrix:\n{similarity}")

# 零样本分类
class_names = ["cat", "dog", "bird", "car"]
probabilities = clip.zero_shot_classification(images, class_names)
predicted_class = torch.argmax(probabilities, dim=-1)
print(f"Predicted classes: {predicted_class}")
```

### 推荐论文
1. Radford et al., "Learning Transferable Visual Models From Natural Language Supervision", ICML 2021
2. Jia et al., "Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision", ICML 2021
3. Li et al., "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation", ICML 2022

---

## BLIP（自举语言-图像预训练）

### 这玩意儿到底是啥？
BLIP是CLIP的改进版！它不仅能理解图像和文本的关系，还能生成文本描述。核心思想是用噪声文本进行自举学习，提升模型能力。

### 核心公式推导
**三阶段训练**：
1. **Captioner**：生成图像描述
   $$p(T|I) = \prod_{i=1}^{|T|} p(t_i | I, t_{<i})$$
   
2. **Filter**：过滤低质量描述
   $$\text{score}(T, I) = \text{CLIP}(I, T)$$
   
3. **Retrieval**：检索相关文本
   $$p(T|I) = \frac{\exp(\text{sim}(I, T)/\tau)}{\sum_{T' \in \mathcal{D}} \exp(\text{sim}(I, T')/\tau)}$$

**架构设计**：
- 共享视觉编码器
- 双解码器：一个用于理解，一个用于生成
- 跨模态注意力机制

### PyTorch代码示例
```python
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

class BLIPWrapper:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        self.model.eval()
        
    def generate_caption(self, images, max_length=20):
        """生成图像描述"""
        inputs = self.processor(images=images, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            early_stopping=True
        )
        captions = self.processor.batch_decode(outputs, skip_special_tokens=True)
        return captions
    
    def conditional_captioning(self, images, prompts, max_length=20):
        """条件生成（回答问题）"""
        inputs = self.processor(images=images, text=prompts, return_tensors="pt", padding=True)
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4
        )
        answers = self.processor.batch_decode(outputs, skip_special_tokens=True)
        return answers
    
    def image_text_matching(self, images, texts):
        """图像-文本匹配分数"""
        inputs = self.processor(images=images, text=texts, return_tensors="pt", padding=True)
        outputs = self.model(**inputs, labels=inputs["input_ids"])
        # 使用损失作为匹配分数（越小越好）
        match_scores = -outputs.loss
        return match_scores

# 使用示例
blip = BLIPWrapper()

# 图像描述生成
images = ["cat.jpg", "dog.jpg"]  # 实际使用PIL.Image对象
captions = blip.generate_caption(images)
print(f"Generated captions: {captions}")

# 视觉问答
questions = ["What is in the image?", "What color is the animal?"]
answers = blip.conditional_captioning(images, questions)
print(f"Answers: {answers}")

# 图像-文本匹配
texts = ["a black cat", "a white dog"]
match_scores = blip.image_text_matching(images, texts)
print(f"Match scores: {match_scores}")
```

### 推荐论文
1. Li et al., "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation", ICML 2022
2. Li et al., "BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models", ICML 2023
3. Alayrac et al., "Flamingo: A Visual Language Model for Few-Shot Learning", NeurIPS 2022

---

## LLaVA（大型语言和视觉助手）

### 这玩意儿到底是啥？
LLaVA就是把视觉编码器和大型语言模型连接起来！它先用CLIP编码图像，然后把图像特征注入到LLM中，让LLM能"看到"图像。

### 核心公式推导
**特征投影**：
$$
V_{\text{projected}} = W_p \cdot V_{\text{CLIP}}
$$

其中$W_p$是可学习的投影矩阵，将CLIP的视觉特征映射到LLM的词嵌入空间。

**多模态输入**：
$$
X = [\text{tokenize}("USER: <image>"), V_{\text{projected}}, \text{tokenize}("\nWhat is this?\nASSISTANT:")]
$$

**训练目标**：
$$
\mathcal{L} = -\sum_{i \in \text{response}} \log P(x_i | X_{<i})
$$

**两阶段训练**：
1. **投影层预训练**：只训练投影层$W_p$
2. **端到端微调**：训练整个模型（包括LLM）

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM, CLIPVisionModel

class LLaVA(nn.Module):
    def __init__(self, llm_name="meta-llama/Llama-2-7b-hf", vision_model_name="openai/clip-vit-large-patch14"):
        super().__init__()
        # 视觉编码器（冻结）
        self.vision_encoder = CLIPVisionModel.from_pretrained(vision_model_name)
        for param in self.vision_encoder.parameters():
            param.requires_grad = False
            
        # 大型语言模型
        self.llm = AutoModelForCausalLM.from_pretrained(llm_name)
        self.tokenizer = AutoTokenizer.from_pretrained(llm_name)
        
        # 视觉投影层
        self.visual_projection = nn.Linear(
            self.vision_encoder.config.hidden_size,
            self.llm.config.hidden_size
        )
        
        # 特殊token
        self.image_token_id = self.tokenizer.convert_tokens_to_ids("<image>")
        
    def encode_image(self, images):
        """编码图像"""
        with torch.no_grad():
            vision_outputs = self.vision_encoder(pixel_values=images)
            image_features = vision_outputs.last_hidden_state  # [batch, num_patches, vision_dim]
            
        # 投影到LLM空间
        projected_features = self.visual_projection(image_features)  # [batch, num_patches, llm_dim]
        return projected_features
    
    def forward(self, input_ids, images=None, attention_mask=None, labels=None):
        batch_size = input_ids.size(0)
        
        # 获取文本嵌入
        inputs_embeds = self.llm.get_input_embeddings()(input_ids)
        
        if images is not None:
            # 编码图像
            image_features = self.encode_image(images)  # [batch, num_patches, llm_dim]
            
            # 找到<image> token的位置并替换
            image_token_mask = (input_ids == self.image_token_id)
            inputs_embeds[image_token_mask] = image_features.view(-1, image_features.size(-1))
            
        # LLM前向传播
        outputs = self.llm(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            labels=labels
        )
        return outputs

# 使用示例（简化版）
def create_llava_input(tokenizer, image_features, prompt):
    """创建LLaVA输入"""
    # Tokenize prompt
    prompt_tokens = tokenizer(prompt, return_tensors="pt")
    input_ids = prompt_tokens.input_ids
    
    # 找到<image>位置并插入图像特征
    image_token_id = tokenizer.convert_tokens_to_ids("<image>")
    image_positions = (input_ids == image_token_id).nonzero(as_tuple=True)[1]
    
    return input_ids, image_positions

# 注意：实际使用需要复杂的输入处理和训练流程
# 这里只是概念演示
```

### 推荐论文
1. Liu et al., "Visual Instruction Tuning", NeurIPS 2023
2. Liu et al., "LLaVA-1.5: Improved Baselines with Visual Instruction Tuning", arXiv 2023
3. Zhu et al., "MiniGPT-4: Enhancing Vision-language Understanding with Advanced Large Language Models", CVPR 2023

---

## Flamingo（火烈鸟模型）

### 这玩意儿到底是啥？
Flamingo是DeepMind提出的少样本视觉语言模型！它能在看到几个例子后就学会新任务，就像人类一样。

### 核心公式推导
**交叉注意力机制**：
在LLM的每一层都插入视觉交叉注意力：
$$
\text{CrossAttn}(Q_{\text{LLM}}, K_{\text{vision}}, V_{\text{vision}}) = \text{softmax}\left(\frac{Q_{\text{LLM}} K_{\text{vision}}^T}{\sqrt{d}}\right) V_{\text{vision}}
$$

**Perceiver Resampler**：
将大量视觉token压缩成固定数量的查询：
$$
Q_{\text{perceiver}} = \text{MLP}(\text{learnable queries})
$$
$$
Z = \text{CrossAttn}(Q_{\text{perceiver}}, K_{\text{vision}}, V_{\text{vision}})
$$

**上下文学习**：
给定示例$(I_1, T_1), (I_2, T_2), ..., (I_k, T_k)$和查询$I_q$，预测$T_q$：
$$
P(T_q | I_q, \{(I_i, T_i)\}_{i=1}^k) = \prod_{j=1}^{|T_q|} P(t_{q,j} | I_q, \{(I_i, T_i)\}_{i=1}^k, t_{q,<j})
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class PerceiverResampler(nn.Module):
    def __init__(self, input_dim, output_dim, num_latents=64, num_layers=3):
        super().__init__()
        self.num_latents = num_latents
        self.latents = nn.Parameter(torch.randn(num_latents, input_dim))
        self.layers = nn.ModuleList([
            nn.TransformerDecoderLayer(
                d_model=input_dim,
                nhead=8,
                dim_feedforward=input_dim * 4
            ) for _ in range(num_layers)
        ])
        self.output_proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x):
        # x: [batch, seq_len, input_dim]
        batch_size = x.size(0)
        latents = self.latents.unsqueeze(0).expand(batch_size, -1, -1)
        
        # Perceiver cross-attention
        for layer in self.layers:
            latents = layer(latents, x)
            
        return self.output_proj(latents)  # [batch, num_latents, output_dim]

class FlamingoLayer(nn.Module):
    def __init__(self, llm_hidden_dim, vision_hidden_dim):
        super().__init__()
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=llm_hidden_dim,
            kdim=vision_hidden_dim,
            vdim=vision_hidden_dim,
            num_heads=8,
            batch_first=True
        )
        self.norm = nn.LayerNorm(llm_hidden_dim)
        
    def forward(self, llm_hidden, vision_features):
        # llm_hidden: [batch, seq_len, llm_hidden_dim]
        # vision_features: [batch, num_vision_tokens, vision_hidden_dim]
        cross_attn_output, _ = self.cross_attn(
            query=llm_hidden,
            key=vision_features,
            value=vision_features
        )
        return self.norm(llm_hidden + cross_attn_output)

class Flamingo(nn.Module):
    def __init__(self, llm_name="facebook/opt-1.3b", vision_model_name="openai/clip-vit-large-patch14"):
        super().__init__()
        # 视觉编码器
        self.vision_encoder = AutoModel.from_pretrained(vision_model_name)
        for param in self.vision_encoder.parameters():
            param.requires_grad = False
            
        # Perceiver Resampler
        self.perceiver = PerceiverResampler(
            input_dim=self.vision_encoder.config.hidden_size,
            output_dim=768,  # OPT hidden dim
            num_latents=64
        )
        
        # LLM with cross-attention layers
        self.llm = AutoModel.from_pretrained(llm_name)
        self.flamingo_layers = nn.ModuleList([
            FlamingoLayer(768, 768) for _ in range(len(self.llm.decoder.layers))
        ])
        
        self.tokenizer = AutoTokenizer.from_pretrained(llm_name)
        
    def forward(self, input_ids, images, attention_mask=None):
        # 编码图像
        with torch.no_grad():
            vision_outputs = self.vision_encoder(pixel_values=images)
            vision_features = vision_outputs.last_hidden_state
            
        # Perceiver resampling
        vision_latents = self.perceiver(vision_features)  # [batch, 64, 768]
        
        # LLM前向传播 with cross-attention
        llm_outputs = self.llm(input_ids, output_hidden_states=True)
        hidden_states = llm_outputs.hidden_states
        
        # Apply Flamingo layers
        for i, flamingo_layer in enumerate(self.flamingo_layers):
            hidden_states[i+1] = flamingo_layer(hidden_states[i+1], vision_latents)
            
        return hidden_states[-1]

# 使用示例（概念演示）
flamingo = Flamingo()
input_ids = torch.randint(0, 50000, (2, 100))
images = torch.randn(2, 3, 224, 224)

output = flamingo(input_ids, images)
print(f"Flamingo output shape: {output.shape}")
```

### 推荐论文
1. Alayrac et al., "Flamingo: A Visual Language Model for Few-Shot Learning", NeurIPS 2022
2. Datasets: "M3IT: A Multimodal Multilingual Instruction-Tuning Dataset", EMNLP 2023
3. Awadalla et al., "OpenFlamingo: An Open-Source Framework for Training Large Autoregressive Vision-Language Models", arXiv 2023

---
> 视觉多模态让AI更智能！CLIP实现图文对齐，BLIP支持理解和生成，LLaVA连接视觉和语言模型，Flamingo实现少样本学习。记住：好的多模态模型需要强大的视觉编码器、语言模型和有效的融合机制！