# 36. RAG框架

> 一句话：RAG框架就是让大模型"开卷考试"的工具，先把知识检索出来，再让模型基于检索结果回答问题。LlamaIndex专注索引，LangChain全栈通用，Haystack生产就绪。

---

## LlamaIndex

### 这玩意儿到底是啥？

LlamaIndex（原GPT Index）是一个专门为构建RAG应用设计的框架，核心优势在于**强大的数据索引和检索能力**。它提供了多种索引类型、检索策略和查询引擎，让开发者能快速构建高质量的知识问答系统。

**核心组件：**
- **数据连接器**：支持各种数据源（PDF、数据库、API等）
- **索引**：向量索引、树索引、关键词索引等
- **检索器**：语义检索、混合检索、重排序
- **查询引擎**：组合检索结果生成回答

### 核心架构

```
LlamaIndex架构：
┌─────────────────────────────────────────┐
│              Query Engine               │
│  ┌─────────────┐    ┌────────────────┐ │
│  │   Retriever │ ←→ │ Response Synth │ │
│  └─────────────┘    └────────────────┘ │
├─────────────────────────────────────────┤
│                Index                     │
│  ┌─────────────────────────────────────┐│
│  │  Vector Store Index / Tree Index    ││
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  ││
│  │  │Node1│ │Node2│ │Node3│ │ ... │  ││
│  │  └─────┘ └─────┘ └─────┘ └─────┘  ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│           Document Store                 │
│  ┌─────────────────────────────────────┐│
│  │  PDF / Web / DB / API / ...         ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### 代码示例

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

# 配置
Settings.embed_model = OpenAIEmbedding()
Settings.llm = OpenAI(model="gpt-4")

# 加载文档
documents = SimpleDirectoryReader("./data").load_data()

# 分割文档
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = splitter.get_nodes_from_documents(documents)

# 创建索引
index = VectorStoreIndex(nodes)

# 创建查询引擎
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact",
)

# 查询
response = query_engine.query("什么是Transformer？")
print(response)

# 流式查询
streaming_engine = index.as_query_engine(streaming=True)
streaming_response = streaming_engine.query("解释一下注意力机制")
for text in streaming_response.response_gen:
    print(text, end="", flush=True)
```

### 高级功能

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.indices.vector_store.retrievers import AutoMergingRetriever
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore

# 持久化存储
storage_context = StorageContext.from_defaults(
    docstore=SimpleDocumentStore(),
)
index.storage_context.persist(persist_dir="./storage")

# 重新加载
from llama_index.core import load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# 混合检索（向量 + 关键词）
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever

vector_retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5)

# 融合检索器
fusion_retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    similarity_top_k=5,
    num_queries=1,
    mode="reciprocal_rerank",
)

# 重排序
from llama_index.postprocessor.cohere_rerank import CohereRerank

cohere_rerank = CohereRerank(api_key="your-api-key", top_n=5)

query_engine = RetrieverQueryEngine.from_args(
    retriever=fusion_retriever,
    node_postprocessors=[cohere_rerank],
)

# 多文档查询
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

# 创建多个索引
vector_index_2023 = VectorStoreIndex.from_documents(docs_2023)
vector_index_2024 = VectorStoreIndex.from_documents(docs_2024)

# 创建工具
query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_index_2023.as_query_engine(),
        metadata=ToolMetadata(
            name="docs_2023",
            description="2023年的文档资料",
        ),
    ),
    QueryEngineTool(
        query_engine=vector_index_2024.as_query_engine(),
        metadata=ToolMetadata(
            name="docs_2024",
            description="2024年的文档资料",
        ),
    ),
]

# 子问题查询引擎
sub_question_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
)

response = sub_question_engine.query("对比2023年和2024年的主要变化")
```

### 推荐论文

1. **Liu et al., 2023** - "LlamaIndex: A Data Framework for LLM Applications" - 官方文档
2. **Gao et al., 2023** - "Retrieval-Augmented Generation for Large Language Models: A Survey" - RAG综述
3. **Lewis et al., 2020** - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" - RAG原论文

---

## LangChain

### 这玩意儿到底是啥？

LangChain是一个全栈LLM应用开发框架，不仅支持RAG，还支持Agent、Chain、Memory等多种功能。它的核心思想是通过**组件化和链式调用**来构建复杂的LLM应用。

**核心组件：**
- **Models**：LLM和Embedding模型的统一接口
- **Prompts**：提示模板和管理
- **Memory**：对话历史管理
- **Indexes**：文档加载、分割、向量存储
- **Chains**：组件组合成工作流
- **Agents**：动态决策和工具调用

### RAG代码示例

```python
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 加载文档
loader = PyPDFLoader("./document.pdf")
documents = loader.load()

# 分割文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
splits = text_splitter.split_documents(documents)

# 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db",
)

# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)

# 创建RAG链
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

prompt_template = """你是一个专业的AI助手。请根据以下上下文回答问题。
如果上下文中没有相关信息，请说"我不知道"。

上下文：
{context}

问题：{question}

回答："""
PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"],
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
)

# 查询
result = qa_chain({"query": "什么是Transformer？"})
print(result["result"])
print("\n来源文档：")
for doc in result["source_documents"]:
    print(f"- {doc.metadata.get('source', 'Unknown')}")
```

### 高级RAG功能

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import MultiQueryRetriever

# 1. 上下文压缩
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever,
)

# 2. 混合检索
bm25_retriever = BM25Retriever.from_documents(splits)
bm25_retriever.k = 5

ensemble_retriever = EnsembleRetriever(
    retrievers=[retriever, bm25_retriever],
    weights=[0.5, 0.5],
)

# 3. 多查询检索
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm,
)

# 自动生成多个相关查询
docs = multi_query_retriever.get_relevant_documents("什么是深度学习？")

# 4. 对话式RAG
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)

conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    verbose=True,
)

# 多轮对话
result1 = conversational_chain({"question": "什么是Transformer？"})
result2 = conversational_chain({"question": "它有什么优点？"})  # 会记住之前的上下文

# 5. Self-Query检索（元数据过滤）
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever

metadata_field_info = [
    AttributeInfo(
        name="year",
        description="文档发表的年份",
        type="integer",
    ),
    AttributeInfo(
        name="category",
        description="文档的类别",
        type="string",
    ),
]

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="技术文档",
    metadata_field_info=metadata_field_info,
    verbose=True,
)

# 自动解析查询并过滤
docs = self_query_retriever.get_relevant_documents(
    "2023年发表的关于Transformer的文章"
)
```

### 推荐论文

1. **Chase, 2022** - "LangChain: Building Applications with LLMs" - 官方文档
2. **Liu et al., 2023** - "Lost in the Middle: How Language Models Use Long Contexts" - 检索策略
3. **Gao et al., 2023** - "Precise Zero-Shot Dense Retrieval without Relevance Labels" - HyDE技术

---

## Haystack

### 这玩意儿到底是啥？

Haystack是deepset开源的NLP框架，专注于**生产环境的RAG和问答系统**。它的核心优势是**Pipeline架构**，让开发者可以像搭积木一样组装检索和生成组件。

**核心组件：**
- **DocumentStore**：文档存储（Elasticsearch, FAISS, Weaviate等）
- **Retriever**：检索器（BM25, Embedding, MultiModal）
- **Reader**：阅读器（Extractive, Generative）
- **Pipeline**：工作流编排

### 代码示例

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever, InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder

# 创建文档存储
document_store = InMemoryDocumentStore()

# 添加文档
documents = [
    Document(content="Transformer是一种基于自注意力机制的神经网络架构。"),
    Document(content="BERT是双向Transformer预训练模型。"),
    Document(content="GPT是单向Transformer，用于文本生成。"),
]
document_store.write_documents(documents)

# 创建嵌入
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
doc_embedder.warm_up()
documents_with_embeddings = doc_embedder.run(documents)
document_store.write_documents(documents_with_embeddings["documents"])

# 创建Pipeline
text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

retriever = InMemoryEmbeddingRetriever(document_store=document_store, top_k=3)

prompt_template = """
根据以下文档回答问题。如果文档中没有相关信息，请说"我不知道"。

文档：
{% for doc in documents %}
  {{ doc.content }}
{% endfor %}

问题：{{ query }}

回答：
"""
prompt_builder = PromptBuilder(template=prompt_template)

generator = OpenAIGenerator(model="gpt-4")

# 组装Pipeline
rag_pipeline = Pipeline()
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("generator", generator)

rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "generator.prompt")

# 执行查询
result = rag_pipeline.run({
    "text_embedder": {"text": "什么是Transformer？"},
    "prompt_builder": {"query": "什么是Transformer？"},
})

print(result["generator"]["replies"][0])
```

### Pipeline架构

```python
from haystack import Pipeline
from haystack.components.retrievers import BM25Retriever
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.generators import HuggingFaceLocalGenerator

# 多阶段Pipeline
pipeline = Pipeline()

# 添加组件
pipeline.add_component("bm25_retriever", BM25Retriever(document_store=document_store, top_k=20))
pipeline.add_component("embedding_retriever", InMemoryEmbeddingRetriever(document_store=document_store, top_k=20))
pipeline.add_component("ranker", TransformersSimilarityRanker(model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_k=5))
pipeline.add_component("generator", OpenAIGenerator(model="gpt-4"))

# 连接组件
pipeline.connect("bm25_retriever.documents", "ranker.documents")
pipeline.connect("embedding_retriever.documents", "ranker.documents")
pipeline.connect("ranker.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "generator.prompt")

# 绘制Pipeline图
pipeline.draw("./rag_pipeline.png")
```

### 推荐论文

1. **deepset, 2022** - "Haystack: Neural Question Answering at Scale" - 官方文档
2. **Karpukhin et al., 2020** - "Dense Passage Retrieval for Open-Domain Question Answering" - DPR检索
3. **Nogueira & Cho, 2019** - "Passage Re-ranking with BERT" - 重排序

---

## RAGFlow

### 这玩意儿到底是啥？

RAGFlow是开源的RAG引擎，特点是**深度文档理解**和**可视化工作流编排**。它特别擅长处理复杂的文档格式（表格、图表、多栏布局），并提供可视化界面构建RAG流程。

**核心特点：**
- **深度文档解析**：支持PDF、图片、表格的智能解析
- **可视化编排**：拖拽式构建RAG流程
- **多种检索策略**：关键词、语义、混合检索
- **内置LLM**：支持本地和云端模型

### 代码示例

```python
# RAGFlow主要通过API或UI使用
import requests

# 创建知识库
response = requests.post(
    "http://localhost/api/kb/create",
    json={
        "name": "技术文档库",
        "description": "存储技术相关文档",
    },
)
kb_id = response.json()["data"]["id"]

# 上传文档
files = {"file": open("document.pdf", "rb")}
response = requests.post(
    f"http://localhost/api/kb/{kb_id}/upload",
    files=files,
)

# 查询
response = requests.post(
    "http://localhost/api/chat",
    json={
        "kb_id": kb_id,
        "question": "什么是Transformer？",
        "top_k": 5,
    },
)
answer = response.json()["data"]["answer"]
print(answer)
```

### 推荐论文

1. **RAGFlow Team, 2024** - "RAGFlow: An Open-Source RAG Engine" - 官方文档
2. **Gao et al., 2023** - "Retrieval-Augmented Generation for Large Language Models: A Survey" - RAG综述
3. **Glass et al., 2022** - "Re2G: Retrieve, Rerank, Generate" - 重排序

---

## GraphRAG

### 这玩意儿到底是啥？

GraphRAG是微软研究院提出的基于**知识图谱**的RAG方法。传统RAG用向量相似度检索，GraphRAG则构建文档之间的知识图谱，通过图结构进行推理和检索，能更好地处理复杂的多跳问答。

**核心思想：**
```
传统RAG：
Query → 向量检索 → Top-K文档 → LLM生成

GraphRAG：
Query → 图谱推理 → 相关实体/关系 → 子图检索 → LLM生成
```

### 核心流程

```
GraphRAG构建流程：
1. 文档分块 → 提取实体和关系
2. 构建知识图谱（节点=实体，边=关系）
3. 社区检测 → 形成层次化社区
4. 社区摘要 → LLM生成每个社区的描述

查询流程：
1. 问题分析 → 提取相关实体
2. 图谱遍历 → 找到相关子图
3. 社区检索 → 获取相关社区摘要
4. 答案生成 → 整合信息回答
```

### 代码示例

```python
# 使用微软GraphRAG库
# pip install graphrag

import asyncio
from graphrag.index import create_pipeline_config, run_pipeline

# 配置GraphRAG
config = create_pipeline_config(
    input_path="./input",  # 输入文档目录
    root_dir="./graphrag_workspace",
)

# 运行索引
async def build_index():
    pipeline = await run_pipeline(config)
    return pipeline

# asyncio.run(build_index())

# 查询
from graphrag.query.structured_search.local_search import LocalSearch
from graphrag.query.structured_search.global_search import GlobalSearch

# 本地搜索（特定细节）
local_search = LocalSearch(
    config=config,
    llm=llm,
    entities=entities,
    relationships=relationships,
    covariates=covariates,
)

result = await local_search.search("谁发明了Transformer？")
print(result.response)

# 全局搜索（宏观问题）
global_search = GlobalSearch(
    config=config,
    llm=llm,
    communities=communities,
)

result = await global_search.search("AI领域的主要发展趋势是什么？")
print(result.response)
```

### 推荐论文

1. **Edge et al., 2024** - "From Local to Global: A Graph RAG Approach to Query-Focused Summarization" - GraphRAG原论文
2. **Wu et al., 2023** - "Knowledge Graph-Enhanced Language Models for Reasoning" - 知识图谱增强
3. **Wei et al., 2023** - "Chain-of-Thought Prompting Elicits Reasoning" - 推理增强

---

## RAG优化技术

### 检索优化

**1. 混合检索（Hybrid Search）：**
```python
# 向量检索 + BM25
from langchain.retrievers import EnsembleRetriever

ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)
```

**2. 重排序（Reranking）：**
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = reranker.predict([(query, doc.page_content) for doc in docs])
sorted_docs = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]
```

**3. HyDE（Hypothetical Document Embeddings）：**
```python
# 生成假设文档，用假设文档检索
from langchain.chains import HypotheticalDocumentEmbedder

hyde_retriever = HypotheticalDocumentEmbedder.from_llm(
    llm=llm,
    base_embeddings=embeddings,
    prompts={"query": "请生成一段回答这个问题的文本"},
)
```

### 生成优化

**1. 链式推理（Chain-of-Thought）：**
```python
prompt = """
请一步步思考以下问题：
1. 分析问题的关键点
2. 从文档中找出相关信息
3. 综合信息给出答案

文档：{context}
问题：{question}
"""
```

**2. 自我反思（Self-Reflection）：**
```python
from langchain.chains import LLMChain

reflection_prompt = """
你给出的答案是否完全基于提供的文档？
文档中是否有遗漏的重要信息？
请评估并改进你的答案。
"""
```

---

## 对比总结

| 框架 | 核心优势 | 适用场景 | 学习曲线 |
|------|----------|----------|----------|
| LlamaIndex | 索引和检索能力强 | 知识问答、文档搜索 | 中 |
| LangChain | 全栈、组件丰富 | 复杂应用、Agent | 高 |
| Haystack | 生产就绪、Pipeline | 企业级RAG系统 | 中 |
| RAGFlow | 深度文档解析 | 复杂文档处理 | 低 |
| GraphRAG | 图谱推理 | 多跳问答、复杂推理 | 高 |

### 选择建议

```
快速构建知识问答 → LlamaIndex
需要Agent和复杂工作流 → LangChain
企业生产部署 → Haystack
复杂文档（表格、图表）→ RAGFlow
需要复杂推理 → GraphRAG
```

---

> RAG框架是大模型落地的核心技术！LlamaIndex专注检索，LangChain全栈通用，Haystack生产就绪。选择合适的框架，再配合重排序、HyDE等优化技术，能让你的问答系统更智能、更准确！