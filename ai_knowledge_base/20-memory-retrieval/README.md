# 20. 记忆与检索

> 师弟师妹们好！记忆与检索就是让大模型能"记住"和"查找"信息，不再局限于训练时学到的知识。今天咱们用大白话+公式+代码，彻底搞懂各种记忆检索方法！

---

## Vector Database Retrieval

### 这玩意儿到底是啥？
向量数据库检索就是把文本变成向量存起来，查询时也变成向量，然后找最相似的向量。就像图书馆的图书分类系统一样。

### 核心公式推导
**向量化**：
$$
v = \text{Encoder}(text)
$$

**相似度计算**（余弦相似度）：
$$
\text{sim}(q, d) = \frac{q \cdot d}{\|q\| \|d\|}
$$

**最近邻搜索**：
$$
\text{top-k} = \arg\max_{d_i \in D} \text{sim}(q, d_i)
$$

**为什么用向量？**
- 向量能捕捉语义信息
- 相似语义的文本有相似向量
- 可以用高效的近似最近邻算法

### PyTorch代码示例
```python
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorDatabase:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        
    def add_documents(self, documents):
        """添加文档到数据库"""
        self.documents.extend(documents)
        
        # 编码文档
        embeddings = self.encoder.encode(documents)
        
        # 创建FAISS索引
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # 内积（余弦相似度）
        faiss.normalize_L2(embeddings)  # 归一化用于余弦相似度
        self.index.add(embeddings.astype('float32'))
        
    def search(self, query, k=5):
        """搜索最相关的文档"""
        # 编码查询
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # 搜索
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # 返回结果
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'document': self.documents[idx],
                'score': distances[0][i],
                'index': idx
            })
        return results

# 使用示例
db = VectorDatabase()
documents = [
    "机器学习是人工智能的一个分支",
    "深度学习使用神经网络进行学习",
    "自然语言处理处理人类语言",
    "计算机视觉处理图像和视频"
]
db.add_documents(documents)

results = db.search("什么是AI?", k=2)
for result in results:
    print(f"Score: {result['score']:.4f}, Document: {result['document']}")
```

### 推荐论文
1. Johnson et al., "Billion-scale similarity search with GPUs", IEEE Transactions on Big Data 2019
2. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020
3. Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering", EMNLP 2020

---

## Memory Networks

### 这玩意儿到底是啥？
记忆网络就是给神经网络加一个外部记忆模块，让它能读写记忆。就像人脑有短期记忆和长期记忆一样。

### 核心公式推导
**记忆读取**：
$$
o = \sum_{i=1}^M p_i m_i
$$

其中：
- $m_i$ 是第i个记忆槽的内容
- $p_i$ 是注意力权重：$p_i = \text{softmax}(q \cdot m_i)$
- $q$ 是查询向量

**记忆更新**：
$$
m_i^{new} = m_i^{old} + \alpha \cdot (x - m_i^{old})
$$

其中$x$是新输入，$\alpha$是学习率。

**端到端训练**：
整个系统（包括记忆模块）都可以通过梯度下降训练。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MemoryNetwork(nn.Module):
    def __init__(self, memory_size=100, memory_dim=256):
        super().__init__()
        self.memory_size = memory_size
        self.memory_dim = memory_dim
        
        # 初始化记忆矩阵
        self.memory = nn.Parameter(torch.randn(memory_size, memory_dim))
        
        # 查询网络
        self.query_net = nn.Linear(768, memory_dim)  # 假设输入维度768
        
        # 输出网络
        self.output_net = nn.Linear(memory_dim, 768)
        
    def read(self, query):
        """从记忆中读取信息"""
        # 计算注意力权重
        attention = torch.matmul(query, self.memory.t())  # [batch, memory_size]
        attention = F.softmax(attention, dim=1)
        
        # 加权求和
        output = torch.matmul(attention, self.memory)  # [batch, memory_dim]
        return output, attention
    
    def write(self, input_vector, attention):
        """写入记忆"""
        # 外积更新
        update = torch.bmm(input_vector.unsqueeze(2), attention.unsqueeze(1))  # [batch, memory_dim, memory_size]
        update = update.sum(dim=0).t()  # [memory_size, memory_dim]
        
        # 更新记忆（简化版）
        self.memory.data = self.memory.data + 0.1 * update
        
    def forward(self, x):
        """前向传播"""
        # 生成查询
        query = self.query_net(x)  # [batch, memory_dim]
        
        # 读取记忆
        memory_output, attention = self.read(query)
        
        # 生成最终输出
        output = self.output_net(memory_output)
        
        # 写入记忆（可选）
        if self.training:
            self.write(query, attention)
            
        return output

# 使用示例
model = MemoryNetwork(memory_size=50, memory_dim=128)
input_data = torch.randn(32, 768)  # batch_size=32, input_dim=768
output = model(input_data)
print(f"Output shape: {output.shape}")
```

### 推荐论文
1. Weston et al., "Memory Networks", ICLR 2015
2. Sukhbaatar et al., "End-To-End Memory Networks", NeurIPS 2015
3. Graves et al., "Hybrid computing using a neural network with dynamic external memory", Nature 2016

---

## Differentiable Neural Computer (DNC)

### 这玩意儿到底是啥？
DNC是记忆网络的升级版！它不仅有记忆矩阵，还有复杂的读写头，能执行更复杂的记忆操作，比如分配、排序、递归等。

### 核心公式推导
**内容寻址**：
$$
K_t(i, j) = \frac{\cos(\mathbf{k}_t(i), \mathbf{M}_t(j))}{\tau}
$$

**位置寻址**：
$$
\mathbf{w}_t^{g} = g_t \mathbf{w}_t^c + (1 - g_t) \mathbf{w}_{t-1}
$$

**内存分配**：
$$
a_t(j) = \prod_{i=1}^{R} (1 - w_t^r(i, j)) \cdot \prod_{i=1}^{W} (1 - w_t^w(i, j))
$$

其中：
- $\mathbf{k}_t$ 是键向量
- $\mathbf{M}_t$ 是记忆矩阵
- $g_t$ 是插值门
- $\mathbf{w}_t^c$ 是内容权重
- $a_t$ 是可用性向量

**读写操作**：
- 读头：$\mathbf{r}_t = \mathbf{M}_t \mathbf{w}_t^r$
- 写头：$\mathbf{M}_t = \mathbf{M}_{t-1} - \mathbf{w}_t^w \mathbf{e}_t^T + \mathbf{w}_t^w \mathbf{a}_t^T$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class DNC(nn.Module):
    def __init__(self, input_size, hidden_size, memory_size, memory_dim, num_read_heads=1, num_write_heads=1):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.memory_size = memory_size
        self.memory_dim = memory_dim
        self.num_read_heads = num_read_heads
        self.num_write_heads = num_write_heads
        
        # 控制器网络
        self.controller = nn.LSTMCell(input_size + num_read_heads * memory_dim, hidden_size)
        
        # 读写头参数
        controller_output_size = hidden_size
        
        # 读头参数
        self.read_keys = nn.Linear(controller_output_size, num_read_heads * memory_dim)
        self.read_strengths = nn.Linear(controller_output_size, num_read_heads)
        self.read_modes = nn.Linear(controller_output_size, num_read_heads * 3)
        
        # 写头参数
        self.write_key = nn.Linear(controller_output_size, memory_dim)
        self.write_strength = nn.Linear(controller_output_size, 1)
        self.erase_vector = nn.Linear(controller_output_size, memory_dim)
        self.write_vector = nn.Linear(controller_output_size, memory_dim)
        self.free_gates = nn.Linear(controller_output_size, num_read_heads)
        self.allocation_gate = nn.Linear(controller_output_size, 1)
        self.write_gate = nn.Linear(controller_output_size, 1)
        
        # 输出层
        self.output_layer = nn.Linear(hidden_size + num_read_heads * memory_dim, input_size)
        
        # 初始化记忆
        self.memory_bias = nn.Parameter(torch.randn(memory_size, memory_dim))
        
    def content_weighting(self, keys, strengths, memory):
        """内容寻址"""
        # keys: [batch, num_heads, memory_dim]
        # memory: [batch, memory_size, memory_dim]
        cosine_similarity = torch.matmul(keys, memory.transpose(-2, -1))  # [batch, num_heads, memory_size]
        weights = F.softmax(cosine_similarity * strengths.unsqueeze(-1), dim=-1)
        return weights
        
    def forward(self, x, prev_state=None):
        batch_size = x.size(0)
        
        if prev_state is None:
            # 初始化状态
            controller_hidden = torch.zeros(batch_size, self.hidden_size).to(x.device)
            controller_cell = torch.zeros(batch_size, self.hidden_size).to(x.device)
            memory = self.memory_bias.unsqueeze(0).expand(batch_size, -1, -1)
            read_weights = torch.zeros(batch_size, self.num_read_heads, self.memory_size).to(x.device)
            write_weights = torch.zeros(batch_size, self.num_write_heads, self.memory_size).to(x.device)
            usage = torch.zeros(batch_size, self.memory_size).to(x.device)
        else:
            controller_hidden, controller_cell, memory, read_weights, write_weights, usage = prev_state
            
        # 控制器输入：原始输入 + 之前读取的内容
        read_vectors = torch.matmul(read_weights, memory)  # [batch, num_heads, memory_dim]
        read_vectors_flat = read_vectors.view(batch_size, -1)
        controller_input = torch.cat([x, read_vectors_flat], dim=1)
        
        # 控制器前向传播
        controller_hidden, controller_cell = self.controller(controller_input, (controller_hidden, controller_cell))
        
        # 生成读写参数
        read_keys = self.read_keys(controller_hidden).view(batch_size, self.num_read_heads, self.memory_dim)
        read_strengths = F.softplus(self.read_strengths(controller_hidden)) + 1
        read_modes = F.softmax(self.read_modes(controller_hidden).view(batch_size, self.num_read_heads, 3), dim=-1)
        
        write_key = self.write_key(controller_hidden).unsqueeze(1)
        write_strength = F.softplus(self.write_strength(controller_hidden)) + 1
        erase_vector = F.sigmoid(self.erase_vector(controller_hidden))
        write_vector = self.write_vector(controller_hidden)
        free_gates = F.sigmoid(self.free_gates(controller_hidden))
        allocation_gate = F.sigmoid(self.allocation_gate(controller_hidden))
        write_gate = F.sigmoid(self.write_gate(controller_hidden))
        
        # 内容寻址
        read_content_weights = self.content_weighting(read_keys, read_strengths, memory)
        write_content_weights = self.content_weighting(write_key, write_strength, memory).squeeze(1)
        
        # 简化的DNC实现（省略位置寻址和内存分配）
        new_read_weights = read_content_weights
        new_write_weights = write_content_weights.unsqueeze(1)
        
        # 写入记忆
        erase_matrix = torch.bmm(new_write_weights.transpose(-2, -1), erase_vector.unsqueeze(1))
        add_matrix = torch.bmm(new_write_weights.transpose(-2, -1), write_vector.unsqueeze(1))
        memory = memory * (1 - erase_matrix) + add_matrix
        
        # 读取记忆
        new_read_vectors = torch.matmul(new_read_weights, memory)
        new_read_vectors_flat = new_read_vectors.view(batch_size, -1)
        
        # 生成输出
        output = self.output_layer(torch.cat([controller_hidden, new_read_vectors_flat], dim=1))
        
        # 新状态
        new_state = (controller_hidden, controller_cell, memory, new_read_weights, new_write_weights, usage)
        
        return output, new_state

# 使用示例
dnc = DNC(input_size=10, hidden_size=64, memory_size=16, memory_dim=16)
x = torch.randn(32, 10)  # batch_size=32, input_size=10
output, state = dnc(x)
print(f"Output shape: {output.shape}")
```

### 推荐论文
1. Graves et al., "Hybrid computing using a neural network with dynamic external memory", Nature 2016
2. Santoro et al., "One-shot Learning with Memory-Augmented Neural Networks", ICML 2016
3. Rae et al., "Scaling Memory-Augmented Neural Networks with Sparse Reads and Writes", NeurIPS 2016

---

## Retrieval-Augmented Generation (RAG)

### 这玩意儿到底是啥？
RAG就是把检索和生成结合起来！先从外部知识库检索相关信息，然后把这些信息作为上下文输入给生成模型。

### 核心公式推导
**检索阶段**：
$$
D = \text{Retrieve}(q, K)
$$

**生成阶段**：
$$
P(y|q, D) = \prod_{i=1}^{|y|} P(y_i | q, D, y_{<i})
$$

**端到端训练**：
$$
\mathcal{L} = -\log P(y^* | q, D)
$$

其中：
- $q$ 是查询
- $K$ 是知识库
- $D$ 是检索到的文档
- $y^*$ 是真实答案

**为什么有效？**
- 结合了检索的准确性和生成的流畅性
- 可以访问最新的外部知识
- 减少了模型的幻觉问题

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM

class RAGModel(nn.Module):
    def __init__(self, retriever_name="facebook/dpr-question_encoder-single-nq-base", 
                 generator_name="facebook/bart-large"):
        super().__init__()
        self.retriever_tokenizer = AutoTokenizer.from_pretrained(retriever_name)
        self.retriever = AutoModel.from_pretrained(retriever_name)
        
        self.generator_tokenizer = AutoTokenizer.from_pretrained(generator_name)
        self.generator = AutoModelForSeq2SeqLM.from_pretrained(generator_name)
        
    def encode_query(self, query):
        """编码查询"""
        inputs = self.retriever_tokenizer(query, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.retriever(**inputs)
            query_embedding = outputs.last_hidden_state[:, 0, :]  # [CLS] token
        return query_embedding
    
    def encode_documents(self, documents):
        """编码文档"""
        inputs = self.retriever_tokenizer(documents, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.retriever(**inputs)
            doc_embeddings = outputs.last_hidden_state[:, 0, :]
        return doc_embeddings
    
    def retrieve(self, query_embedding, doc_embeddings, documents, k=5):
        """检索最相关的文档"""
        similarities = torch.matmul(query_embedding, doc_embeddings.t())
        top_k_indices = torch.topk(similarities, k, dim=1).indices[0]
        retrieved_docs = [documents[i] for i in top_k_indices]
        return retrieved_docs
    
    def generate(self, query, retrieved_docs):
        """生成答案"""
        context = " ".join(retrieved_docs)
        input_text = f"question: {query} context: {context}"
        
        inputs = self.generator_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = self.generator.generate(**inputs, max_length=100, num_beams=4)
            answer = self.generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer
    
    def forward(self, query, documents, target_answer=None):
        """端到端前向传播"""
        # 检索
        query_embedding = self.encode_query(query)
        doc_embeddings = self.encode_documents(documents)
        retrieved_docs = self.retrieve(query_embedding, doc_embeddings, documents)
        
        # 生成
        if target_answer is not None:
            # 训练模式
            context = " ".join(retrieved_docs)
            input_text = f"question: {query} context: {context}"
            
            inputs = self.generator_tokenizer(
                input_text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True,
                padding=True
            )
            targets = self.generator_tokenizer(
                target_answer,
                return_tensors="pt",
                max_length=100,
                truncation=True,
                padding=True
            )
            
            outputs = self.generator(**inputs, labels=targets.input_ids)
            return outputs.loss
        else:
            # 推理模式
            return self.generate(query, retrieved_docs)

# 使用示例
rag = RAGModel()

# 检索+生成
query = "What is the capital of France?"
documents = [
    "Paris is the capital and most populous city of France.",
    "London is the capital of England.",
    "Berlin is the capital of Germany."
]

answer = rag(query, documents)
print(f"Answer: {answer}")

# 训练（需要真实答案）
loss = rag(query, documents, target_answer="Paris")
print(f"Loss: {loss.item()}")
```

### 推荐论文
1. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020
2. Izacard & Grave, "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering", EACL 2021
3. Guu et al., "REALM: Retrieval-Augmented Language Model Pre-Training", ICML 2020

---
> 记忆与检索让模型变得更聪明！向量检索简单实用，记忆网络模拟人脑，DNC功能强大，RAG结合检索和生成。记住：好的记忆系统能让模型回答更准确、更可靠！