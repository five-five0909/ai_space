# AI/ML知识库完整文档

> 本知识库包含43个主题的详细技术文档，**全部已完成**！每个文档都包含：
> - 大白话解释（"这玩意儿到底是啥？"）
> - 核心公式推导
> - PyTorch代码示例
> - 3篇推荐论文

---

## 目录

### 基础架构
- [1. Mamba 系列](./01-mamba/README.md) ✅
- [2. Transformer 系列](./02-transformer/README.md) ✅
- [3. 注意力机制完整版](./03-attention/README.md) ✅
- [4. 位置编码全家桶](./04-positional-encoding/README.md) ✅
- [5. 序列建模架构（替代Transformer）](./05-sequence-modeling/README.md) ✅
- [6. 新型网络层/模块](./06-novel-modules/README.md) ✅

### 训练基础设施
- [7. 归一化方法](./07-normalization/README.md) ✅
- [8. 激活函数](./08-activation/README.md) ✅
- [9. 优化器](./09-optimizer/README.md) ✅
- [10. 学习率调度](./10-lr-schedule/README.md) ✅
- [11. 正则化/防过拟合](./11-regularization/README.md) ✅
- [12. 损失函数](./12-loss-functions/README.md) ✅
- [13. 数据增强/生成](./13-data-augmentation/README.md) ✅

### 模型压缩与对齐
- [14. 知识蒸馏](./14-knowledge-distillation/README.md) ✅
- [15. 量化/压缩/部署](./15-quantization/README.md) ✅
- [16. RLHF/对齐全家桶](./16-rlhf-alignment/README.md) ✅
- [17. 推理增强/思维链](./17-reasoning/README.md) ✅

### 分布式与多模态
- [18. 模型并行/分布式训练](./18-distributed/README.md) ✅
- [19. 词嵌入/Tokenization](./19-tokenization/README.md) ✅
- [20. 记忆/检索增强](./20-memory-retrieval/README.md) ✅
- [21. Kimi Attention Residuals](./21-kimi-attnres/README.md) ✅
- [22. KV Cache 全家桶](./22-kv-cache/README.md) ✅
- [23. MoE 系列](./23-moe/README.md) ✅
- [24. 视觉/多模态架构](./24-vision-multimodal/README.md) ✅
- [25. 扩散模型系列](./25-diffusion/README.md) ✅

### 大模型技术栈
- [26. 大模型训练/推理技术](./26-training-inference/README.md) ✅
- [27. 自监督/预训练范式](./27-self-supervised/README.md) ✅
- [28. 图/点云/3D](./28-graph-3d/README.md) ✅
- [29. 智能体/工具调用](./29-agent/README.md) ✅
- [30. 时间序列Transformer](./30-time-series/README.md) ✅
- [31. 音频/语音Transformer](./31-audio-speech/README.md) ✅

### 工具与框架
- [32. 推理服务框架](./32-inference-frameworks/README.md) ✅
- [33. 本地运行工具](./33-local-tools/README.md) ✅
- [34. API聚合/路由平台](./34-api-platforms/README.md) ✅
- [35. 模型格式与量化工具](./35-model-formats/README.md) ✅
- [36. RAG框架](./36-rag-frameworks/README.md) ✅
- [37. 向量数据库](./37-vector-db/README.md) ✅
- [38. Agent框架](./38-agent-frameworks/README.md) ✅
- [39. 评估/测试框架](./39-evaluation/README.md) ✅
- [40. 训练框架](./40-training-frameworks/README.md) ✅

### 专业领域
- [41. 遥感/光谱相关](./41-remote-sensing/README.md) ✅
- [42. 其他热词](./42-hot-topics/README.md) ✅
- [43. PISFM项目相关汇总](./43-pisfm/README.md) ✅

---

## 使用说明

1. **学习路线**：建议从基础架构开始，然后到训练基础设施，最后到具体应用
2. **查阅方式**：每个名词都有独立的详细解释，可以直接跳转查看
3. **代码实践**：所有PyTorch示例都可以直接运行测试
4. **论文阅读**：每篇推荐论文都标注了核心贡献

## 文档特点

- **大白话解释**：避免学术术语堆砌，用工程师语言解释
- **公式推导**：关键公式都有完整推导过程
- **代码示例**：提供可运行的PyTorch实现
- **论文推荐**：精选3篇最具代表性的论文
- **中国研究生友好**：符合国内研究生的阅读和书写习惯

---
*最后更新：2026-03-22*