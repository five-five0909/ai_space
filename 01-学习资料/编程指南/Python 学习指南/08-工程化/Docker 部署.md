# Docker 部署

## 基础概念

```bash
# 构建镜像
docker build -t my-pytorch:latest .

# 运行容器
docker run --rm -it my-pytorch:latest
```

## Dockerfile 示例

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "train.py"]
```

## 科研实战场景

### 1. GPU 容器运行

```bash
# NVIDIA GPU
docker run --gpus all -it my-pytorch:latest

# 共享内存（多进程数据加载）
docker run --gpus all --shm-size=16g -it my-pytorch:latest
```

### 2. 数据卷挂载

```bash
docker run \
  -v /host/data:/data \
  -v /host/models:/models \
  -v /host/results:/results \
  -it my-image
```

### 3. Docker Compose

```yaml
version: '3.8'

services:
  training:
    build: .
    volumes:
      - ./data:/app/data
      - ./experiments:/app/experiments
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 性能优化

### 层缓存优化

```dockerfile
# 先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制代码
COPY . .
```

### .dockerignore

```
__pycache__/
*.pyc
.git/
.experiments/
```
