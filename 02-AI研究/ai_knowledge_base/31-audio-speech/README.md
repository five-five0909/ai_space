# 31. 音频与语音

> 师弟师妹们好！音频和语音处理让AI能听懂和说话。今天咱们用大白话+公式+代码，彻底搞懂各种音频语音方法！

---

## WaveNet（波形网络）

### 这玩意儿到底是啥？
WaveNet就是直接生成原始音频波形的深度网络！它用因果卷积和扩张卷积来捕捉音频的长期依赖。

### 核心公式推导
**因果卷积**：
$$
y_t = \sum_{k=1}^K w_k x_{t-k}
$$

**扩张卷积**：
$$
y_t = \sum_{k=0}^{K-1} w_k x_{t - d \cdot k}
$$

其中$d$是扩张率。

**门控激活**：
$$
z = \tanh(W_{f,k} * x) \odot \sigma(W_{g,k} * x)
$$

**残差连接**：
$$
x_{\text{out}} = z + x_{\text{skip}}
$$

**多层堆叠**：
每个层的扩张率成指数增长：$d = 2^l$，其中$l$是层数。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class CausalDilatedConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation, bias=True):
        super().__init__()
        self.kernel_size = kernel_size
        self.dilation = dilation
        
        # 因果填充
        self.padding = (kernel_size - 1) * dilation
        
        self.conv = nn.Conv1d(
            in_channels, 
            out_channels * 2,  # 用于门控
            kernel_size,
            padding=self.padding,
            dilation=dilation,
            bias=bias
        )
        
    def forward(self, x):
        # 因果卷积
        out = self.conv(x)
        
        # 移除因果填充
        if self.padding != 0:
            out = out[:, :, :-self.padding]
            
        # 门控机制
        filter_out, gate_out = torch.chunk(out, 2, dim=1)
        return torch.tanh(filter_out) * torch.sigmoid(gate_out)

class WaveNetBlock(nn.Module):
    def __init__(self, residual_channels, skip_channels, kernel_size, dilation):
        super().__init__()
        self.dilated_conv = CausalDilatedConv1d(
            residual_channels, residual_channels, kernel_size, dilation
        )
        
        self.residual_conv = nn.Conv1d(residual_channels, residual_channels, 1)
        self.skip_conv = nn.Conv1d(residual_channels, skip_channels, 1)
        
    def forward(self, x):
        residual = x
        dilated_out = self.dilated_conv(x)
        
        # 残差连接
        residual_out = self.residual_conv(dilated_out)
        residual_out = residual_out + residual
        
        # 跳跃连接
        skip_out = self.skip_conv(dilated_out)
        
        return residual_out, skip_out

class WaveNet(nn.Module):
    def __init__(self, vocab_size=256, residual_channels=32, skip_channels=256, 
                 kernel_size=2, n_layers=10, n_stacks=2):
        super().__init__()
        self.vocab_size = vocab_size
        self.n_layers = n_layers
        self.n_stacks = n_stacks
        
        # 输入嵌入
        self.input_embedding = nn.Embedding(vocab_size, residual_channels)
        
        # WaveNet块堆叠
        self.blocks = nn.ModuleList()
        for stack in range(n_stacks):
            for layer in range(n_layers):
                dilation = 2 ** layer
                self.blocks.append(
                    WaveNetBlock(residual_channels, skip_channels, kernel_size, dilation)
                )
                
        # 输出层
        self.output_conv1 = nn.Conv1d(skip_channels, skip_channels, 1)
        self.output_conv2 = nn.Conv1d(skip_channels, vocab_size, 1)
        
    def forward(self, x):
        """
        x: [batch_size, seq_len] - 量化后的音频样本
        """
        # 输入嵌入
        x = self.input_embedding(x)  # [batch, seq_len, residual_channels]
        x = x.transpose(1, 2)  # [batch, residual_channels, seq_len]
        
        # 通过所有块
        skip_connections = []
        for block in self.blocks:
            x, skip = block(x)
            skip_connections.append(skip)
            
        # 合并跳跃连接
        skip_sum = torch.sum(torch.stack(skip_connections), dim=0)
        
        # 输出层
        output = F.relu(skip_sum)
        output = self.output_conv1(output)
        output = F.relu(output)
        output = self.output_conv2(output)
        
        return output.transpose(1, 2)  # [batch, seq_len, vocab_size]

# 使用示例
# 生成模拟音频数据（8位量化）
batch_size = 4
seq_len = 1000
vocab_size = 256

audio_data = torch.randint(0, vocab_size, (batch_size, seq_len))

wavenet = WaveNet(vocab_size=vocab_size, residual_channels=32, skip_channels=256, n_layers=10, n_stacks=2)
output = wavenet(audio_data)

print(f"Input shape: {audio_data.shape}")
print(f"Output shape: {output.shape}")
print(f"Output min/max: {output.min():.4f}, {output.max():.4f}")

# 计算损失
target = audio_data[:, 1:]  # 下一个时间步
pred = output[:, :-1, :]    # 预测分布

criterion = nn.CrossEntropyLoss()
loss = criterion(pred.reshape(-1, vocab_size), target.reshape(-1))
print(f"Loss: {loss.item():.6f}")
```

### 推荐论文
1. van den Oord et al., "WaveNet: A Generative Model for Raw Audio", arXiv 2016
2. Mehri et al., "SampleRNN: An Unconditional End-to-End Neural Audio Generation Model", ICLR 2017
3. Ping et al., "Deep Voice 3: Scaling Text-to-Speech with Convolutional Sequence Learning", ICLR 2018

---

## Whisper（语音识别）

### 这玩意儿到底是啥？
Whisper是OpenAI开发的通用语音识别模型！它能处理多种语言、口音和音频质量，支持语音转文本、翻译等任务。

### 核心公式推导
**编码器-解码器架构**：
- 编码器：Transformer编码器处理音频特征
- 解码器：Transformer解码器生成文本

**音频特征提取**：
$$
X = \text{Log-Mel}(S)
$$

其中$S$是STFT（短时傅里叶变换）结果。

**多任务学习**：
- 语音识别：$P(y|x, \text{language})$
- 语音翻译：$P(y|x, \text{translate to English})$
- 语言识别：$P(\text{language}|x)$

**零样本迁移**：
通过提示工程实现零样本能力：
$$
\text{prompt} = \text{"Transcribe the following audio in Spanish:"}
$$

### PyTorch代码示例
```python
import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class WhisperASR:
    def __init__(self, model_name="openai/whisper-small"):
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.model.eval()
        
    def transcribe_audio(self, audio_path, language=None, task="transcribe"):
        """转录音频"""
        # 加载音频
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # 重采样到16kHz
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
            
        # 处理音频
        inputs = self.processor(
            waveform.squeeze(), 
            sampling_rate=16000, 
            return_tensors="pt"
        )
        
        # 生成配置
        gen_kwargs = {"max_new_tokens": 256}
        if language:
            gen_kwargs["language"] = language
        if task == "translate":
            gen_kwargs["task"] = "translate"
            
        # 生成文本
        with torch.no_grad():
            predicted_ids = self.model.generate(
                inputs.input_features, 
                **gen_kwargs
            )
            
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription[0]
    
    def batch_transcribe(self, audio_paths, languages=None, tasks=None):
        """批量转录"""
        transcriptions = []
        for i, audio_path in enumerate(audio_paths):
            lang = languages[i] if languages else None
            task = tasks[i] if tasks else "transcribe"
            transcription = self.transcribe_audio(audio_path, lang, task)
            transcriptions.append(transcription)
        return transcriptions

# 使用示例（需要实际音频文件）
# whisper_asr = WhisperASR("openai/whisper-base")

# # 单个音频转录
# transcription = whisper_asr.transcribe_audio("sample.wav", language="en")
# print(f"Transcription: {transcription}")

# # 语音翻译
# translation = whisper_asr.transcribe_audio("spanish_sample.wav", task="translate")
# print(f"Translation: {translation}")

# # 批量处理
# audio_files = ["file1.wav", "file2.wav", "file3.wav"]
# languages = ["en", "es", "fr"]
# transcriptions = whisper_asr.batch_transcribe(audio_files, languages)
# for i, trans in enumerate(transcriptions):
#     print(f"File {i+1}: {trans}")

# 模拟音频处理
def simulate_whisper_processing():
    """模拟Whisper的音频处理流程"""
    # 生成模拟音频
    sample_rate = 16000
    duration = 5  # 5秒
    t = torch.linspace(0, duration, int(sample_rate * duration))
    audio = torch.sin(2 * torch.pi * 440 * t) + 0.1 * torch.randn_like(t)  # 440Hz正弦波 + 噪声
    
    # STFT
    n_fft = 400
    hop_length = 160
    stft = torch.stft(audio, n_fft=n_fft, hop_length=hop_length, return_complex=True)
    
    # Log-Mel谱图
    mel_filters = torchaudio.transforms.MelScale(
        n_mels=80, 
        sample_rate=sample_rate, 
        f_min=0, 
        f_max=8000,
        n_stft=n_fft//2+1
    )
    mel_spec = mel_filters(torch.abs(stft)**2)
    log_mel = torch.log(mel_spec + 1e-9)
    
    print(f"Audio shape: {audio.shape}")
    print(f"STFT shape: {stft.shape}")
    print(f"Log-Mel shape: {log_mel.shape}")
    
    return log_mel

log_mel_features = simulate_whisper_processing()
```

### 推荐论文
1. Radford et al., "Robust Speech Recognition via Large-Scale Weak Supervision", ICML 2023
2. Gulati et al., "Conformer: Convolution-augmented Transformer for Speech Recognition", Interspeech 2020
3. Baevski et al., "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations", NeurIPS 2020

---

## Tacotron 2（语音合成）

### 这玩意儿到底是啥？
Tacotron 2就是端到端的文本到语音合成系统！它先生成梅尔谱图，再用WaveNet将其转换为原始音频。

### 核心公式推导
**编码器**：
$$
h = \text{Encoder}(x)
$$

**注意力机制**：
$$
a_t = \text{Attention}(h, s_{t-1})
$$
$$
c_t = \sum_i a_{t,i} h_i
$$

**解码器**：
$$
s_t = \text{Decoder}(s_{t-1}, c_t, y_{t-1})
$$
$$
\hat{m}_t = W s_t
$$

**后处理网络**：
$$
\hat{y} = \text{PostNet}(\hat{M})
$$

**两阶段训练**：
1. 训练Tacotron 2生成梅尔谱图
2. 训练WaveNet将梅尔谱图转换为音频

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Tacotron2Encoder(nn.Module):
    def __init__(self, vocab_size, embedding_dim=512, encoder_dim=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.convolutions = nn.Sequential(
            nn.Conv1d(embedding_dim, encoder_dim, kernel_size=5, padding=2),
            nn.BatchNorm1d(encoder_dim),
            nn.ReLU(),
            nn.Conv1d(encoder_dim, encoder_dim, kernel_size=5, padding=2),
            nn.BatchNorm1d(encoder_dim),
            nn.ReLU(),
            nn.Conv1d(encoder_dim, encoder_dim, kernel_size=5, padding=2),
            nn.BatchNorm1d(encoder_dim),
            nn.ReLU()
        )
        self.lstm = nn.LSTM(encoder_dim, encoder_dim//2, num_layers=1, batch_first=True, bidirectional=True)
        
    def forward(self, x):
        """
        x: [batch_size, seq_len]
        """
        embedded = self.embedding(x)  # [batch, seq_len, embedding_dim]
        conv_out = self.convolutions(embedded.transpose(1, 2))  # [batch, encoder_dim, seq_len]
        lstm_out, _ = self.lstm(conv_out.transpose(1, 2))  # [batch, seq_len, encoder_dim]
        return lstm_out

class LocationSensitiveAttention(nn.Module):
    def __init__(self, attention_dim=128, attention_location_n_filters=32, attention_location_kernel_size=31):
        super().__init__()
        self.query_layer = nn.Linear(1024, attention_dim, bias=False)
        self.memory_layer = nn.Linear(512, attention_dim, bias=False)
        self.v = nn.Linear(attention_dim, 1, bias=False)
        
        self.location_layer = nn.Conv1d(
            2, attention_location_n_filters,
            kernel_size=attention_location_kernel_size, 
            padding=int((attention_location_kernel_size - 1) / 2),
            bias=False, stride=1, dilation=1
        )
        self.location_dense = nn.Linear(attention_location_n_filters, attention_dim, bias=False)
        
    def forward(self, query, memory, processed_memory, attention_weights_cat):
        """
        query: [batch_size, 1, decoder_dim]
        memory: [batch_size, max_time, encoder_dim]
        processed_memory: [batch_size, max_time, attention_dim]
        attention_weights_cat: [batch_size, 2, max_time]
        """
        processed_query = self.query_layer(query.squeeze(1)).unsqueeze(1)  # [batch, 1, attention_dim]
        
        # 位置敏感特征
        processed_loc = self.location_layer(attention_weights_cat)
        processed_loc = processed_loc.transpose(1, 2)
        processed_loc = self.location_dense(processed_loc)
        
        # 注意力得分
        energies = self.v(torch.tanh(processed_query + processed_memory + processed_loc))
        energies = energies.squeeze(-1)  # [batch, max_time]
        
        # 注意力权重
        attention_weights = F.softmax(energies, dim=1)
        attention_context = torch.bmm(attention_weights.unsqueeze(1), memory)
        attention_context = attention_context.squeeze(1)
        
        return attention_context, attention_weights

class Tacotron2Decoder(nn.Module):
    def __init__(self, n_mel_channels=80, n_frames_per_step=1, encoder_embedding_dim=512, 
                 decoder_dim=1024, max_decoder_steps=1000):
        super().__init__()
        self.n_mel_channels = n_mel_channels
        self.n_frames_per_step = n_frames_per_step
        self.encoder_embedding_dim = encoder_embedding_dim
        self.decoder_dim = decoder_dim
        self.max_decoder_steps = max_decoder_steps
        
        self.prenet = nn.Sequential(
            nn.Linear(n_mel_channels * n_frames_per_step, decoder_dim),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(decoder_dim, decoder_dim),
            nn.ReLU(),
            nn.Dropout(0.5)
        )
        
        self.attention_rnn = nn.LSTMCell(decoder_dim + encoder_embedding_dim, decoder_dim)
        self.attention_layer = LocationSensitiveAttention()
        
        self.decoder_rnn = nn.LSTMCell(decoder_dim + encoder_embedding_dim, decoder_dim)
        
        self.linear_projection = nn.Linear(decoder_dim + encoder_embedding_dim, 
                                        n_mel_channels * n_frames_per_step)
        self.gate_layer = nn.Linear(decoder_dim + encoder_embedding_dim, 1)
        
    def forward(self, memory, decoder_inputs, memory_lengths):
        """
        memory: [batch_size, max_time, encoder_embedding_dim]
        decoder_inputs: [batch_size, mel_bins, T_out]
        """
        batch_size = memory.size(0)
        
        # 初始化
        attention_hidden = torch.zeros(batch_size, self.decoder_dim).to(memory.device)
        attention_cell = torch.zeros(batch_size, self.decoder_dim).to(memory.device)
        decoder_hidden = torch.zeros(batch_size, self.decoder_dim).to(memory.device)
        decoder_cell = torch.zeros(batch_size, self.decoder_dim).to(memory.device)
        
        attention_weights = torch.zeros(batch_size, memory.size(1)).to(memory.device)
        attention_weights_cum = torch.zeros(batch_size, memory.size(1)).to(memory.device)
        attention_context = torch.zeros(batch_size, self.encoder_embedding_dim).to(memory.device)
        
        # 处理记忆
        processed_memory = self.attention_layer.memory_layer(memory)
        
        mel_outputs, gate_outputs, alignments = [], [], []
        
        # 解码循环
        for i in range(decoder_inputs.size(2) // self.n_frames_per_step):
            # Prenet
            decoder_input = decoder_inputs[:, :, i*self.n_frames_per_step:(i+1)*self.n_frames_per_step]
            decoder_input = decoder_input.view(batch_size, -1)
            decoder_input = self.prenet(decoder_input)
            
            # 注意力RNN
            cell_input = torch.cat((decoder_input, attention_context), -1)
            attention_hidden, attention_cell = self.attention_rnn(
                cell_input, (attention_hidden, attention_cell)
            )
            attention_hidden = F.dropout(attention_hidden, 0.1)
            
            # 注意力机制
            attention_weights_cat = torch.cat(
                (attention_weights.unsqueeze(1), attention_weights_cum.unsqueeze(1)), dim=1
            )
            attention_context, attention_weights = self.attention_layer(
                attention_hidden.unsqueeze(1), memory, processed_memory, attention_weights_cat
            )
            attention_weights_cum += attention_weights
            
            # 解码器RNN
            decoder_input = torch.cat((attention_hidden, attention_context), -1)
            decoder_hidden, decoder_cell = self.decoder_rnn(
                decoder_input, (decoder_hidden, decoder_cell)
            )
            decoder_hidden = F.dropout(decoder_hidden, 0.1)
            
            # 输出投影
            decoder_hidden_attention_context = torch.cat((decoder_hidden, attention_context), dim=1)
            mel_output = self.linear_projection(decoder_hidden_attention_context)
            gate_prediction = self.gate_layer(decoder_hidden_attention_context)
            
            mel_outputs.append(mel_output)
            gate_outputs.append(gate_prediction)
            alignments.append(attention_weights)
            
        mel_outputs = torch.stack(mel_outputs, dim=2)
        gate_outputs = torch.stack(gate_outputs, dim=1)
        alignments = torch.stack(alignments, dim=1)
        
        return mel_outputs, gate_outputs, alignments

# 使用示例
vocab_size = 1000
encoder = Tacotron2Encoder(vocab_size)
decoder = Tacotron2Decoder()

# 模拟输入
batch_size = 2
text_seq_len = 20
mel_seq_len = 100

text_input = torch.randint(0, vocab_size, (batch_size, text_seq_len))
mel_input = torch.randn(batch_size, 80, mel_seq_len)

# 编码器前向传播
memory = encoder(text_input)
print(f"Encoder output shape: {memory.shape}")  # [batch, seq_len, 512]

# 解码器前向传播
mel_outputs, gate_outputs, alignments = decoder(memory, mel_input, torch.tensor([text_seq_len, text_seq_len]))
print(f"Mel outputs shape: {mel_outputs.shape}")      # [batch, 80, mel_seq_len]
print(f"Gate outputs shape: {gate_outputs.shape}")    # [batch, mel_seq_len, 1]
print(f"Alignments shape: {alignments.shape}")        # [batch, mel_seq_len, text_seq_len]
```

### 推荐论文
1. Shen et al., "Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions", ICASSP 2018
2. Wang et al., "Tacotron: Towards End-to-End Speech Synthesis", Interspeech 2017
3. Ping et al., "Deep Voice 3: Scaling Text-to-Speech with Convolutional Sequence Learning", ICLR 2018

---

## VITS（变分推理文本到语音）

### 这玩意儿到底是啥？
VITS就是结合变分自编码器和GAN的端到端语音合成！它同时优化似然和对抗损失，生成更自然的语音。

### 核心公式推导
**变分推理**：
$$
\mathcal{L}_{\text{VAE}} = \mathbb{E}_{q(z|x,y)}[\log p(y|z,x)] - \beta D_{KL}(q(z|x,y) \| p(z|x))
$$

**对抗训练**：
$$
\mathcal{L}_{\text{GAN}} = \mathbb{E}[\log D(y)] + \mathbb{E}[\log(1 - D(G(x)))]
$$

**持续时间预测**：
$$
\mathcal{L}_{\text{dur}} = \|\log(T_{\text{pred}} + 1) - \log(T_{\text{true}} + 1)\|^2
$$

**总损失**：
$$
\mathcal{L} = \mathcal{L}_{\text{VAE}} + \lambda_{\text{adv}} \mathcal{L}_{\text{GAN}} + \lambda_{\text{dur}} \mathcal{L}_{\text{dur}}
$$

### PyTorch代码示例
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class VITSGenerator(nn.Module):
    def __init__(self, hidden_dim=192, n_flows=4, n_speakers=1):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.n_flows = n_flows
        
        # 文本编码器
        self.text_encoder = nn.Sequential(
            nn.Embedding(1000, hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim * 2)  # mean and logvar
        )
        
        # 流式变换
        self.flows = nn.ModuleList([
            AffineCouplingLayer(hidden_dim) for _ in range(n_flows)
        ])
        
        # 波形生成器（简化版）
        self.wave_generator = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 4),
            nn.ReLU(),
            nn.Linear(hidden_dim * 4, hidden_dim * 8),
            nn.ReLU(),
            nn.Linear(hidden_dim * 8, 80)  # 80维梅尔谱图
        )
        
        # 持续时间预测器
        self.duration_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Softplus()
        )
        
    def forward(self, text, speaker_ids=None):
        # 文本编码
        text_encoded = self.text_encoder(text)  # [batch, seq_len, hidden_dim*2]
        mu, logvar = torch.chunk(text_encoded, 2, dim=-1)
        
        # 重参数化
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        
        # 流式变换
        log_det_jacobian = 0
        for flow in self.flows:
            z, log_det = flow(z)
            log_det_jacobian += log_det
            
        # 生成梅尔谱图
        mel_spectrogram = self.wave_generator(z)
        
        # 持续时间预测
        durations = self.duration_predictor(mu)
        
        return mel_spectrogram, durations, mu, logvar, log_det_jacobian

class AffineCouplingLayer(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.scale_net = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim // 2),
            nn.Tanh()
        )
        self.translate_net = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim // 2)
        )
        
    def forward(self, x):
        x1, x2 = torch.chunk(x, 2, dim=-1)
        scale = self.scale_net(x1)
        translate = self.translate_net(x1)
        
        y1 = x1
        y2 = x2 * torch.exp(scale) + translate
        
        log_det = torch.sum(scale, dim=-1)
        
        return torch.cat([y1, y2], dim=-1), log_det
    
    def inverse(self, y):
        y1, y2 = torch.chunk(y, 2, dim=-1)
        scale = self.scale_net(y1)
        translate = self.translate_net(y1)
        
        x1 = y1
        x2 = (y2 - translate) * torch.exp(-scale)
        
        return torch.cat([x1, x2], dim=-1)

class VITSDiscriminator(nn.Module):
    def __init__(self, input_dim=80):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv1d(input_dim, 64, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 1, kernel_size=3, padding=1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.layers(x)

# 损失函数
def vits_loss(mel_pred, mel_true, durations_pred, durations_true, 
              mu, logvar, log_det_jacobian, discriminator_score, beta=1.0):
    # VAE损失
    recon_loss = F.mse_loss(mel_pred, mel_true)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    vae_loss = recon_loss + beta * kl_loss
    
    # 持续时间损失
    dur_loss = F.mse_loss(torch.log(durations_pred + 1), torch.log(durations_true + 1))
    
    # 对抗损失
    adv_loss = -torch.mean(torch.log(discriminator_score + 1e-8))
    
    total_loss = vae_loss + 0.1 * dur_loss + 0.01 * adv_loss
    return total_loss, vae_loss, dur_loss, adv_loss

# 使用示例
generator = VITSGenerator()
discriminator = VITSDiscriminator()

# 模拟输入
batch_size = 2
text_len = 20
mel_len = 100

text_input = torch.randint(0, 1000, (batch_size, text_len))
mel_target = torch.randn(batch_size, 80, mel_len)
duration_target = torch.randint(1, 10, (batch_size, text_len)).float()

# 生成器前向传播
mel_pred, durations_pred, mu, logvar, log_det = generator(text_input)

# 判别器前向传播
fake_score = discriminator(mel_pred)

# 计算损失
total_loss, vae_loss, dur_loss, adv_loss = vits_loss(
    mel_pred, mel_target, durations_pred, duration_target, 
    mu, logvar, log_det, fake_score
)

print(f"Total loss: {total_loss.item():.6f}")
print(f"VAE loss: {vae_loss.item():.6f}")
print(f"Duration loss: {dur_loss.item():.6f}")
print(f"Adversarial loss: {adv_loss.item():.6f}")
```

### 推荐论文
1. Kim et al., "Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech", ICML 2021
2. Zhao et al., "VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech", ICML 2021
3. Donahue et al., "Efficiently Trainable Text-to-Speech System Based on Deep Convolutional Networks with Guided Attention", ICASSP 2018

---
> 音频和语音处理让AI能听会说！WaveNet生成高质量音频，Whisper实现多语言语音识别，Tacotron 2进行端到端语音合成，VITS结合VAE和GAN生成更自然的语音。记住：好的音频模型需要考虑人类听觉特性，而不仅仅是数学优化！