# 项目约定

> 本文件定义项目的目录结构、模块划分和技术栈约定。

## 技术栈

| 领域 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 深度学习 | PyTorch 2.x |
| 数据处理 | NumPy, Pandas |
| 可视化 | Matplotlib, seaborn |

## 目录结构

```
python学习/
├── .spec/              # 项目规范
├── .claude/            # Claude 配置
├── knowledge_base/     # 知识库文档
│   ├── 01-mamba/       # 按主题编号
│   ├── 02-transformer/
│   └── ...
├── experiments/        # 实验代码
├── notebooks/          # Jupyter 笔记本
├── src/                # 源代码（如需要）
│   ├── models/         # 模型定义
│   ├── data/           # 数据处理
│   └── utils/          # 工具函数
└── tests/              # 测试代码
```

## 模块命名

- 使用两位数字前缀：`01-mamba`, `02-transformer`
- 每个模块包含 `README.md` 说明

## 实验代码规范

### 文件命名

```
experiment_YYYYMMDD_description.py
```

### 标准头部

```python
"""
实验说明：简要描述实验目的

运行方式：
    python experiment_20260325_attention.py --config config.yaml

依赖：
    torch>=2.0, transformers>=4.30
"""
```

## Git 约定

### 提交信息格式

```
<type>: <description>

# 类型：feat, fix, docs, refactor, test, chore
# 示例：
# feat: 添加多头注意力实现
# fix: 修复梯度计算错误
```

### 分支命名

```
feature/description    # 新功能
fix/description        # 修复
experiment/description # 实验性代码
```