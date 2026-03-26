# 37. 向量数据库

> 一句话：向量数据库就是专门存和查向量的数据库，核心能力是**相似度搜索**。Milvus开源强大，Pinecone全托管省心，Chroma轻量易用，Qdrant性能优秀。

---

## 向量数据库基础

### 这玩意儿到底是啥？

向量数据库是专门用于存储、索引和检索高维向量的数据库系统。在AI应用中，它主要用于：

- **语义搜索**：根据含义而非关键词搜索
- **推荐系统**：找到相似的用户或物品
- **RAG检索**：为问答系统检索相关文档
- **去重**：检测相似或重复的内容

### 核心概念

**向量嵌入（Embedding）：**
```
文本 → Embedding模型 → 向量
"猫是一种宠物" → [0.23, -0.15, 0.87, ..., 0.12] (1536维)
```

**相似度度量：**

**余弦相似度：**
$$
\text{similarity} = \frac{A \cdot B}{\|A\| \|B\|} = \frac{\sum_{i=1}^n A_i B_i}{\sqrt{\sum_{i=1}^n A_i^2} \sqrt{\sum_{i=1}^n B_i^2}}
$$

**欧氏距离：**
$$
\text{distance} = \sqrt{\sum_{i=1}^n (A_i - B_i)^2}
$$

**点积：**
$$
\text{score} = A \cdot B = \sum_{i=1}^n A_i B_i
$$

**索引类型：**

| 索引类型 | 原理 | 查询速度 | 内存占用 | 精度 |
|----------|------|----------|----------|------|
| Flat | 暴力搜索 | 慢 | 高 | 100% |
| IVF | 聚类后搜索 | 快 | 中 | 高 |
| HNSW | 图索引 | 最快 | 高 | 高 |
| PQ | 量化压缩 | 中 | 低 | 中 |

---

## Milvus

### 这玩意儿到底是啥？

Milvus是Zilliz开源的云原生向量数据库，支持大规模向量检索。它是目前最流行的开源向量数据库之一，支持多种索引类型、分布式部署、混合查询等高级功能。

**核心特点：**
- **高性能**：支持十亿级向量检索
- **云原生**：Kubernetes友好，支持弹性扩展
- **多索引**：支持FLAT、IVF、HNSW、ANNOY等多种索引
- **混合查询**：支持向量+标量过滤
- **GPU加速**：支持GPU索引加速

### 核心架构

```
Milvus架构：
┌─────────────────────────────────────────────────────┐
│                    Proxy (访问层)                    │
├─────────────────────────────────────────────────────┤
│                  Coordinator (协调层)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Root Coord│ │Query Coord│ │Data Coord│ │Index   │ │
│  │          │ │           │ │          │ │Coord   │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────┤
│                    Worker (工作节点)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Query Node│ │Data Node │ │Index Node│           │
│  └──────────┘ └──────────┘ └──────────┘           │
├─────────────────────────────────────────────────────┤
│                    Storage (存储层)                  │
│  ┌────────────────┐  ┌────────────────────────┐    │
│  │Meta Storage    │  │Object Storage (MinIO)  │    │
│  │(etcd)          │  │                        │    │
│  └────────────────┘  └────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### PyTorch代码示例

```python
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)
import numpy as np

# 连接Milvus
connections.connect(host="localhost", port="19530")

# 定义schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="year", dtype=DataType.INT32),
]

schema = CollectionSchema(fields=fields, description="文档向量集合")

# 创建collection
collection = Collection(name="documents", schema=schema)

# 创建索引（HNSW）
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {
        "M": 16,  # 连接数
        "efConstruction": 256,  # 构建时的搜索范围
    },
}
collection.create_index(field_name="embedding", index_params=index_params)

# 插入数据
import random

num_entities = 10000
entities = [
    [i for i in range(num_entities)],  # id (auto_id会忽略)
    [[random.random() for _ in range(768)] for _ in range(num_entities)],  # embedding
    [f"文档{i}" for i in range(num_entities)],  # title
    [random.randint(2010, 2024) for _ in range(num_entities)],  # year
]

collection.insert(entities)
collection.flush()  # 确保数据持久化

# 加载collection到内存
collection.load()

# 搜索
search_params = {"metric_type": "COSINE", "params": {"ef": 64}}
query_vector = [[random.random() for _ in range(768)]]

results = collection.search(
    data=query_vector,
    anns_field="embedding",
    param=search_params,
    limit=10,
    expr="year > 2020",  # 标量过滤
    output_fields=["title", "year"],
)

for hits in results:
    for hit in hits:
        print(f"ID: {hit.id}, Distance: {hit.distance:.4f}")
        print(f"Title: {hit.entity.get('title')}, Year: {hit.entity.get('year')}")

# 混合查询（向量 + 标量）
results = collection.query(
    expr="year >= 2020 and year <= 2023",
    output_fields=["title", "year", "embedding"],
    limit=100,
)

# 释放资源
collection.release()
connections.disconnect("default")
```

### 使用LangChain集成

```python
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 初始化
embeddings = OpenAIEmbeddings()

# 从文档创建
vectorstore = Milvus.from_documents(
    documents=splits,
    embedding=embeddings,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="langchain_demo",
)

# 搜索
results = vectorstore.similarity_search("什么是Transformer？", k=5)
for doc in results:
    print(doc.page_content)

# 带分数的搜索
results_with_scores = vectorstore.similarity_search_with_score("什么是深度学习？", k=5)
for doc, score in results_with_scores:
    print(f"Score: {score:.4f}, Content: {doc.page_content[:100]}...")
```

### 推荐论文

1. **Wang et al., 2021** - "Milvus: A Purpose-Built Vector Data Management System" - Milvus原论文
2. **Malkov & Yashunin, 2018** - "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs" - HNSW算法
3. **Jegou et al., 2011** - "Product Quantization for Nearest Neighbor Search" - PQ量化

---

## Pinecone

### 这玩意儿到底是啥？

Pinecone是一个全托管的向量数据库服务，开发者无需管理基础设施，专注于构建应用。它提供了简单易用的API，自动扩缩容，是企业级应用的理想选择。

**核心特点：**
- **全托管**：无需运维，自动扩缩容
- **低延迟**：全球分布式部署
- **高可用**：多副本、自动故障恢复
- **简单API**：几行代码即可使用

### 代码示例

```python
import pinecone
from pinecone import Pinecone, ServerlessSpec

# 初始化
pc = Pinecone(api_key="your-api-key")

# 创建索引
index_name = "documents"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        ),
    )

# 连接索引
index = pc.Index(index_name)

# 插入向量
vectors = [
    {
        "id": "doc1",
        "values": [0.1, 0.2, 0.3, ...],  # 768维向量
        "metadata": {"title": "文档1", "category": "技术"},
    },
    {
        "id": "doc2",
        "values": [0.4, 0.5, 0.6, ...],
        "metadata": {"title": "文档2", "category": "新闻"},
    },
]

index.upsert(vectors=vectors)

# 查询
query_vector = [0.1, 0.2, 0.3, ...]
results = index.query(
    vector=query_vector,
    top_k=10,
    include_metadata=True,
    filter={
        "category": {"$eq": "技术"},
    },  # 元数据过滤
)

for match in results["matches"]:
    print(f"ID: {match['id']}, Score: {match['score']:.4f}")
    print(f"Metadata: {match['metadata']}")

# 批量操作
batch_size = 100
for i in range(0, len(all_vectors), batch_size):
    batch = all_vectors[i:i + batch_size]
    index.upsert(vectors=batch)

# 删除
index.delete(ids=["doc1", "doc2"])

# 更新
index.upsert([{
    "id": "doc1",
    "values": new_vector,
    "metadata": {"title": "更新后的文档1"},
}])
```

### LangChain集成

```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

vectorstore = PineconeVectorStore.from_documents(
    documents=splits,
    index_name="documents",
    embedding=embeddings,
    pinecone_api_key="your-api-key",
)

# 搜索
results = vectorstore.similarity_search("机器学习", k=5)
```

### 推荐论文

1. **Pinecone, 2021** - "Pinecone: The Vector Database for AI Applications" - 官方文档
2. **Google, 2020** - "ScaNN: Efficient Vector Similarity Search" - 向量搜索算法
3. **Spotify, 2019** - "Annoy: Approximate Nearest Neighbors" - ANNOY算法

---

## Weaviate

### 这玩意儿到底是啥？

Weaviate是一个开源的向量数据库，核心特色是**语义理解**和**模块化架构**。它内置了向量化和重排序模块，可以直接存储原始对象，自动生成向量。

**核心特点：**
- **模块化**：内置向量化、重排序、生成模块
- **GraphQL API**：灵活的查询接口
- **语义理解**：支持跨模态搜索
- **实时更新**：支持增量索引

### 代码示例

```python
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType

# 连接
client = weaviate.connect_to_local()

# 创建collection
questions = client.collections.create(
    name="Question",
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="category", data_type=DataType.TEXT),
    ],
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    generative_config=Configure.Generative.openai(),
)

# 插入数据
with questions.batch.dynamic() as batch:
    batch.add_object({
        "content": "什么是Transformer？",
        "category": "技术",
    })
    batch.add_object({
        "content": "Python如何学习？",
        "category": "编程",
    })

# 向量搜索
response = questions.query.near_text(
    query="深度学习模型",
    limit=5,
)

for obj in response.objects:
    print(f"Content: {obj.properties['content']}")
    print(f"Category: {obj.properties['category']}")

# 混合搜索（向量 + 关键词）
from weaviate.classes.query import HybridFusion

response = questions.query.hybrid(
    query="Transformer",
    alpha=0.5,  # 向量和BM25的权重平衡
    limit=10,
)

# RAG生成
response = questions.generate.near_text(
    query="什么是注意力机制？",
    limit=3,
    grouped_task="请总结这些问题的共同点",
)

print(response.generated)

# 关闭连接
client.close()
```

### 推荐论文

1. **Weaviate, 2021** - "Weaviate: A Vector Search Engine with Semantic Understanding" - 官方文档
2. **Sankar et al., 2022** - "Hybrid Search: Combining BM25 and Vector Search" - 混合搜索
3. **SeMI, 2023** - "Weaviate Modules: Modular Vector Database Architecture" - 模块化架构

---

## Chroma

### 这玩意儿到底是啥？

Chroma是一个轻量级的开源向量数据库，专注于**简单易用**。它是构建RAG应用最简单的选择之一，几行代码就能启动，支持本地文件存储和HTTP服务两种模式。

**核心特点：**
- **零配置**：开箱即用
- **轻量级**：纯Python实现，无需外部依赖
- **嵌入式**：支持嵌入式运行，无需单独服务
- **易集成**：与LangChain、LlamaIndex无缝集成

### 代码示例

```python
import chromadb
from chromadb.utils import embedding_functions

# 初始化（本地模式）
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 创建collection
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.create_collection(
    name="documents",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"},
)

# 添加文档
collection.add(
    documents=[
        "Transformer是一种基于注意力机制的神经网络架构。",
        "BERT是双向Transformer预训练模型。",
        "GPT是用于文本生成的自回归模型。",
    ],
    metadatas=[
        {"source": "wiki", "topic": "transformer"},
        {"source": "paper", "topic": "bert"},
        {"source": "paper", "topic": "gpt"},
    ],
    ids=["doc1", "doc2", "doc3"],
)

# 查询
results = collection.query(
    query_texts=["什么是语言模型？"],
    n_results=3,
    where={"source": "paper"},  # 元数据过滤
)

print(results["documents"])
print(results["metadatas"])
print(results["distances"])

# 使用ID查询
results = collection.get(
    ids=["doc1", "doc2"],
    include=["documents", "metadatas", "embeddings"],
)

# 更新
collection.update(
    ids=["doc1"],
    documents=["Transformer是一种革命性的神经网络架构。"],
    metadatas=[{"source": "wiki", "topic": "transformer", "updated": "true"}],
)

# 删除
collection.delete(ids=["doc3"])

# 列出所有collection
collections = chroma_client.list_collections()
print([c.name for c in collections])

# 删除collection
chroma_client.delete_collection(name="documents")
```

### LangChain集成

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 创建向量存储
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_langchain",
)

# 搜索
results = vectorstore.similarity_search("深度学习", k=5)

# 作为检索器
retriever = vectorstore.as_retriever(
    search_type="mmr",  # 最大边际相关性
    search_kwargs={"k": 5, "fetch_k": 20},
)
```

### 推荐论文

1. **Chroma, 2023** - "Chroma: The AI-native Open-Source Embedding Database" - 官方文档
2. **HuggingFace, 2019** - "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" - 嵌入模型
3. **Carbonell & Goldstein, 1998** - "The Use of MMR in Text Summarization" - MMR算法

---

## Qdrant

### 这玩意儿到底是啥？

Qdrant是一个高性能的开源向量数据库，用Rust编写，支持高吞吐量和低延迟。它提供了丰富的过滤功能和精准的相似度搜索，是生产环境的热门选择。

**核心特点：**
- **Rust编写**：高性能、内存安全
- **丰富的过滤**：支持复杂的布尔查询
- **量化支持**：支持标量量化、乘积量化
- **分布式**：支持分布式部署

### 代码示例

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# 连接
client = QdrantClient(host="localhost", port=6333)

# 创建collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE,
    ),
)

# 插入向量
points = [
    PointStruct(
        id=i,
        vector=[0.1 * i for _ in range(768)],
        payload={"title": f"文档{i}", "category": "技术" if i % 2 == 0 else "新闻"},
    )
    for i in range(100)
]

client.upsert(
    collection_name="documents",
    points=points,
)

# 搜索
query_vector = [0.1 for _ in range(768)]
results = client.search(
    collection_name="documents",
    query_vector=query_vector,
    limit=10,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="category",
                match=models.MatchValue(value="技术"),
            )
        ]
    ),
)

for result in results:
    print(f"ID: {result.id}, Score: {result.score:.4f}")
    print(f"Payload: {result.payload}")

# 批量搜索
results = client.search_batch(
    collection_name="documents",
    requests=[
        models.SearchRequest(
            vector=[0.2 for _ in range(768)],
            limit=5,
        ),
        models.SearchRequest(
            vector=[0.3 for _ in range(768)],
            limit=5,
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value="新闻"),
                    )
                ]
            ),
        ),
    ],
)

# 创建索引加速过滤
client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

# 量化配置（节省内存）
client.update_collection(
    collection_name="documents",
    optimizer_config=models.OptimizersConfigDiff(
        indexing_threshold=10000,
    ),
    quantization_config=models.ScalarQuantization(
        scalar=models.ScalarQuantizationConfig(
            type=models.ScalarType.INT8,
            quantile=0.99,
            always_ram=True,
        ),
    ),
)
```

### LangChain集成

```python
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = QdrantVectorStore.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    url="http://localhost:6333",
    collection_name="langchain_docs",
)

results = vectorstore.similarity_search("机器学习", k=5)
```

### 推荐论文

1. **Qdrant, 2021** - "Qdrant: Vector Similarity Search Engine" - 官方文档
2. **Andre et al., 2015** - "Product Quantization for Nearest Neighbor Search" - 量化技术
3. **Babenko & Lempitsky, 2014** - "Additive Quantization" - 加性量化

---

## Faiss

### 这玩意儿到底是啥？

Faiss是Facebook AI Research开源的向量相似度搜索库，虽然它更像一个算法库而非完整数据库，但它是目前最流行的向量检索基础库，很多向量数据库底层都使用Faiss。

**核心特点：**
- **高性能**：支持GPU加速
- **多索引**：支持各种ANN算法
- **量化压缩**：大幅减少内存占用
- **灵活**：可嵌入任何应用

### 代码示例

```python
import faiss
import numpy as np

# 生成测试数据
d = 768  # 向量维度
nb = 100000  # 数据库大小
nq = 10  # 查询数量

xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# 1. 暴力搜索（IndexFlatL2）
index_flat = faiss.IndexFlatL2(d)
index_flat.add(xb)

D, I = index_flat.search(xq, 10)  # 搜索最近10个
print(f"Flat索引结果: {I[:3]}")

# 2. IVF索引（倒排索引）
nlist = 100  # 聚类中心数量
quantizer = faiss.IndexFlatL2(d)
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist)

# 训练
index_ivf.train(xb)
index_ivf.add(xb)

D, I = index_ivf.search(xq, 10)
print(f"IVF索引结果: {I[:3]}")

# 3. HNSW索引
index_hnsw = faiss.IndexHNSWFlat(d, 32)  # 32是M参数
index_hnsw.add(xb)

D, I = index_hnsw.search(xq, 10)
print(f"HNSW索引结果: {I[:3]}")

# 4. PQ量化（节省内存）
m = 8  # 子向量数量
index_pq = faiss.IndexPQ(d, m, 8)  # 8 bits per sub-vector
index_pq.train(xb)
index_pq.add(xb)

D, I = index_pq.search(xq, 10)
print(f"PQ索引结果: {I[:3]}")

# 5. GPU加速
res = faiss.StandardGpuResources()
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_flat)
index_gpu.add(xb)
D, I = index_gpu.search(xq, 10)

# 6. IVF+PQ组合（推荐配置）
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
index.train(xb)
index.add(xb)

# 设置搜索参数
index.nprobe = 10  # 搜索的聚类数量
D, I = index.search(xq, 10)
```

### 推荐论文

1. **Johnson et al., 2019** - "Faiss: A Library for Efficient Similarity Search" - Faiss原论文
2. **Malkov & Yashunin, 2018** - "Efficient and Robust Approximate Nearest Neighbor Search Using HNSW" - HNSW算法
3. **Jegou et al., 2011** - "Product Quantization for Nearest Neighbor Search" - PQ量化

---

## 对比总结

| 数据库 | 类型 | 部署方式 | 核心优势 | 适用场景 |
|--------|------|----------|----------|----------|
| Milvus | 开源 | 自托管/云 | 大规模、高性能 | 企业级生产 |
| Pinecone | SaaS | 全托管 | 简单易用、免运维 | 快速上线 |
| Weaviate | 开源 | 自托管/云 | 语义理解、模块化 | 知识图谱 |
| Chroma | 开源 | 嵌入式 | 轻量简单 | 开发测试 |
| Qdrant | 开源 | 自托管/云 | 高性能、Rust | 生产环境 |
| Faiss | 库 | 嵌入式 | 极致性能 | 算法研究 |

### 索引类型对比

| 索引 | 构建速度 | 查询速度 | 内存占用 | 精度 | 适用规模 |
|------|----------|----------|----------|------|----------|
| Flat | 快 | 慢 | 高 | 100% | <100万 |
| IVF | 中 | 快 | 中 | 高 | 百万级 |
| HNSW | 慢 | 最快 | 高 | 高 | 千万级 |
| PQ | 中 | 中 | 低 | 中 | 亿级 |

### 选择建议

```
快速原型/开发测试 → Chroma
企业级生产环境 → Milvus 或 Qdrant
免运维/快速上线 → Pinecone
需要语义理解 → Weaviate
极致性能/研究 → Faiss
```

---

> 向量数据库是AI应用的基础设施！Milvus适合大规模生产，Pinecone省心全托管，Chroma简单易用，Qdrant高性能。选择合适的数据库和索引类型，能让你的AI应用检索更快、更准！