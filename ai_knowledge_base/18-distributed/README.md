# 18. 分布式训练

> 师弟师妹们好！分布式训练就是让多个GPU一起干活，把大模型训练时间从几周缩短到几天。今天咱们用大白话+公式+代码，彻底搞懂各种分布式方法！

---

## Data Parallelism (数据并行)

### 这玩意儿到底是啥？
最简单的分布式方法！每个GPU都有一份完整的模型，但处理不同的数据批次。计算完梯度后，把所有GPU的梯度平均一下，再更新模型。

### 核心公式推导
**梯度同步**：
$$
g_{\text{global}} = \frac{1}{N} \sum_{i=1}^N g_i
$$

其中$g_i$是第i个GPU的梯度，$N$是GPU数量。

**All-Reduce操作**：
- 每个GPU计算本地梯度$g_i$
- 所有GPU执行All-Reduce操作
- 每个GPU得到全局平均梯度$g_{\text{global}}$
- 各自独立更新模型参数

**通信开销**：
- 通信量：$O(P)$，其中$P$是参数数量
- 通信次数：每个batch一次
- 通信时间：$T_{\text{comm}} = \alpha + \beta \cdot P$

### PyTorch代码示例
```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP

def setup(rank, world_size):
    """初始化分布式环境"""
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def cleanup():
    """清理分布式环境"""
    dist.destroy_process_group()

def train(rank, world_size):
    """单个GPU的训练函数"""
    setup(rank, world_size)
    
    # 创建模型
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    
    # 创建优化器
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.01)
    
    # 创建数据加载器
    dataset = MyDataset()
    sampler = torch.utils.data.distributed.DistributedSampler(
        dataset, num_replicas=world_size, rank=rank
    )
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=32, sampler=sampler
    )
    
    # 训练循环
    for epoch in range(100):
        sampler.set_epoch(epoch)  # 确保每个epoch数据不同
        for batch in dataloader:
            inputs, targets = batch
            inputs, targets = inputs.to(rank), targets.to(rank)
            
            optimizer.zero_grad()
            outputs = ddp_model(inputs)
            loss = F.cross_entropy(outputs, targets)
            loss.backward()
            optimizer.step()
    
    cleanup()

if __name__ == "__main__":
    world_size = torch.cuda.device_count()
    mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)
```

### 推荐论文
1. Dean et al., "Large Scale Distributed Deep Networks", NIPS 2012
2. Li et al., "Scaling Distributed Machine Learning with the Parameter Server", OSDI 2014
3. Sergeev & Del Balso, "Horovod: Fast and Easy Distributed Deep Learning in TensorFlow", arXiv 2018

---

## Model Parallelism (模型并行)

### 这玩意儿到底是啥？
当模型太大，一个GPU放不下时，就把模型拆成几块，每块放在不同的GPU上。前向传播时，数据在GPU间传递；反向传播时，梯度也要传递。

### 核心公式推导
**张量切分**：
假设权重矩阵$W \in \mathbb{R}^{m \times n}$，在第0维切分：
$$
W = \text{concat}(W_1, W_2, ..., W_k)
$$

其中$W_i \in \mathbb{R}^{m_i \times n}$，$\sum m_i = m$。

**前向传播**：
$$
y = xW = x \cdot \text{concat}(W_1, ..., W_k) = \text{concat}(xW_1, ..., xW_k)
$$

**反向传播**：
$$
\frac{\partial L}{\partial W_i} = x^T \frac{\partial L}{\partial y_i}
$$

**通信模式**：
- 前向：不需要通信（如果输入x广播到所有GPU）
- 反向：需要All-Gather梯度

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from torch.distributed import rpc

class ModelParallelModel(nn.Module):
    def __init__(self, device_list):
        super().__init__()
        self.device_list = device_list
        self.layers = nn.ModuleList([
            nn.Linear(1000, 1000).to(device_list[0]),
            nn.ReLU().to(device_list[0]),
            nn.Linear(1000, 1000).to(device_list[1]),
            nn.ReLU().to(device_list[1]),
            nn.Linear(1000, 10).to(device_list[2])
        ])
        
    def forward(self, x):
        # 第一层在device 0
        x = x.to(self.device_list[0])
        x = self.layers[0](x)
        x = self.layers[1](x)
        
        # 传递到device 1
        x = x.to(self.device_list[1])
        x = self.layers[2](x)
        x = self.layers[3](x)
        
        # 传递到device 2
        x = x.to(self.device_list[2])
        x = self.layers[4](x)
        
        return x

# 使用示例
device_list = ['cuda:0', 'cuda:1', 'cuda:2']
model = ModelParallelModel(device_list)
input_data = torch.randn(64, 1000)
output = model(input_data)
```

### 推荐论文
1. Shoeybi et al., "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", arXiv 2019
2. Narayanan et al., "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", SC 2021
3. Xu et al., "PipeDream: Generalized Pipeline Parallelism for DNN Training", SOSP 2019

---

## Pipeline Parallelism (流水线并行)

### 这玩意儿到底是啥？
把模型按层切分，不同GPU负责不同的层。像工厂流水线一样，数据一批批地流过各个GPU，提高GPU利用率。

### 核心公式推导
**微批次（Micro-batch）**：
将一个大batch分成$M$个小micro-batch：
$$
B = \{b_1, b_2, ..., b_M\}
$$

**流水线调度**：
- 时间步$t$，GPU$i$处理micro-batch $b_{t-i+1}$
- 需要$P + M - 1$个时间步完成一个完整batch
- 其中$P$是pipeline stages数

**气泡问题**：
- 前$P-1$个时间步和后$P-1$个时间步有空闲GPU
- 气泡比例：$\frac{2(P-1)}{P + M - 1}$
- 解决方案：增加$M$或使用1F1B调度

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from torch.distributed.pipeline.sync import Pipe

class Layer1(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1000, 1000)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        return self.relu(self.linear(x))

class Layer2(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1000, 1000)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        return self.relu(self.linear(x))

class Layer3(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1000, 10)
        
    def forward(self, x):
        return self.linear(x)

# 创建流水线模型
model = nn.Sequential(
    Layer1(),
    Layer2(),
    Layer3()
)

# 转换为流水线模型
pipe = Pipe(model, balance=[1, 1, 1], devices=['cuda:0', 'cuda:1', 'cuda:2'], chunks=8)

# 训练
input_data = torch.randn(64, 1000)
output = pipe(input_data)
loss = F.cross_entropy(output, target)
loss.backward()
```

### 推荐论文
1. Huang et al., "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism", NeurIPS 2019
2. Narayanan et al., "PipeDream: Generalized Pipeline Parallelism for DNN Training", SOSP 2019
3. Narayanan et al., "Memory-Efficient Pipeline-Parallel DNN Training", ICML 2021

---

## ZeRO (Zero Redundancy Optimizer)

### 这玩意儿到底是啥？
ZeRO通过分片优化器状态、梯度和参数来减少内存占用。核心思想是：不是每个GPU都存完整的副本，而是只存自己负责的那一部分。

### 核心公式推导
**ZeRO Stage 1**（优化器状态分片）：
- 优化器状态$O = \{m, v\}$被分片到$N$个GPU
- 每个GPU只存储$\frac{1}{N}$的优化器状态
- 内存节省：$12P \to 4P + \frac{8P}{N}$（Adam优化器）

**ZeRO Stage 2**（梯度分片）：
- 梯度$g$也被分片
- 每个GPU只存储$\frac{1}{N}$的梯度
- 内存节省：$16P \to 4P + \frac{12P}{N}$

**ZeRO Stage 3**（参数分片）：
- 模型参数$W$也被分片
- 前向/反向传播时按需收集参数
- 内存节省：$18P \to 2P + \frac{16P}{N}$

其中$P$是参数数量（以字节计）。

### PyTorch代码示例
```python
from deepspeed import DeepSpeedConfig, deepspeed

# DeepSpeed配置
ds_config = {
    "train_batch_size": 32,
    "optimizer": {
        "type": "Adam",
        "params": {
            "lr": 0.001,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        }
    },
    "fp16": {
        "enabled": True,
        "loss_scale": 0,
        "initial_scale_power": 16
    },
    "zero_optimization": {
        "stage": 3,  # ZeRO Stage 3
        "offload_optimizer": {
            "device": "cpu"
        },
        "offload_param": {
            "device": "cpu"
        }
    }
}

# 初始化DeepSpeed引擎
model = MyModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    optimizer=optimizer,
    config=ds_config
)

# 训练循环
for batch in dataloader:
    inputs, targets = batch
    outputs = model_engine(inputs)
    loss = F.cross_entropy(outputs, targets)
    model_engine.backward(loss)
    model_engine.step()
```

### 推荐论文
1. Rajbhandari et al., "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", SC 2020
2. Rajbhandari et al., "ZeRO-Offload: Democratizing Billion-Scale Model Training", USENIX ATC 2021
3. Aminabadi et al., "ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning", SC 2021

---

## FSDP (Fully Sharded Data Parallel)

### 这玩意儿到底是啥？
PyTorch原生的ZeRO实现！FSDP在数据并行的基础上，对模型参数、梯度和优化器状态进行分片，大幅减少内存占用。

### 核心公式推导
**参数分片**：
模型参数$W$被均匀分片到$N$个GPU：
$$
W = \bigcup_{i=1}^N W_i, \quad |W_i| = \frac{|W|}{N}
$$

**All-Gather操作**：
- 前向传播前：All-Gather收集完整参数
- 前向传播后：释放完整参数，只保留分片
- 反向传播前：All-Gather收集完整参数
- 反向传播后：计算本地梯度，然后Reduce-Scatter

**内存复杂度**：
- 标准DDP：$O(P)$
- FSDP：$O(\frac{P}{N})$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.fully_sharded_data_parallel import CPUOffload

def setup_fsdp():
    """设置FSDP"""
    model = MyModel()
    
    # 包装为FSDP
    fsdp_model = FSDP(
        model,
        cpu_offload=CPUOffload(offload_params=True),  # 参数卸载到CPU
        mixed_precision=torch.float16  # 混合精度
    )
    
    return fsdp_model

def train_fsdp():
    """FSDP训练"""
    model = setup_fsdp()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(100):
        for batch in dataloader:
            inputs, targets = batch
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = F.cross_entropy(outputs, targets)
            loss.backward()
            optimizer.step()

# 启动分布式训练
torch.multiprocessing.spawn(
    train_fsdp,
    args=(),
    nprocs=torch.cuda.device_count(),
    join=True
)
```

### 推荐论文
1. Zhao et al., "PyTorch FSDP: Flexible and Scalable Model Parallelism for Training Large Models", arXiv 2023
2. Rajbhandari et al., "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", SC 2020
3. Narayanan et al., "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", SC 2021

---
> 分布式训练是个系统工程！数据并行适合小模型，模型并行适合超大模型，流水线并行提高GPU利用率，ZeRO/FSDP大幅减少内存占用。记住：没有最好的方法，只有最适合你硬件和模型的方法！