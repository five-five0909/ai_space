# PyTorch 刷题计划 — LeetCode风格

> 30道题 × 8周 × 从Tensor到PISFM实战

## 统计

| 总题数 | Easy | Medium | Hard |
|--------|------|--------|------|
| 30 | 12 | 13 | 5 |

## 周次安排

| 周 | 主题 | 题数 | 难度分布 |
|----|------|------|----------|
| Week 1 | Tensor + Autograd | 4 | 3 Easy, 1 Medium |
| Week 2 | Dataset + 训练循环 | 4 | 1 Easy, 2 Medium, 1 Hard |
| Week 3 | CNN | 4 | 1 Easy, 2 Medium, 1 Hard |
| Week 4 | LSTM / RNN | 3 | 1 Medium, 1 Medium, 1 Hard |
| Week 5 | Transformer | 3 | 2 Medium, 1 Hard |
| Week 6 | 调优技巧 | 4 | 1 Easy, 3 Medium |
| Week 7 | PISFM项目周 | 4 | 2 Medium, 2 Hard |
| Week 8 | 工程化 | 4 | 2 Easy, 1 Medium, 1 Hard |

## 题目分类

- **Kaggle周赛题**: P008, P012, P015, P018, P022, P026 (6题)
- **PISFM相关**: P001, P002, P005, P010, P013, P014, P017, P020, P023-P026, P030 (13题)

## 每题结构

每道题包含：

```
## P[编号] [题目名称] [难度标签]

### 题目描述
[问题描述]

### 函数签名
```python
[函数签名]
```

### 约束条件
- [约束1]
- [约束2]
- ...

### 验收断言（assert）
```python
[断言代码]
```

### 提示
> [提示内容]
```

## 文件结构

```
PyTorch刷题/
├── README.md                    # 本文件
├── progress.md                  # 进度追踪表
├── Week01-Tensor-Autograd/      # 第1周题目
│   └── README.md
├── Week02-Dataset-训练循环/
│   └── README.md
├── ...
├── Week08-工程化/
│   └── README.md
└── solutions/                   # 参考答案（独立目录）
    ├── Week01-参考答案.md
    ├── Week02-参考答案.md
    └── ...
```

## 使用方式

1. **刷题**: 进入对应周的目录，阅读README中的题目
2. **验证**: 运行assert断言检查答案
3. **参考**: 卡住时查看 `solutions/` 目录的参考答案

## 核心设计理念

借鉴LeetCode体验：
- **函数签名**: 明确要写什么
- **约束条件**: 不允许用什么API、参数范围
- **可执行assert**: 跑一下就知道过没过
- **隐藏提示**: 卡住时可展开查看

## 难度曲线

```
Week 1-2  ⭐⭐    基础API + 数据管线
Week 3-5  ⭐⭐⭐  经典架构实现
Week 6-8  ⭐⭐⭐⭐ 调优 + PISFM实战
```

## 关键题目

最有价值的三道Hard题：
- **P007**: 从零实现Linear层
- **P010**: 手写BatchNorm1d
- **P013**: 手写LSTM cell

把这三道搞定，PyTorch底层就通透了。