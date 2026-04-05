# Python 学习指南

> 面向 LeetCode 刷题 + 科研项目的 Python 速查手册

## 目录结构

```
Python 学习指南/
├── 01-基础语法/        # 元组、函数、模块与包
├── 02-面向对象/        # 类与对象、接口、魔术方法
├── 03-文件与系统/      # 文件 IO、OS 操作
├── 04-数据处理/        # JSON、字符串、日期时间、正则
├── 05-数据库与网络/    # MySQL、SMTP 邮件、网络编程
├── 06-并发编程/        # 多线程、异步编程
├── 07-高级主题/        # GUI、Python2vs3、XML 解析
├── 08-工程化/          # 项目结构、生态地图、Docker
└── API 速查/           # 内置函数、字符串/集合/文件/日期 API
```

---

## 01-基础语法

### [元组.md](01-基础语法/元组.md)
**核心内容**：不可变序列，可哈希，可作为 dict key 和 set 元素

| 章节 | 内容 |
|------|------|
| 创建元组 | 基本创建、单元素元组、解包 |
| LeetCode 实战 | BFS/DFS visited 集合、DP 状态表示、多关键字排序 |
| 科研实战 | 模型返回多值、不可变配置、DataLoader 样本索引 |

### [函数.md](01-基础语法/函数.md)
**核心内容**：装饰器、*args/**kwargs、LRU cache

| 章节 | 内容 |
|------|------|
| 参数类型 | 位置参数、默认参数、可变参数 |
| LeetCode 实战 | 装饰器计时、LRU cache 记忆化搜索、回溯/滑动窗口模板 |
| 科研实战 | 训练函数封装、实验日志装饰器、配置创建模型 |

### [模块与包.md](01-基础语法/模块与包.md)
**核心内容**：导入机制、项目模块组织

| 章节 | 内容 |
|------|------|
| 导入方式 | import、from...import、相对导入 |
| LeetCode 实战 | 算法模板库组织 |
| 科研实战 | 科研项目模块组织、相对导入 vs 绝对导入 |

---

## 02-面向对象

### [类与对象.md](02-面向对象/类与对象.md)
**核心内容**：PyTorch nn.Module 继承、dataclass 配置

| 章节 | 内容 |
|------|------|
| 类的定义 | __init__、self、类属性 vs 实例属性 |
| LeetCode 实战 | ListNode、TreeNode、Interval（合并区间） |
| 科研实战 | PyTorch nn.Module 继承、dataclass 实验配置、ModelFactory 模式 |

### [接口与抽象类.md](02-面向对象/接口与抽象类.md)
**核心内容**：ABC 定义 Dataset/Model 接口

| 章节 | 内容 |
|------|------|
| ABC 语法 | @abstractmethod、抽象基类 |
| LeetCode 实战 | 策略模式、迭代器接口 |
| 科研实战 | Dataset 接口定义、Model 接口定义、Protocol 数据加载器接口 |

### [魔术方法.md](02-面向对象/魔术方法.md)
**核心内容**：__len__、__getitem__ 在 Dataset 中的实现

| 章节 | 内容 |
|------|------|
| 常用魔术方法 | __str__、__repr__、__len__、__getitem__、__eq__、__hash__ |
| LeetCode 实战 | LC 173 二叉搜索树迭代器、可哈希自定义对象、优先队列元素 |
| 科研实战 | 自定义 Dataset、Batch 数据类、实验结果排序 |

---

## 03-文件与系统

### [文件 IO.md](03-文件与系统/文件 IO.md)
**核心内容**：日志读写、CSV/JSON 保存、Checkpoint 保存

| 章节 | 内容 |
|------|------|
| 读写文件 | open()、with 语句、pathlib |
| LeetCode 实战 | 测试用例加载、结果文件写入 |
| 科研实战 | 训练日志读写、实验结果 CSV/JSON、CheckpointManager |

### [OS 操作.md](03-文件与系统/OS 操作.md)
**核心内容**：实验目录自动创建、环境变量读取

| 章节 | 内容 |
|------|------|
| 系统操作 | 文件/目录操作、环境变量、路径处理 |
| LeetCode 实战 | 文件遍历、批量处理 |
| 科研实战 | 实验目录自动创建、文件批量重命名、API key 读取、CUDA 设备配置 |

---

## 04-数据处理

### [JSON 处理.md](04-数据处理/JSON 处理.md)
**核心内容**：实验配置文件、超参数保存/加载

| 章节 | 内容 |
|------|------|
| JSON 操作 | json.load/dump、json.loads/dumps |
| LeetCode 实战 | API 响应解析 |
| 科研实战 | 实验配置文件、HyperParamManager、训练日志 JSON 保存 |

### [字符串操作.md](04-数据处理/字符串操作.md)
**核心内容**：日志解析、f-string 格式化训练输出

| 章节 | 内容 |
|------|------|
| 字符串方法 | 查找、替换、分割、连接、格式化 |
| LeetCode 实战 | LC 344/125/443/3 回文、匹配、滑动窗口 |
| 科研实战 | 训练日志解析、实验目录管理、TrainingLogger 格式化输出 |

### [日期时间.md](04-数据处理/日期时间.md)
**核心内容**：实验时间戳、训练耗时统计

| 章节 | 内容 |
|------|------|
| datetime 模块 | datetime、date、time、timedelta |
| LeetCode 实战 | LC 1360 日期差、日期格式转换 |
| 科研实战 | 实验时间戳命名、日志时间解析、TrainingTimer、检查点命名 |

### [正则表达式.md](04-数据处理/正则表达式.md)
**核心内容**：日志提取 loss/accuracy、文件名模式匹配

| 章节 | 内容 |
|------|------|
| re 模块 | 匹配、查找、替换、分割 |
| LeetCode 实战 | LC 10/65/125 字符串匹配、表达式验证 |
| 科研实战 | 训练日志提取、文件名模式匹配、数据清洗 |

---

## 05-数据库与网络

### [MySQL 连接.md](05-数据库与网络/MySQL 连接.md)
**核心内容**：实验结果持久化

| 章节 | 内容 |
|------|------|
| 数据库操作 | 连接、CRUD、事务、参数化查询 |
| 科研实战 | 实验结果持久化、TrainingManager 训练管理、ModelRegistry 模型版本管理 |

### [SMTP 邮件.md](05-数据库与网络/SMTP 邮件.md)
**核心内容**：训练完成自动发邮件通知

| 章节 | 内容 |
|------|------|
| 邮件发送 | smtplib、邮件格式、附件 |
| 科研实战 | 训练完成通知、异常告警 |

### [网络编程.md](05-数据库与网络/网络编程.md)
**核心内容**：API 调用、requests 库科研用途

| 章节 | 内容 |
|------|------|
| HTTP 请求 | requests、httpx、超时、重试 |
| 科研实战 | HuggingFace API、arXiv 论文爬取、批量 HTTP 请求、推理服务 API |

---

## 06-并发编程

### [多线程.md](06-并发编程/多线程.md)
**核心内容**：DataLoader 的 num_workers 原理、GIL 影响

| 章节 | 内容 |
|------|------|
| 线程基础 | threading、Lock、线程池 |
| GIL 影响 | CPU 密集 vs I/O 密集、多线程 vs 多进程选择 |
| 科研实战 | DataLoader num_workers 原理、并行实验评估、数据加载 |

### [异步编程.md](06-并发编程/异步编程.md)
**核心内容**：批量 LLM API 调用、异步数据下载

| 章节 | 内容 |
|------|------|
| asyncio | async/await、协程、aiohttp |
| 科研实战 | 批量 LLM API 调用、异步数据下载、并发爬虫 |

---

## 07-高级主题

### [GUI 编程.md](07-高级主题/GUI 编程.md)
**核心内容**：Gradio/Streamlit 快速可视化

| 章节 | 内容 |
|------|------|
| Gradio | 快速原型、模型演示 |
| Streamlit | 数据应用、可视化 |
| 科研实战 | 模型推理演示、超参数搜索工具 |

### [Python2vs3.md](07-高级主题/Python2vs3.md)
**核心内容**：历史差异（仅供了解，2026 年基本不需要）

| 章节 | 内容 |
|------|------|
| 主要差异 | print、除法、Unicode、range |

### [XML 解析.md](07-高级主题/XML 解析.md)
**核心内容**：PASCAL VOC 标注解析

| 章节 | 内容 |
|------|------|
| ElementTree | 解析、查找、修改 |
| 科研实战 | PASCAL VOC 标注解析、配置文件处理 |

---

## 08-工程化

### [项目结构.md](08-工程化/项目结构.md)
**核心内容**：科研项目标准目录结构

| 章节 | 内容 |
|------|------|
| 目录规范 | data/、models/、configs/、scripts/、notebooks/ |
| 科研实战 | 完整科研项目结构示例、数据管理规范 |

### [生态对照表.md](08-工程化/生态对照表.md)
**核心内容**：Python 科研/AI 生态地图

| 章节 | 内容 |
|------|------|
| 深度学习框架 | PyTorch、TensorFlow、JAX |
| 实验管理 | wandb、mlflow、hydra |
| 数据处理 | NumPy、Pandas、Polars |
| 模型部署 | ONNX、TensorRT、FastAPI |

### [Docker 部署.md](08-工程化/Docker 部署.md)
**核心内容**：科研环境 Docker 化、GPU 容器

| 章节 | 内容 |
|------|------|
| Dockerfile | 基础镜像、多阶段构建 |
| 科研实战 | GPU 容器配置、CUDA 环境、实验复现 |

---

## API 速查

### [内置函数.md](API 速查/内置函数.md)
| 章节 | 内容 |
|------|------|
| 类型转换 | int、float、str、list、tuple、dict |
| 数值操作 | abs、max、min、sum、pow、round |
| 序列操作 | len、range、enumerate、zip、sorted、reversed |
| LeetCode 实战 | enumerate 索引遍历、zip 矩阵转置 |

### [字符串 API.md](API 速查/字符串 API.md)
| 章节 | 内容 |
|------|------|
| 查找判断 | find、index、count、startswith、endswith |
| 转换修剪 | upper、lower、strip、replace |
| LeetCode 实战 | LC 14/242/3 字符串操作 |

### [集合 API.md](API 速查/集合 API.md)
| 章节 | 内容 |
|------|------|
| 集合操作 | add、remove、discard、union、intersection |
| LeetCode 实战 | LC 1/217/349/202/36 哈希表、去重、交集 |

### [文件 API.md](API 速查/文件 API.md)
| 章节 | 内容 |
|------|------|
| 文件读写 | open、read、write、readlines |
| LeetCode 实战 | 测试用例加载、结果保存 |

### [日期 API.md](API 速查/日期 API.md)
| 章节 | 内容 |
|------|------|
| datetime | date、time、datetime、timedelta |
| LeetCode 实战 | LC 1360/1185 日期计算 |
| 科研实战 | 学习率调度、实验时间记录 |

### [异常处理.md](API 速查/异常处理.md)
| 章节 | 内容 |
|------|------|
| 异常语法 | try/except/finally、raise、自定义异常 |
| LeetCode 实战 | 边界条件处理 |
| 科研实战 | 数据加载容错、API 重试机制 |

---

## 使用建议

1. **刷题时**：优先查看「LeetCode 实战场景」章节
2. **写科研代码时**：优先查看「科研实战场景」章节
3. **快速查 API**：直接查看「API 速查」目录

---

## 文件说明

- 所有文件已从「面向 Java 开发者」改写为「面向 LeetCode + 科研项目」
- 原 Java 对照内容已删除
- 新增大量 LeetCode 题号和科研代码示例
- 保持速查手册风格，简洁实用

---

*最后更新：2026-04-05*