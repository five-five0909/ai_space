# 19. 分词

> 师弟师妹们好！分词就是把文本切成小块（token），让模型能处理。今天咱们用大白话+公式+代码，彻底搞懂各种分词方法！

---

## Byte Pair Encoding (BPE)

### 这玩意儿到底是啥？
BPE是一种子词分词算法！它从字符级别开始，不断合并最频繁的字符对，直到达到预设的词汇表大小。

### 核心公式推导
**初始化**：
- 词汇表$V = \{所有字符\}$
- 语料库$C = \{句子列表\}$

**迭代过程**：
1. 统计所有相邻符号对的频率：$freq(a,b) = \sum_{s \in C} \text{count}(a,b,s)$
2. 找到最高频的对：$(a^*, b^*) = \arg\max_{(a,b)} freq(a,b)$
3. 合并：$V = V \cup \{a^*b^*\}$
4. 在语料库中替换：$C = \text{replace}(C, a^*b^*, a^*b^*)$
5. 重复直到$|V| = V_{max}$

**分词过程**：
- 贪心匹配：从最长的token开始匹配
- 如果找不到，就用更短的token
- 最终保证每个字符都能被表示

### PyTorch代码示例
```python
import torch
from collections import defaultdict, Counter
import re

class BPETokenizer:
    def __init__(self, vocab_size=10000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.merges = {}
        self.special_tokens = {"<unk>": 0, "<pad>": 1, "<s>": 2, "</s>": 3}
        
    def get_stats(self, tokens):
        """统计相邻token对的频率"""
        pairs = defaultdict(int)
        for i in range(len(tokens) - 1):
            pairs[(tokens[i], tokens[i+1])] += 1
        return pairs
    
    def merge_tokens(self, tokens, pair, new_token):
        """合并token对"""
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i+1] == pair[1]:
                new_tokens.append(new_token)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        return new_tokens
    
    def train(self, corpus):
        """训练BPE分词器"""
        # 预处理：按空格分词，添加结尾标记
        word_freqs = defaultdict(int)
        for sentence in corpus:
            words = sentence.split()
            for word in words:
                word_freqs[word + "</w>"] += 1
        
        # 初始化词汇表（字符级别）
        vocab = defaultdict(int)
        for word, freq in word_freqs.items():
            chars = list(word)
            for char in chars:
                vocab[char] += freq
                
        # BPE迭代
        merges = {}
        while len(vocab) < self.vocab_size:
            # 统计所有相邻对
            pairs = defaultdict(int)
            for word, freq in word_freqs.items():
                chars = list(word)
                for i in range(len(chars) - 1):
                    pairs[(chars[i], chars[i+1])] += freq
                    
            if not pairs:
                break
                
            # 找到最高频对
            best_pair = max(pairs, key=pairs.get)
            new_token = ''.join(best_pair)
            
            # 更新词汇表
            merges[best_pair] = new_token
            vocab[new_token] = pairs[best_pair]
            
            # 更新语料库
            new_word_freqs = defaultdict(int)
            for word, freq in word_freqs.items():
                new_word = word.replace(''.join(best_pair), new_token)
                new_word_freqs[new_word] = freq
            word_freqs = new_word_freqs
        
        # 构建最终词汇表
        self.vocab = {token: idx + len(self.special_tokens) for idx, token in enumerate(vocab)}
        self.vocab.update(self.special_tokens)
        self.merges = merges
        
    def encode(self, text):
        """分词"""
        words = text.split()
        tokens = []
        for word in words:
            word += "</w>"
            # 字符级别开始
            chars = list(word)
            # 应用所有合并规则
            for pair, merge in self.merges.items():
                if pair[0] in chars and pair[1] in chars:
                    i = 0
                    while i < len(chars) - 1:
                        if chars[i] == pair[0] and chars[i+1] == pair[1]:
                            chars[i] = merge
                            chars.pop(i+1)
                        else:
                            i += 1
            tokens.extend(chars)
        return [self.vocab.get(token, self.vocab["<unk>"]) for token in tokens]

# 使用示例
corpus = ["hello world", "hello there", "world of python"]
tokenizer = BPETokenizer(vocab_size=1000)
tokenizer.train(corpus)
tokens = tokenizer.encode("hello world")
print(tokens)
```

### 推荐论文
1. Sennrich et al., "Neural Machine Translation of Rare Words with Subword Units", ACL 2016
2. Kudo & Richardson, "SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing", EMNLP 2018
3. Wu et al., "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation", arXiv 2016

---

## WordPiece

### 这玩意儿到底是啥？
WordPiece是BPE的变体，但选择合并规则的标准不同！BPE选最频繁的对，WordPiece选能最大化语言模型概率的对。

### 核心公式推导
**语言模型概率**：
假设当前词汇表为$V$，考虑合并$a$和$b$成$ab$，计算似然增益：
$$
\Delta L = \log P(ab) - \log P(a) - \log P(b)
$$

其中：
$$
P(token) = \frac{\text{freq}(token)}{\sum_{t \in V} \text{freq}(t)}
$$

**选择标准**：
$$
(a^*, b^*) = \arg\max_{(a,b)} \Delta L(a,b)
$$

**为什么比BPE好？**
- BPE只考虑频率，WordPiece考虑概率
- WordPiece更倾向于合并有意义的子词
- 在低频词上表现更好

### PyTorch代码示例
```python
import torch
from collections import defaultdict
import math

class WordPieceTokenizer:
    def __init__(self, vocab_size=10000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.special_tokens = {"<unk>": 0, "<pad>": 1, "[CLS]": 2, "[SEP]": 3}
        
    def calculate_likelihood_gain(self, word_freqs, a, b, ab):
        """计算似然增益"""
        total_freq = sum(word_freqs.values())
        
        # 当前概率
        p_a = word_freqs.get(a, 0) / total_freq
        p_b = word_freqs.get(b, 0) / total_freq
        p_ab = word_freqs.get(ab, 0) / total_freq
        
        # 避免除零
        if p_a == 0 or p_b == 0:
            return float('-inf')
            
        # 似然增益
        if p_ab > 0:
            return math.log(p_ab) - math.log(p_a) - math.log(p_b)
        else:
            return float('-inf')
    
    def train(self, corpus):
        """训练WordPiece分词器"""
        # 初始化：字符级别
        word_freqs = defaultdict(int)
        for sentence in corpus:
            words = sentence.split()
            for word in words:
                word_freqs[word] += 1
                
        # 字符频率
        char_freqs = defaultdict(int)
        for word, freq in word_freqs.items():
            for char in word:
                char_freqs[char] += freq
                
        vocab = set(char_freqs.keys())
        
        # WordPiece迭代
        while len(vocab) < self.vocab_size:
            best_gain = float('-inf')
            best_pair = None
            
            # 尝试所有可能的合并
            for word in list(word_freqs.keys()):
                chars = list(word)
                for i in range(len(chars) - 1):
                    a, b = chars[i], chars[i+1]
                    ab = a + b
                    if ab not in vocab:
                        gain = self.calculate_likelihood_gain(word_freqs, a, b, ab)
                        if gain > best_gain:
                            best_gain = gain
                            best_pair = (a, b, ab)
                            
            if best_pair is None or best_gain <= 0:
                break
                
            a, b, ab = best_pair
            vocab.add(ab)
            
            # 更新词频
            new_word_freqs = defaultdict(int)
            for word, freq in word_freqs.items():
                new_word = word.replace(a + b, ab)
                new_word_freqs[new_word] += freq
            word_freqs = new_word_freqs
        
        # 构建词汇表
        self.vocab = {token: idx + len(self.special_tokens) for idx, token in enumerate(vocab)}
        self.vocab.update(self.special_tokens)
        
    def encode(self, text):
        """分词（贪心最长匹配）"""
        words = text.split()
        tokens = []
        for word in words:
            # 从最长可能的token开始匹配
            i = 0
            while i < len(word):
                matched = False
                # 尝试从长到短匹配
                for j in range(len(word), i, -1):
                    subword = word[i:j]
                    if subword in self.vocab:
                        tokens.append(subword)
                        i = j
                        matched = True
                        break
                if not matched:
                    tokens.append("<unk>")
                    i += 1
        return [self.vocab.get(token, self.vocab["<unk>"]) for token in tokens]
```

### 推荐论文
1. Wu et al., "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation", arXiv 2016
2. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019
3. Schuster & Nakajima, "Japanese and Korean Voice Search", ICASSP 2012

---

## Unigram Language Model

### 这玩意儿到底是啥？
Unigram LM是一种基于概率的分词方法！它假设每个token的出现是独立的，通过最大化整个序列的概率来选择最佳分词。

### 核心公式推导
**目标函数**：
给定文本$S$，找到分词$T = \{t_1, t_2, ..., t_n\}$使得：
$$
P(T) = \prod_{i=1}^n P(t_i)
$$

最大化$\log P(T) = \sum_{i=1}^n \log P(t_i)$

**训练过程**（EM算法）：
1. **E-step**：给定当前词汇表$V$和概率$P$，计算每个句子的最佳分词
2. **M-step**：给定分词结果，更新token概率：
   $$
   P(t) = \frac{\text{count}(t)}{\sum_{t' \in V} \text{count}(t')}
   $$
3. **Pruning**：移除低概率token，添加新候选token
4. 重复直到收敛

**分词过程**（维特比算法）：
- 动态规划：$dp[i] = \max_{j < i} dp[j] + \log P(S[j:i])$
- 回溯找到最佳分词路径

### PyTorch代码示例
```python
import torch
import heapq
from collections import defaultdict

class UnigramTokenizer:
    def __init__(self, vocab_size=10000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.token_probs = {}
        self.special_tokens = {"<unk>": 0, "<pad>": 1}
        
    def segment_sentence(self, sentence, token_probs):
        """使用维特比算法分词"""
        n = len(sentence)
        dp = [float('-inf')] * (n + 1)
        parent = [-1] * (n + 1)
        dp[0] = 0
        
        for i in range(1, n + 1):
            for j in range(i):
                substring = sentence[j:i]
                if substring in token_probs:
                    prob = token_probs[substring]
                    if dp[j] + math.log(prob) > dp[i]:
                        dp[i] = dp[j] + math.log(prob)
                        parent[i] = j
                        
        # 回溯
        tokens = []
        i = n
        while i > 0:
            j = parent[i]
            if j == -1:
                tokens.append("<unk>")
                i -= 1
            else:
                tokens.append(sentence[j:i])
                i = j
        return list(reversed(tokens))
    
    def train(self, corpus):
        """训练Unigram分词器"""
        # 初始化：所有可能的子串
        candidate_tokens = set()
        for sentence in corpus:
            for i in range(len(sentence)):
                for j in range(i + 1, len(sentence) + 1):
                    candidate_tokens.add(sentence[i:j])
                    
        # 初始化概率（均匀分布）
        token_probs = {token: 1.0 / len(candidate_tokens) for token in candidate_tokens}
        
        # EM迭代
        for iteration in range(10):
            # E-step: 分词所有句子
            token_counts = defaultdict(int)
            total_tokens = 0
            
            for sentence in corpus:
                tokens = self.segment_sentence(sentence, token_probs)
                for token in tokens:
                    if token != "<unk>":
                        token_counts[token] += 1
                        total_tokens += 1
                        
            # M-step: 更新概率
            token_probs = {token: count / total_tokens for token, count in token_counts.items()}
            
            # Pruning: 保留最高概率的vocab_size个token
            if len(token_probs) > self.vocab_size:
                top_tokens = heapq.nlargest(self.vocab_size, token_probs.items(), key=lambda x: x[1])
                token_probs = dict(top_tokens)
                
        # 构建最终词汇表
        self.token_probs = token_probs
        self.vocab = {token: idx + len(self.special_tokens) for idx, token in enumerate(token_probs)}
        self.vocab.update(self.special_tokens)
        
    def encode(self, text):
        """分词"""
        tokens = self.segment_sentence(text, self.token_probs)
        return [self.vocab.get(token, self.vocab["<unk>"]) for token in tokens]
```

### 推荐论文
1. Kudo, "Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates", ACL 2018
2. Kudo & Richardson, "SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing", EMNLP 2018
3. Mikolov et al., "Efficient Estimation of Word Representations in Vector Space", ICLR 2013

---

## TikToken (GPT分词器)

### 这玩意儿到底是啥？
TikToken是OpenAI开发的超快分词器！它使用预训练的BPE模型，支持多种编码（cl100k_base, p50k_base, r50k_base等）。

### 核心特点
- **速度极快**：用Rust实现，比Python快10-100倍
- **预训练模型**：不需要自己训练，直接加载预训练的BPE模型
- **多语言支持**：cl100k_base支持100+种语言
- **特殊token处理**：内置特殊token如<|endoftext|>

### PyTorch代码示例
```python
import tiktoken
import torch

class TikTokenTokenizer:
    def __init__(self, encoding_name="cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.vocab_size = self.encoding.n_vocab
        
    def encode(self, text):
        """分词"""
        return self.encoding.encode(text)
    
    def decode(self, tokens):
        """解码"""
        return self.encoding.decode(tokens)
    
    def batch_encode(self, texts, max_length=512, pad_token_id=0):
        """批量分词"""
        encoded = []
        for text in texts:
            tokens = self.encode(text)[:max_length]
            # 填充到max_length
            tokens += [pad_token_id] * (max_length - len(tokens))
            encoded.append(tokens)
        return torch.tensor(encoded)
    
    def get_vocab(self):
        """获取词汇表"""
        return self.encoding._mergeable_ranks

# 使用示例
tokenizer = TikTokenTokenizer("cl100k_base")

# 编码
text = "Hello, world!"
tokens = tokenizer.encode(text)
print(f"Tokens: {tokens}")
print(f"Decoded: {tokenizer.decode(tokens)}")

# 批量编码
texts = ["Hello, world!", "How are you?", "I'm fine, thanks!"]
batch_tokens = tokenizer.batch_encode(texts, max_length=10)
print(f"Batch shape: {batch_tokens.shape}")

# 查看词汇表大小
print(f"Vocab size: {tokenizer.vocab_size}")
```

### 推荐论文
1. OpenAI, "GPT-4 Technical Report", arXiv 2023
2. Radford et al., "Language Models are Unsupervised Multitask Learners", OpenAI Blog 2019
3. Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020

---
> 分词是NLP的基础！BPE简单有效，WordPiece考虑概率，Unigram LM理论优美，TikToken实用高效。记住：没有最好的分词器，只有最适合你任务的分词器！