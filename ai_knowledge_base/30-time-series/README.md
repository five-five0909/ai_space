# 30. 时间序列

> 师弟师妹们好！时间序列分析就是让AI能预测未来趋势和模式。今天咱们用大白话+公式+代码，彻底搞懂各种时间序列方法！

---

## ARIMA（自回归积分滑动平均）

### 这玩意儿到底是啥？
ARIMA是经典的时间序列模型！它结合了自回归（AR）、差分（I）和滑动平均（MA）三个部分，适合处理平稳时间序列。

### 核心公式推导
**AR(p)部分**：
$$
X_t = c + \sum_{i=1}^p \phi_i X_{t-i} + \epsilon_t
$$

**MA(q)部分**：
$$
X_t = \mu + \epsilon_t + \sum_{i=1}^q \theta_i \epsilon_{t-i}
$$

**ARIMA(p,d,q)**：
$$
(1 - \sum_{i=1}^p \phi_i L^i)(1 - L)^d X_t = c + (1 + \sum_{i=1}^q \theta_i L^i)\epsilon_t
$$

其中$L$是滞后算子，$d$是差分阶数。

**平稳性要求**：
- AR部分：特征根在单位圆外
- MA部分：总是平稳的
- 差分：使非平稳序列变平稳

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

class ARIMATorch(nn.Module):
    def __init__(self, p=1, d=1, q=1):
        super().__init__()
        self.p = p
        self.d = d
        self.q = q
        
        # AR参数
        if p > 0:
            self.ar_params = nn.Parameter(torch.randn(p) * 0.1)
        else:
            self.ar_params = None
            
        # MA参数  
        if q > 0:
            self.ma_params = nn.Parameter(torch.randn(q) * 0.1)
        else:
            self.ma_params = None
            
        self.constant = nn.Parameter(torch.tensor(0.0))
        
    def difference(self, x, d):
        """差分操作"""
        for _ in range(d):
            x = x[1:] - x[:-1]
        return x
    
    def inverse_difference(self, diff_x, original_x, d):
        """逆差分操作"""
        if d == 0:
            return diff_x
            
        # 从最后一个原始值开始重建
        result = [original_x[-d]]
        for i in range(len(diff_x)):
            result.append(result[-1] + diff_x[i])
        return torch.tensor(result[1:])
    
    def forward(self, x, steps=1):
        """
        x: 输入时间序列 [seq_len]
        steps: 预测步数
        """
        batch_size = x.size(0) if x.dim() > 1 else 1
        
        if x.dim() == 1:
            x = x.unsqueeze(0)
            
        predictions = []
        
        for b in range(batch_size):
            series = x[b]
            
            # 差分
            diff_series = self.difference(series, self.d)
            
            # 初始化预测
            pred_series = diff_series.tolist()
            
            # 逐步预测
            for step in range(steps):
                ar_part = 0
                if self.p > 0:
                    for i in range(min(self.p, len(pred_series))):
                        ar_part += self.ar_params[i] * pred_series[-(i+1)]
                        
                ma_part = 0
                if self.q > 0 and len(pred_series) >= self.q:
                    # 简化：假设残差为0
                    ma_part = 0
                    
                prediction = self.constant + ar_part + ma_part
                pred_series.append(prediction)
                
            # 逆差分
            if self.d > 0:
                final_pred = self.inverse_difference(
                    torch.tensor(pred_series[-steps:]), 
                    series, 
                    self.d
                )
            else:
                final_pred = torch.tensor(pred_series[-steps:])
                
            predictions.append(final_pred)
            
        return torch.stack(predictions)

# 使用statsmodels进行对比
def compare_arima_methods():
    # 生成模拟数据
    np.random.seed(42)
    t = np.arange(100)
    trend = 0.1 * t
    seasonal = 10 * np.sin(2 * np.pi * t / 12)
    noise = np.random.normal(0, 2, 100)
    data = trend + seasonal + noise
    
    # statsmodels ARIMA
    model_sm = ARIMA(data, order=(1, 1, 1))
    fitted_sm = model_sm.fit()
    forecast_sm = fitted_sm.forecast(steps=10)
    
    # PyTorch ARIMA
    model_torch = ARIMATorch(p=1, d=1, q=1)
    data_tensor = torch.tensor(data, dtype=torch.float32)
    forecast_torch = model_torch(data_tensor, steps=10)
    
    print("Statsmodels forecast:", forecast_sm[:5])
    print("PyTorch forecast:", forecast_torch[0][:5].detach().numpy())
    print("Difference:", np.abs(forecast_sm[:5] - forecast_torch[0][:5].detach().numpy()))

# 使用示例
compare_arima_methods()
```

### 推荐论文
1. Box & Jenkins, "Time Series Analysis: Forecasting and Control", 1970
2. Hyndman & Athanasopoulos, "Forecasting: principles and practice", 2018
3. Makridakis et al., "The M4 Competition: 100,000 time series and 61 forecasting methods", International Journal of Forecasting 2020

---

## LSTM for Time Series（LSTM时间序列）

### 这玩意儿到底是啥？
LSTM就是专门处理序列数据的神经网络！它通过门控机制记住长期依赖，特别适合时间序列预测。

### 核心公式推导
**遗忘门**：
$$
f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)
$$

**输入门**：
$$
i_t = \sigma(W_i [h_{t-1}, x_t] + b_i)
$$
$$
\tilde{C}_t = \tanh(W_C [h_{t-1}, x_t] + b_C)
$$

**细胞状态更新**：
$$
C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t
$$

**输出门**：
$$
o_t = \sigma(W_o [h_{t-1}, x_t] + b_o)
$$
$$
h_t = o_t \odot \tanh(C_t)
$$

**多步预测**：
- 单步：$y_t = W_y h_t$
- 多步：递归使用预测值作为输入

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class LSTMTimeSeries(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1, dropout=0.2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x, future_steps=0):
        """
        x: [batch_size, seq_len, input_size]
        future_steps: 要预测的未来步数
        """
        batch_size = x.size(0)
        
        # 初始隐藏状态
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        
        # 编码器：处理历史数据
        lstm_out, (hn, cn) = self.lstm(x, (h0, c0))
        
        if future_steps == 0:
            # 只预测下一步
            predictions = self.fc(lstm_out[:, -1:, :])
            return predictions.squeeze(-1)
        else:
            # 多步预测
            predictions = []
            current_input = x[:, -1:, :]  # 最后一个时间步
            current_hn, current_cn = hn, cn
            
            for _ in range(future_steps):
                output, (current_hn, current_cn) = self.lstm(current_input, (current_hn, current_cn))
                prediction = self.fc(output)
                predictions.append(prediction)
                current_input = prediction  # 使用预测值作为下一个输入
                
            predictions = torch.cat(predictions, dim=1)
            return predictions.squeeze(-1)

# 训练函数
def train_lstm_time_series(model, train_data, seq_len=50, epochs=100, lr=0.001):
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0
        
        for i in range(seq_len, len(train_data) - 1):
            # 准备输入和目标
            input_seq = train_data[i-seq_len:i].unsqueeze(0).unsqueeze(-1)
            target = train_data[i].unsqueeze(0)
            
            optimizer.zero_grad()
            output = model(input_seq)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
        if epoch % 20 == 0:
            avg_loss = total_loss / num_batches
            print(f"Epoch {epoch}, Loss: {avg_loss:.6f}")

# 使用示例
# 生成模拟时间序列数据
np.random.seed(42)
t = np.linspace(0, 100, 1000)
data = np.sin(t) + 0.1 * np.random.randn(1000)
train_data = torch.tensor(data[:800], dtype=torch.float32)
test_data = torch.tensor(data[800:], dtype=torch.float32)

# 创建和训练模型
lstm_model = LSTMTimeSeries(input_size=1, hidden_size=64, num_layers=2, output_size=1)
train_lstm_time_series(lstm_model, train_data, seq_len=50, epochs=100)

# 预测
lstm_model.eval()
with torch.no_grad():
    # 单步预测
    test_input = test_data[:50].unsqueeze(0).unsqueeze(-1)
    single_step_pred = lstm_model(test_input)
    
    # 多步预测
    multi_step_pred = lstm_model(test_input, future_steps=10)
    
print(f"Single step prediction shape: {single_step_pred.shape}")
print(f"Multi-step prediction shape: {multi_step_pred.shape}")
print(f"First few multi-step predictions: {multi_step_pred[0][:5].numpy()}")
```

### 推荐论文
1. Hochreiter & Schmidhuber, "Long Short-Term Memory", Neural Computation 1997
2. Gers et al., "Learning to Forget: Continual Prediction with LSTM", ICANN 1999
3. Makridakis et al., "Statistical and Machine Learning forecasting methods: Concerns and ways forward", PLOS ONE 2018

---

## Transformer for Time Series（Transformer时间序列）

### 这玩意儿到底是啥？
Transformer时间序列就是把Transformer架构应用到时间序列预测！它用自注意力机制捕捉长期依赖，避免了RNN的顺序计算瓶颈。

### 核心公式推导
**位置编码**：
$$
PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right)
$$
$$
PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)
$$

**自注意力**：
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

**时间特征嵌入**：
- 时间戳嵌入：年、月、日、小时等
- 位置嵌入：序列位置
- 值嵌入：时间序列值

**因果掩码**：
$$
M_{ij} = \begin{cases} 0 & \text{if } i \geq j \\ -\infty & \text{otherwise} \end{cases}
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import math

class TimeSeriesTransformer(nn.Module):
    def __init__(self, input_dim=1, d_model=128, nhead=8, num_layers=3, 
                 dropout=0.1, seq_len=100, pred_len=10):
        super().__init__()
        self.input_dim = input_dim
        self.d_model = d_model
        self.seq_len = seq_len
        self.pred_len = pred_len
        
        # 值嵌入
        self.value_embedding = nn.Linear(input_dim, d_model)
        
        # 位置编码
        self.pos_encoding = self._generate_positional_encoding(seq_len + pred_len, d_model)
        
        # 时间特征嵌入（简化版）
        self.time_embedding = nn.Embedding(24, d_model)  # 小时嵌入
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 输出投影
        self.output_projection = nn.Linear(d_model, input_dim)
        
        self.dropout = nn.Dropout(dropout)
        
    def _generate_positional_encoding(self, max_len, d_model):
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)
    
    def forward(self, x, future_times=None):
        """
        x: [batch_size, seq_len, input_dim]
        future_times: [batch_size, pred_len] 可选的未来时间特征
        """
        batch_size = x.size(0)
        
        # 值嵌入
        x_embedded = self.value_embedding(x)  # [batch, seq_len, d_model]
        
        # 位置编码
        pos_enc = self.pos_encoding[:, :self.seq_len, :].to(x.device)
        x_embedded = x_embedded + pos_enc
        
        # 时间特征嵌入（如果提供）
        if future_times is not None:
            time_embed = self.time_embedding(future_times % 24)
            x_embedded = x_embedded + time_embed
        
        x_embedded = self.dropout(x_embedded)
        
        # Transformer编码
        transformer_out = self.transformer(x_embedded)
        
        # 预测未来
        predictions = []
        current_input = transformer_out[:, -1:, :]  # 最后一个时间步
        
        for _ in range(self.pred_len):
            # 添加位置编码
            pos_idx = self.seq_len + len(predictions)
            current_pos_enc = self.pos_encoding[:, pos_idx:pos_idx+1, :].to(x.device)
            current_input_with_pos = current_input + current_pos_enc
            
            # Transformer前向传播
            current_output = self.transformer(current_input_with_pos)
            
            # 生成预测
            prediction = self.output_projection(current_output)
            predictions.append(prediction)
            
            # 更新输入（简化：只用预测值）
            current_input = self.value_embedding(prediction)
            
        predictions = torch.cat(predictions, dim=1)
        return predictions.squeeze(-1)

# 使用示例
# 生成模拟数据
np.random.seed(42)
t = np.linspace(0, 200, 1000)
data = np.sin(t) + 0.5 * np.sin(t/5) + 0.1 * np.random.randn(1000)

# 准备训练数据
def create_sequences(data, seq_len, pred_len):
    sequences = []
    targets = []
    for i in range(len(data) - seq_len - pred_len + 1):
        sequences.append(data[i:i+seq_len])
        targets.append(data[i+seq_len:i+seq_len+pred_len])
    return torch.tensor(sequences, dtype=torch.float32), torch.tensor(targets, dtype=torch.float32)

seq_len = 50
pred_len = 10
train_seq, train_target = create_sequences(data[:800], seq_len, pred_len)
test_seq, test_target = create_sequences(data[800:], seq_len, pred_len)

# 创建和训练模型
transformer_model = TimeSeriesTransformer(
    input_dim=1, d_model=64, nhead=4, num_layers=2, 
    seq_len=seq_len, pred_len=pred_len
)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(transformer_model.parameters(), lr=0.001)

# 训练
transformer_model.train()
for epoch in range(50):
    optimizer.zero_grad()
    output = transformer_model(train_seq.unsqueeze(-1))
    loss = criterion(output, train_target)
    loss.backward()
    optimizer.step()
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

# 测试
transformer_model.eval()
with torch.no_grad():
    test_pred = transformer_model(test_seq.unsqueeze(-1))
    test_loss = criterion(test_pred, test_target)
    print(f"Test Loss: {test_loss.item():.6f}")
    print(f"Prediction shape: {test_pred.shape}")
```

### 推荐论文
1. Lim et al., "Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting", IJF 2021
2. Wu et al., "Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting", NeurIPS 2021
3. Zhou et al., "Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting", AAAI 2021

---

## N-BEATS（神经基础扩展分析时间序列）

### 这玩意儿到底是啥？
N-BEATS就是专门为时间序列预测设计的深度学习架构！它使用堆叠的残差块，每个块都能学习趋势和季节性模式。

### 核心公式推导
**残差块**：
$$
\hat{y}_t = \sum_{k=1}^K g_\theta^{(k)}(x_t^{(k)})
$$
$$
x_t^{(k+1)} = x_t^{(k)} - \hat{y}_t^{(k)}
$$

**双头输出**：
- 趋势头：$\hat{y}_t^{\text{trend}} = \Theta^{\text{trend}} \cdot T$
- 季节性头：$\hat{y}_t^{\text{seasonal}} = \Theta^{\text{seasonal}} \cdot S$

其中$T$是趋势基函数，$S$是季节性基函数。

**可解释性**：
- 每个块可以专门学习趋势或季节性
- 残差连接确保总预测是各块预测的和

### PyTorch代码示例
```python
import torch
import torch.nn as nn

class NBeatsBlock(nn.Module):
    def __init__(self, input_size, theta_size, basis_size, layers, layer_size, dropout=0.1):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Linear(input_size if i == 0 else layer_size, layer_size)
            for i in range(layers)
        ])
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        
        # 背景层
        self.backcast_linear = nn.Linear(layer_size, theta_size)
        self.forecast_linear = nn.Linear(layer_size, theta_size)
        
        # 基函数
        self.backcast_basis = nn.Parameter(torch.randn(theta_size, input_size))
        self.forecast_basis = nn.Parameter(torch.randn(theta_size, basis_size))
        
    def forward(self, x):
        # 前向传播
        residual = x
        for layer in self.layers:
            residual = self.relu(layer(residual))
            residual = self.dropout(residual)
            
        # 背景和预测
        theta_backcast = self.backcast_linear(residual)
        theta_forecast = self.forecast_linear(residual)
        
        backcast = torch.einsum('bt,tf->bf', theta_backcast, self.backcast_basis)
        forecast = torch.einsum('bt,tf->bf', theta_forecast, self.forecast_basis)
        
        return backcast, forecast

class NBeats(nn.Module):
    def __ __init__(self, input_size=10, output_size=5, stack_types=['trend', 'seasonal'], 
                  nb_blocks_per_stack=3, layers=4, layer_size=512, dropout=0.1):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size
        
        # 计算基函数大小
        trend_basis_size = min(input_size, output_size) + 1
        seasonal_basis_size = output_size
        
        self.stacks = nn.ModuleList()
        for stack_type in stack_types:
            blocks = nn.ModuleList()
            for block_id in range(nb_blocks_per_stack):
                if stack_type == 'trend':
                    block = NBeatsBlock(
                        input_size=input_size,
                        theta_size=trend_basis_size,
                        basis_size=output_size,
                        layers=layers,
                        layer_size=layer_size,
                        dropout=dropout
                    )
                else:  # seasonal
                    block = NBeatsBlock(
                        input_size=input_size,
                        theta_size=seasonal_basis_size,
                        basis_size=output_size,
                        layers=layers,
                        layer_size=layer_size,
                        dropout=dropout
                    )
                blocks.append(block)
            self.stacks.append(blocks)
            
    def forward(self, x):
        """
        x: [batch_size, input_size]
        """
        residuals = x
        forecast = torch.zeros(x.size(0), self.output_size).to(x.device)
        
        for stack in self.stacks:
            for block in stack:
                backcast, block_forecast = block(residuals)
                residuals = residuals - backcast
                forecast = forecast + block_forecast
                
        return forecast

# 使用示例
# 生成模拟数据
np.random.seed(42)
t = np.linspace(0, 100, 1000)
trend = 0.01 * t**2
seasonal = 10 * np.sin(2 * np.pi * t / 12) + 5 * np.sin(2 * np.pi * t / 4)
noise = np.random.normal(0, 1, 1000)
data = trend + seasonal + noise

# 准备数据
def create_nbeats_data(data, input_size=50, output_size=10):
    X, y = [], []
    for i in range(len(data) - input_size - output_size + 1):
        X.append(data[i:i+input_size])
        y.append(data[i+input_size:i+input_size+output_size])
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

input_size = 50
output_size = 10
X_train, y_train = create_nbeats_data(data[:800], input_size, output_size)
X_test, y_test = create_nbeats_data(data[800:], input_size, output_size)

# 创建和训练模型
nbeats_model = NBeats(
    input_size=input_size,
    output_size=output_size,
    stack_types=['trend', 'seasonal'],
    nb_blocks_per_stack=3,
    layers=4,
    layer_size=256
)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(nbeats_model.parameters(), lr=0.001)

# 训练
nbeats_model.train()
for epoch in range(100):
    optimizer.zero_grad()
    output = nbeats_model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()
    
    if epoch % 20 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

# 测试
nbeats_model.eval()
with torch.no_grad():
    test_pred = nbeats_model(X_test)
    test_loss = criterion(test_pred, y_test)
    print(f"Test Loss: {test_loss.item():.6f}")
    print(f"Prediction shape: {test_pred.shape}")
    
    # 可视化第一个样本的预测
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(range(input_size), X_test[0].numpy(), 'b-', label='Input')
    plt.plot(range(input_size, input_size+output_size), y_test[0].numpy(), 'g-', label='True')
    plt.plot(range(input_size, input_size+output_size), test_pred[0].numpy(), 'r--', label='Predicted')
    plt.legend()
    plt.title('N-BEATS Time Series Prediction')
    plt.show()
```

### 推荐论文
1. Oreshkin et al., "N-BEATS: Neural basis expansion analysis for interpretable time series forecasting", ICLR 2020
2. Alexandrov et al., "GluonTS: Probabilistic and Neural Time Series Modeling in Python", JMLR 2020
3. Bandara et al., "An Encoder-Decoder Approach for Multivariate Time Series Forecasting with Exogenous Variables", ICDM 2022

---
> 时间序列分析让AI能预测未来！ARIMA是经典统计方法，LSTM擅长捕捉长期依赖，Transformer处理长序列更高效，N-BEATS专门针对时间序列设计。记住：没有最好的方法，只有最适合你数据的方法！