# 29. AI智能体

> 师弟师妹们好！AI智能体就是能自主思考和行动的AI系统。今天咱们用大白话+公式+代码，彻底搞懂各种AI智能体架构！

---

## ReAct（推理+行动）

### 这玩意儿到底是啥？
ReAct就是让AI在推理和行动之间交替进行！它不仅能"想"，还能"做"，通过与环境交互来解决问题。

### 核心公式推导
**思维链**：
$$
\text{Thought}_t = f(\text{Observation}_{<t}, \text{Action}_{<t}, \text{Thought}_{<t})
$$

**行动选择**：
$$
\text{Action}_t = g(\text{Thought}_t, \text{Observation}_t)
$$

**状态更新**：
$$
\text{Observation}_{t+1} = \text{Environment}(\text{Action}_t)
$$

**目标函数**：
$$
\max_{f,g} \mathbb{E}[\sum_{t=1}^T r_t | \pi_{f,g}]
$$

其中$\pi_{f,g}$是由$f$和$g$定义的策略。

### PyTorch代码示例
```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM

class ReActAgent:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        # 定义可用工具
        self.tools = {
            "search": self.search_tool,
            "calculate": self.calculate_tool,
            "lookup": self.lookup_tool
        }
        
    def search_tool(self, query):
        """搜索工具（模拟）"""
        return f"Search results for '{query}': Wikipedia says it's a great topic."
    
    def calculate_tool(self, expression):
        """计算工具"""
        try:
            result = eval(expression)
            return f"Calculation result: {result}"
        except:
            return "Invalid expression"
    
    def lookup_tool(self, entity):
        """查找工具（模拟）"""
        knowledge_base = {
            "Paris": "Capital of France",
            "Eiffel Tower": "Located in Paris, France",
            "France": "Country in Europe"
        }
        return knowledge_base.get(entity, f"No information about {entity}")
    
    def generate_thought_or_action(self, context):
        """生成思维或行动"""
        prompt = f"""{context}
Thought:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        thought_part = response.split("Thought:")[-1].strip()
        
        return thought_part
    
    def parse_action(self, text):
        """解析行动"""
        if "Action:" in text:
            action_line = text.split("Action:")[-1].split("\n")[0].strip()
            if "(" in action_line and ")" in action_line:
                tool_name = action_line.split("(")[0].strip()
                args = action_line.split("(")[1].split(")")[0].strip().strip('"')
                return tool_name, args
        return None, None
    
    def run(self, task, max_steps=5):
        """运行ReAct智能体"""
        context = f"Question: {task}\n"
        observations = []
        
        for step in range(max_steps):
            # 生成思维或行动
            thought = self.generate_thought_or_action(context)
            context += f"Thought: {thought}\n"
            
            # 检查是否包含行动
            tool_name, args = self.parse_action(thought)
            
            if tool_name and tool_name in self.tools:
                # 执行工具
                observation = self.tools[tool_name](args)
                context += f"Action: {tool_name}({args})\nObservation: {observation}\n"
                observations.append(observation)
                
                # 检查是否可以回答
                if "Answer:" in thought or step == max_steps - 1:
                    break
            else:
                # 直接回答
                context += f"Answer: {thought}\n"
                break
                
        return context, observations

# 使用示例
agent = ReActAgent()

# 简单任务
task1 = "What is the capital of France?"
result1, obs1 = agent.run(task1)
print(f"Task: {task1}")
print(f"Result: {result1}")
print(f"Observations: {obs1}\n")

# 复杂任务
task2 = "Calculate the population density of Paris if it has 2.2 million people and area of 105 square kilometers."
result2, obs2 = agent.run(task2)
print(f"Task: {task2}")
print(f"Result: {result2}")
print(f"Observations: {obs2}")
```

### 推荐论文
1. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023
2. Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools", NeurIPS 2023
3. Hao et al., "Reasoning with Language Model is Planning with World Model", arXiv 2023

---

## Chain-of-Thought + Self-Reflection（CoT+自反思）

### 这玩意儿到底是啥？
CoT+自反思就是让AI先用思维链解决问题，然后反思自己的答案是否正确，如果不正确就重新思考。

### 核心公式推导
**初始推理**：
$$
a_0 = \text{CoT}(q)
$$

**反思过程**：
$$
r_t = \text{Reflect}(q, a_{t-1}, \text{critique}_{<t})
$$

**修正推理**：
$$
a_t = \text{Revise}(q, a_{t-1}, r_t)
$$

**终止条件**：
$$
\text{stop} = \text{Verify}(q, a_t) > \tau
$$

### PyTorch代码示例
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class SelfReflectiveAgent:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
    def generate_with_prompt(self, prompt, max_tokens=200):
        """生成文本"""
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def initial_cot(self, question):
        """初始思维链推理"""
        prompt = f"""Question: {question}
Let's think step by step.
Answer:"""
        return self.generate_with_prompt(prompt)
    
    def self_reflect(self, question, previous_answer):
        """自反思"""
        prompt = f"""Question: {question}
Previous Answer: {previous_answer}
Is this answer correct? Let's analyze step by step.
Reflection:"""
        return self.generate_with_prompt(prompt)
    
    def revise_answer(self, question, previous_answer, reflection):
        """修正答案"""
        prompt = f"""Question: {question}
Previous Answer: {previous_answer}
Reflection: {reflection}
Based on the reflection, let's provide a corrected answer.
Corrected Answer:"""
        return self.generate_with_prompt(prompt)
    
    def verify_answer(self, question, answer):
        """验证答案"""
        prompt = f"""Question: {question}
Answer: {answer}
On a scale of 1-10, how confident are you that this answer is correct?
Confidence Score:"""
        response = self.generate_with_prompt(prompt, max_tokens=50)
        try:
            # 提取数字评分
            score = float([x for x in response.split() if x.replace('.', '').isdigit()][0])
            return score / 10.0
        except:
            return 0.5  # 默认中等置信度
    
    def run(self, question, max_reflections=3, confidence_threshold=0.8):
        """运行自反思智能体"""
        # 初始推理
        current_answer = self.initial_cot(question)
        print(f"Initial answer: {current_answer}")
        
        confidence = self.verify_answer(question, current_answer)
        print(f"Initial confidence: {confidence:.2f}")
        
        if confidence >= confidence_threshold:
            return current_answer, 0
            
        # 自反思循环
        for i in range(max_reflections):
            reflection = self.self_reflect(question, current_answer)
            print(f"\nReflection {i+1}: {reflection}")
            
            revised_answer = self.revise_answer(question, current_answer, reflection)
            print(f"Revised answer: {revised_answer}")
            
            confidence = self.verify_answer(question, revised_answer)
            print(f"Confidence after revision: {confidence:.2f}")
            
            current_answer = revised_answer
            
            if confidence >= confidence_threshold:
                return current_answer, i + 1
                
        return current_answer, max_reflections

# 使用示例
agent = SelfReflectiveAgent()

# 数学问题
question1 = "If a train travels at 60 km/h for 2.5 hours, how far does it travel?"
answer1, reflections1 = agent.run(question1)
print(f"\nFinal answer: {answer1}")
print(f"Number of reflections: {reflections1}")

# 逻辑问题
question2 = "If all A are B, and some B are C, does it follow that some A are C?"
answer2, reflections2 = agent.run(question2, confidence_threshold=0.7)
print(f"\nFinal answer: {answer2}")
print(f"Number of reflections: {reflections2}")
```

### 推荐论文
1. Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback", NeurIPS 2023
2. Shinn & Labash, "Reflexion: an autonomous agent with dynamic memory and self-reflection", arXiv 2023
3. Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models", ICLR 2023

---

## Function Calling（函数调用）

### 这玩意儿到底是啥？
函数调用就是让AI能调用预定义的函数来完成任务！模型学会识别何时需要调用哪个函数，以及如何传递参数。

### 核心公式推导
**函数选择**：
$$
f^* = \arg\max_f P(f | q, c)
$$

**参数提取**：
$$
\theta^* = \arg\max_\theta P(\theta | q, c, f^*)
$$

**执行结果**：
$$
r = f^*(\theta^*)
$$

**响应生成**：
$$
a = g(q, c, r)
$$

其中$c$是上下文，$g$是响应生成器。

### PyTorch代码示例
```python
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class FunctionCallingAgent:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        # 定义函数库
        self.functions = {
            "get_weather": {
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                        "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                    },
                    "required": ["location"]
                },
                "implementation": self.get_weather_impl
            },
            "calculate_math": {
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression"}
                    },
                    "required": ["expression"]
                },
                "implementation": self.calculate_math_impl
            },
            "search_knowledge": {
                "description": "Search for factual information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                },
                "implementation": self.search_knowledge_impl
            }
        }
        
    def get_weather_impl(self, location, date=None):
        """天气查询实现"""
        weather_data = {
            "New York": "Sunny, 22°C",
            "London": "Cloudy, 15°C", 
            "Tokyo": "Rainy, 18°C"
        }
        return weather_data.get(location, f"Unknown weather for {location}")
    
    def calculate_math_impl(self, expression):
        """数学计算实现"""
        try:
            result = eval(expression)
            return str(result)
        except:
            return "Invalid mathematical expression"
    
    def search_knowledge_impl(self, query):
        """知识搜索实现"""
        knowledge_base = {
            "capital of france": "Paris",
            "eiffel tower location": "Paris, France",
            "population of new york": "8.8 million"
        }
        return knowledge_base.get(query.lower(), f"No information found for '{query}'")
    
    def extract_function_call(self, text):
        """从文本中提取函数调用"""
        try:
            # 查找JSON格式的函数调用
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                function_call = json.loads(json_str)
                return function_call
        except:
            pass
        return None
    
    def generate_function_call(self, question):
        """生成函数调用"""
        # 构建函数描述
        functions_desc = ""
        for name, func in self.functions.items():
            functions_desc += f"- {name}: {func['description']}\n"
            functions_desc += f"  Parameters: {json.dumps(func['parameters'])}\n\n"
        
        prompt = f"""Available functions:
{functions_desc}

Question: {question}

Respond with a JSON object containing the function name and parameters, like:
{{"name": "function_name", "arguments": {{"param1": "value1"}}}}

Function call:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.1,  # 低温度确保确定性输出
            do_sample=False
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def execute_function_call(self, function_call):
        """执行函数调用"""
        if not function_call or "name" not in function_call or "arguments" not in function_call:
            return "Invalid function call format"
            
        func_name = function_call["name"]
        arguments = function_call["arguments"]
        
        if func_name not in self.functions:
            return f"Function '{func_name}' not found"
            
        try:
            result = self.functions[func_name]["implementation"](**arguments)
            return result
        except Exception as e:
            return f"Error executing function: {str(e)}"
    
    def generate_final_answer(self, question, function_result):
        """生成最终答案"""
        prompt = f"""Question: {question}
Function Result: {function_result}

Provide a natural language answer to the question.
Answer:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Answer:")[-1].strip()
    
    def run(self, question):
        """运行函数调用智能体"""
        # 生成函数调用
        function_call_text = self.generate_function_call(question)
        print(f"Function call text: {function_call_text}")
        
        # 提取函数调用
        function_call = self.extract_function_call(function_call_text)
        print(f"Extracted function call: {function_call}")
        
        if not function_call:
            return "Could not extract valid function call"
        
        # 执行函数
        result = self.execute_function_call(function_call)
        print(f"Function result: {result}")
        
        # 生成最终答案
        final_answer = self.generate_final_answer(question, result)
        return final_answer

# 使用示例
agent = FunctionCallingAgent()

# 天气查询
question1 = "What's the weather in New York today?"
answer1 = agent.run(question1)
print(f"Q: {question1}")
print(f"A: {answer1}\n")

# 数学计算
question2 = "What is 15 * 24 + 78?"
answer2 = agent.run(question2)
print(f"Q: {question2}")
print(f"A: {answer2}\n")

# 知识查询
question3 = "What is the capital of France?"
answer3 = agent.run(question3)
print(f"Q: {question3}")
print(f"A: {answer3}")
```

### 推荐论文
1. OpenAI, "Function Calling and Other API Updates", 2023
2. Chen et al., "Tool Learning with Foundation Models", arXiv 2023
3. Qin et al., "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs", arXiv 2023

---

## Memory-Augmented Agents（记忆增强智能体）

### 这玩意儿到底是啥？
记忆增强智能体就是给AI加上长期记忆！它能记住之前的交互、学到的知识，并在后续任务中利用这些记忆。

### 核心公式推导
**记忆存储**：
$$
M = \{(k_i, v_i)\}_{i=1}^N
$$

**记忆检索**：
$$
\text{retrieved} = \arg\max_{(k,v) \in M} \text{sim}(q, k)
$$

**记忆更新**：
$$
M_{t+1} = M_t \cup \{(k_{t+1}, v_{t+1})\}
$$

**记忆压缩**：
$$
M_{\text{compressed}} = \text{Compress}(M)
$$

### PyTorch代码示例
```python
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class MemoryAugmentedAgent:
    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf", memory_size=1000):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        # 记忆编码器
        self.memory_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # FAISS索引
        self.memory_size = memory_size
        self.dimension = 384  # MiniLM-L6维度
        self.index = faiss.IndexFlatIP(self.dimension)
        faiss.normalize_L2(np.zeros((1, self.dimension)))  # 初始化
        
        # 记忆存储
        self.memories = []
        self.memory_keys = []
        
    def encode_memory(self, text):
        """编码记忆"""
        embedding = self.memory_encoder.encode([text])
        faiss.normalize_L2(embedding)
        return embedding.astype('float32')
    
    def add_memory(self, key, value):
        """添加记忆"""
        if len(self.memories) >= self.memory_size:
            # 移除最旧的记忆
            self.memories.pop(0)
            self.memory_keys.pop(0)
            # 重建FAISS索引
            if self.memories:
                embeddings = np.vstack([self.encode_memory(k) for k in self.memory_keys])
                self.index = faiss.IndexFlatIP(self.dimension)
                self.index.add(embeddings)
        
        self.memories.append(value)
        self.memory_keys.append(key)
        
        # 添加到FAISS索引
        key_embedding = self.encode_memory(key)
        self.index.add(key_embedding)
        
    def retrieve_memory(self, query, k=3):
        """检索记忆"""
        if not self.memories:
            return []
            
        query_embedding = self.encode_memory(query)
        distances, indices = self.index.search(query_embedding, min(k, len(self.memories)))
        
        retrieved = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.memories):
                retrieved.append({
                    'memory': self.memories[idx],
                    'key': self.memory_keys[idx],
                    'score': distances[0][i]
                })
        return retrieved
    
    def generate_with_memory(self, question, context=""):
        """使用记忆生成回答"""
        # 检索相关记忆
        relevant_memories = self.retrieve_memory(question, k=2)
        
        # 构建记忆上下文
        memory_context = ""
        for mem in relevant_memories:
            memory_context += f"Memory: {mem['memory']}\n"
        
        # 构建完整提示
        prompt = f"""{context}
{memory_context}
Question: {question}
Answer:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response.split("Answer:")[-1].strip()
        
        # 将问答对添加到记忆中
        self.add_memory(question, f"Question: {question}\nAnswer: {answer}")
        
        return answer, relevant_memories
    
    def learn_from_interaction(self, question, answer, feedback=None):
        """从交互中学习"""
        if feedback:
            # 如果有反馈，更新记忆
            memory_key = f"Q: {question} A: {answer}"
            memory_value = f"Question: {question}\nAnswer: {answer}\nFeedback: {feedback}"
            self.add_memory(memory_key, memory_value)
        else:
            # 否则只存储问答对
            self.add_memory(question, f"Question: {question}\nAnswer: {answer}")

# 使用示例
agent = MemoryAugmentedAgent()

# 初始问答
question1 = "What is the capital of France?"
answer1, memories1 = agent.generate_with_memory(question1)
print(f"Q1: {question1}")
print(f"A1: {answer1}")
print(f"Retrieved memories: {len(memories1)}\n")

# 相关问题
question2 = "What country is Paris in?"
answer2, memories2 = agent.generate_with_memory(question2)
print(f"Q2: {question2}")
print(f"A2: {answer2}")
print(f"Retrieved memories: {len(memories2)}\n")

# 学习反馈
agent.learn_from_interaction(question1, answer1, feedback="Correct! Paris is indeed the capital of France.")

# 检查记忆大小
print(f"Total memories stored: {len(agent.memories)}")
print(f"Memory keys: {agent.memory_keys[:3]}")  # 显示前3个记忆键
```

### 推荐论文
1. Park et al., "Generative Agents: Interactive Simulacra of Human Behavior", CHI 2023
2. Wu et al., "MemGPT: Leveraging Large Language Models as Main Brains for Autonomous Agents", arXiv 2023
3. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts", TACL 2023

---
> AI智能体让AI更聪明！ReAct结合推理和行动，CoT+自反思能自我纠错，函数调用能使用工具，记忆增强能积累经验。记住：好的智能体架构能让AI从被动应答变为主动思考和行动！