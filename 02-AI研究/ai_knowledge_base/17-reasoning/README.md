# 17. 推理

> 师弟师妹们好！推理就是让大模型学会"动脑子"，不只是背答案，而是能一步步思考解决问题。今天咱们用大白话+公式+代码，彻底搞懂各种推理方法！

---

## Chain-of-Thought (CoT)

### 这玩意儿到底是啥？
CoT就是让模型"把解题步骤写出来"！不是直接给答案，而是先写推理过程，再给答案。就像考试时老师要求"写出解题过程"一样。

### 核心公式推导
**标准语言模型**：
$$
P(y|x) = \prod_{i=1}^{|y|} P(y_i | x, y_{<i})
$$

**Chain-of-Thought**：
$$
P(z, y|x) = P(z|x) \cdot P(y|x, z)
$$

其中$z$是中间推理步骤（thought process），$y$是最终答案。

**为什么有效？**
- 分解复杂问题为简单步骤
- 每个步骤更容易预测
- 错误可以在早期步骤中被发现和纠正
- 符合人类的思维模式

### PyTorch代码示例
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class ChainOfThought:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
    def generate_cot(self, question, max_new_tokens=512):
        """生成Chain-of-Thought回答"""
        # 构造prompt
        prompt = f"Question: {question}\nLet's think step by step.\n"
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def extract_answer(self, cot_response):
        """从CoT响应中提取最终答案"""
        # 简单的启发式方法：找最后的"Answer:"或"The answer is"
        lines = cot_response.split('\n')
        for line in reversed(lines):
            if "answer" in line.lower() or "final" in line.lower():
                return line
        return lines[-1]  # 返回最后一行

# 使用示例
cot = ChainOfThought()
question = "If John has 5 apples and gives 2 to Mary, how many does he have left?"
response = cot.generate_cot(question)
answer = cot.extract_answer(response)
print(f"Response: {response}")
print(f"Answer: {answer}")
```

### 推荐论文
1. Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022
2. Kojima et al., "Large Language Models are Zero-Shot Reasoners", NeurIPS 2022
3. Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models", ICLR 2023

---

## Tree-of-Thoughts (ToT)

### 这玩意儿到底是啥？
ToT是CoT的升级版！它不仅考虑一个推理路径，还考虑多个可能的路径，像树一样分支展开，然后选择最好的路径。

### 核心公式推导
**状态空间搜索**：
- 初始状态：$s_0 = \text{problem}$
- 动作空间：$A(s)$ = 可能的下一步推理
- 状态转移：$s' = \text{step}(s, a)$
- 评估函数：$V(s)$ = 状态的质量评分

**搜索策略**：
1. **BFS（广度优先）**：探索所有可能的k步推理
2. **DFS（深度优先）**：深入探索最有希望的路径
3. **Best-first**：优先扩展最高评分的节点

**数学形式**：
$$
\text{ToT}(s_0) = \arg\max_{s \in \text{leaves}} V(s)
$$

**为什么比CoT强？**
- CoT只能走一条路，ToT可以试多条路
- 能回溯和修正错误的推理
- 更接近人类的试错思维

### PyTorch代码示例
```python
import torch
import heapq
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ThoughtNode:
    state: str
    value: float
    depth: int
    parent: 'ThoughtNode' = None
    children: List['ThoughtNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def __lt__(self, other):
        return self.value > other.value  # 最大堆

class TreeOfThoughts:
    def __init__(self, model, tokenizer, max_depth=3, beam_width=3):
        self.model = model
        self.tokenizer = tokenizer
        self.max_depth = max_depth
        self.beam_width = beam_width
        
    def evaluate_state(self, state: str) -> float:
        """评估状态的质量"""
        prompt = f"Rate the quality of this reasoning step on a scale of 1-10:\n{state}\nRating:"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=10)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取数字评分
        try:
            rating = float([x for x in response.split() if x.replace('.', '').isdigit()][0])
            return rating / 10.0  # 归一化到[0,1]
        except:
            return 0.5  # 默认评分
            
    def generate_next_steps(self, current_state: str, num_steps: int = 3) -> List[str]:
        """生成下一步可能的推理"""
        prompt = f"Given this reasoning so far:\n{current_state}\nWhat are the next possible steps? List {num_steps} options.\n1."
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 解析选项
        steps = []
        for line in response.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                steps.append(line.split('.', 1)[1].strip())
                if len(steps) >= num_steps:
                    break
        return steps[:num_steps]
    
    def search(self, initial_problem: str) -> str:
        """执行ToT搜索"""
        # 初始化根节点
        root = ThoughtNode(state=initial_problem, value=0.0, depth=0)
        heap = [root]
        best_solution = None
        best_value = -1
        
        while heap:
            node = heapq.heappop(heap)
            
            if node.depth >= self.max_depth:
                # 到达叶子节点，检查是否是更好的解决方案
                if node.value > best_value:
                    best_value = node.value
                    best_solution = node.state
                continue
                
            # 生成下一步
            next_steps = self.generate_next_steps(node.state)
            for step in next_steps:
                new_state = node.state + "\n" + step
                value = self.evaluate_state(new_state)
                
                child = ThoughtNode(
                    state=new_state,
                    value=value,
                    depth=node.depth + 1,
                    parent=node
                )
                node.children.append(child)
                heapq.heappush(heap, child)
                
                # 限制堆大小（beam search）
                if len(heap) > self.beam_width * (node.depth + 1):
                    heap = heap[:self.beam_width * (node.depth + 1)]
        
        return best_solution or initial_problem

# 使用示例
# model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
# tot = TreeOfThoughts(model, tokenizer)
# solution = tot.search("How to solve this complex math problem?")