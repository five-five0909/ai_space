# 38. Agent框架

> 一句话：Agent框架就是让AI能自主思考和行动的工具，核心是**规划-执行-反思**的循环。LangGraph灵活可控，AutoGen多智能体协作，CrewAI角色扮演，是构建智能体的三大主力。

---

## Agent基础概念

### 这玩意儿到底是啥？

AI Agent（智能体）是一种能够**自主感知环境、做出决策、执行行动**的AI系统。与传统"一问一答"的LLM不同，Agent能够：

- **规划**：将复杂任务分解为子任务
- **执行**：调用工具完成任务
- **反思**：评估结果并调整策略
- **记忆**：记住历史交互和学到的东西

### Agent核心架构

```
Agent架构（ReAct模式）：
┌─────────────────────────────────────────┐
│                 用户输入                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│              Thought（思考）              │
│  "我需要搜索什么是Transformer..."         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│              Action（行动）               │
│  调用search工具: "Transformer架构介绍"    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│            Observation（观察）            │
│  搜索结果: Transformer是2017年提出的...   │
└─────────────────────────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  是否需要更多行动？   │
         └──────────────────────┘
           ↓ 是              ↓ 否
     [继续循环]        [生成最终回答]
```

---

## LangGraph

### 这玩意儿到底是啥？

LangGraph是LangChain团队推出的Agent框架，核心特色是**图结构工作流**。相比于传统的链式调用，LangGraph用图来定义Agent的行为，支持循环、分支、并行等复杂控制流。

**核心特点：**
- **图结构**：用节点和边定义工作流
- **状态管理**：自动管理Agent状态
- **循环支持**：支持迭代执行直到满足条件
- **人机协作**：支持人工干预和审核
- **可视化**：图形化展示工作流

### 核心概念

```
LangGraph核心组件：

State（状态）：
- 在节点之间传递的共享数据
- 使用TypedDict定义
- 每个节点可以读取和更新状态

Node（节点）：
- 执行具体任务的函数
- 接收状态，返回状态更新

Edge（边）：
- 定义节点之间的转换
- 支持条件边（根据状态选择下一个节点）

Graph（图）：
- 节点和边的集合
- 定义完整的工作流
```

### 代码示例

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# 定义工具
@tool
def search(query: str) -> str:
    """搜索工具"""
    # 模拟搜索
    results = {
        "Transformer": "Transformer是2017年提出的神经网络架构...",
        "BERT": "BERT是2018年提出的预训练模型...",
    }
    for key in results:
        if key.lower() in query.lower():
            return results[key]
    return "未找到相关信息"

@tool
def calculator(expression: str) -> str:
    """计算器工具"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

tools = [search, calculator]

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "消息历史"]
    tool_calls: list

# 创建LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 定义节点
def agent_node(state: AgentState) -> dict:
    """Agent思考节点"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """判断是否继续"""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# 添加边
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)
workflow.add_edge("tools", "agent")  # 工具执行后返回agent

# 编译并运行
app = workflow.compile()

# 执行
result = app.invoke({
    "messages": [HumanMessage(content="Transformer是哪一年提出的？请帮我搜索一下。")]
})
print(result["messages"][-1].content)
```

### 高级功能

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# 1. 使用记忆
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# 多轮对话
config = {"configurable": {"thread_id": "user-123"}}
result1 = app.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config=config,
)
result2 = app.invoke(
    {"messages": [HumanMessage(content="我刚才问了你什么？")]},
    config=config,
)

# 2. 人机协作
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint import MemorySaver

def human_review_node(state: AgentState) -> dict:
    """人工审核节点"""
    last_message = state["messages"][-1]
    print(f"Agent计划执行: {last_message.tool_calls}")
    approval = input("是否批准？(y/n): ")
    if approval.lower() != "y":
        return {"messages": [AIMessage(content="用户拒绝了该操作")]}
    return state

# 3. 并行执行
from langgraph.graph import StateGraph

def parallel_search(state: AgentState) -> dict:
    """并行搜索多个来源"""
    import asyncio
    queries = state.get("search_queries", [])
    # 并行执行搜索
    results = asyncio.gather(*[search(q) for q in queries])
    return {"search_results": results}

# 4. 创建ReAct Agent（快捷方式）
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[search, calculator],
    state_modifier="你是一个专业的AI助手。",
)

result = agent.invoke({
    "messages": [HumanMessage(content="计算(10 + 20) * 3的结果")]
})
```

### 可视化

```python
# 绘制工作流图
from IPython.display import Image, display

display(Image(app.get_graph().draw_mermaid_png()))

# 导出为Mermaid格式
print(app.get_graph().draw_mermaid())
```

### 推荐论文

1. **LangChain Team, 2024** - "LangGraph: Building Stateful, Multi-Actor Applications with LLMs" - 官方文档
2. **Yao et al., 2023** - "ReAct: Synergizing Reasoning and Acting in Language Models" - ReAct架构
3. **Wei et al., 2022** - "Chain-of-Thought Prompting Elicits Reasoning" - 思维链

---

## AutoGen

### 这玩意儿到底是啥？

AutoGen是微软研究院开源的多智能体框架，核心特色是**多Agent对话协作**。它让多个Agent像团队一样工作，通过对话来完成任务，支持人类参与和代码执行。

**核心特点：**
- **多Agent对话**：Agent之间通过对话协作
- **人机协作**：支持人类在对话中介入
- **代码执行**：Agent可以编写和执行代码
- **预设角色**：提供AssistantAgent、UserProxyAgent等

### 核心架构

```
AutoGen架构：
┌─────────────────────────────────────────────────────┐
│                 Conversation Manager                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────┐     ┌────────────────┐         │
│  │ AssistantAgent │ ←→ │ UserProxyAgent │         │
│  │ (AI助手)        │     │ (用户代理)      │         │
│  └────────────────┘     └────────────────┘         │
│         ↓                        ↓                  │
│  ┌────────────────┐     ┌────────────────┐         │
│  │  CodeExecutor  │     │  HumanInput    │         │
│  │  (代码执行器)   │     │  (人工输入)     │         │
│  └────────────────┘     └────────────────┘         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 代码示例

```python
import autogen
from autogen import AssistantAgent, UserProxyAgent

# 配置LLM
config_list = [
    {
        "model": "gpt-4",
        "api_key": "your-api-key",
    }
]

llm_config = {
    "config_list": config_list,
    "timeout": 120,
}

# 创建助手Agent
assistant = AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="""你是一个专业的AI编程助手。
    你可以：
    1. 编写Python代码解决问题
    2. 分析和解释代码
    3. 调试和修复代码错误

    当需要执行代码时，请使用```python代码块包裹代码。
    """,
)

# 创建用户代理Agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # NEVER, ALWAYS, TERMINATE
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "./coding",
        "use_docker": False,  # 使用Docker更安全
    },
)

# 开始对话
user_proxy.initiate_chat(
    assistant,
    message="请帮我写一个Python函数来计算斐波那契数列，并测试它。",
)

# 查看对话历史
for message in user_proxy.chat_messages[assistant]:
    print(f"{message['role']}: {message['content'][:100]}...")
```

### 多Agent协作

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# 创建多个专家Agent
coder = AssistantAgent(
    name="coder",
    llm_config=llm_config,
    system_message="你是Python编程专家，负责编写代码。",
)

reviewer = AssistantAgent(
    name="reviewer",
    llm_config=llm_config,
    system_message="你是代码审查专家，负责检查代码质量和潜在问题。",
)

tester = AssistantAgent(
    name="tester",
    llm_config=llm_config,
    system_message="你是测试专家，负责编写测试用例并验证代码。",
)

# 创建用户代理
user = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "./coding"},
)

# 创建群聊
group_chat = GroupChat(
    agents=[user, coder, reviewer, tester],
    messages=[],
    max_round=20,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

# 开始群聊
user.initiate_chat(
    manager,
    message="请帮我开发一个简单的待办事项管理程序，包含添加、删除、列出功能。",
)
```

### 高级功能

```python
# 1. 自定义工具
from autogen import register_function

def get_weather(city: str) -> str:
    """获取天气信息"""
    # 模拟API调用
    return f"{city}今天天气晴朗，温度25°C"

register_function(
    get_weather,
    caller=assistant,
    executor=user_proxy,
    name="get_weather",
    description="获取指定城市的天气信息",
)

# 2. 教学模式
teacher = AssistantAgent(
    name="teacher",
    llm_config=llm_config,
    system_message="你是一位耐心的编程老师，通过引导式提问帮助学生理解概念。",
)

student = UserProxyAgent(
    name="student",
    human_input_mode="ALWAYS",  # 让学生可以输入
)

# 3. 代码执行沙箱
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "./workspace",
        "use_docker": True,  # 使用Docker隔离执行
        "timeout": 60,
    },
)
```

### 推荐论文

1. **Wu et al., 2023** - "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" - AutoGen原论文
2. **Park et al., 2023** - "Generative Agents: Interactive Simulacra of Human Behavior" - 生成式智能体
3. **Hao et al., 2023** - "Reasoning with Language Model is Planning with World Model" - 推理与规划

---

## CrewAI

### 这玩意儿到底是啥？

CrewAI是一个角色扮演式的多智能体框架，核心特色是**定义清晰的Agent角色和任务**。每个Agent都有自己的角色、目标和背景故事，像组建一个团队一样协作完成任务。

**核心特点：**
- **角色定义**：每个Agent有明确的角色和职责
- **任务分配**：明确定义每个任务由谁完成
- **工具共享**：Agent可以共享和使用各种工具
- **流程编排**：支持顺序和并行执行

### 核心架构

```
CrewAI架构：
┌─────────────────────────────────────────────────────┐
│                      Crew (团队)                      │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐│
│  │                   Process                        ││
│  │         (Sequential / Hierarchical)             ││
│  └─────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │   Agent 1    │ │   Agent 2    │ │   Agent 3    ││
│  │  (Researcher)│ │   (Writer)   │ │  (Reviewer)  ││
│  │              │ │              │ │              ││
│  │  - Role      │ │  - Role      │ │  - Role      ││
│  │  - Goal      │ │  - Goal      │ │  - Goal      ││
│  │  - Backstory │ │  - Backstory │ │  - Backstory ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │   Task 1     │ │   Task 2     │ │   Task 3     ││
│  │ (研究主题)    │ │ (撰写内容)    │ │ (审核修改)    ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
└─────────────────────────────────────────────────────┘
```

### 代码示例

```python
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 定义LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# 定义Agent
researcher = Agent(
    role="研究员",
    goal="深入研究指定主题，收集全面的信息",
    backstory="""你是一位经验丰富的研究员，擅长从各种来源收集和分析信息。
    你对细节有敏锐的洞察力，总能找到关键信息。""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

writer = Agent(
    role="技术作家",
    goal="将研究结果转化为清晰、易读的文章",
    backstory="""你是一位专业的技术作家，擅长将复杂的技术概念转化为
    易于理解的内容。你的文章结构清晰，语言生动。""",
    verbose=True,
    allow_delegation=True,
    llm=llm,
)

reviewer = Agent(
    role="审核编辑",
    goal="确保文章质量，提出改进建议",
    backstory="""你是一位严格的审核编辑，有丰富的内容审核经验。
    你擅长发现问题并提出具体的改进建议。""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

# 定义Task
research_task = Task(
    description="研究Transformer架构的发展历史和核心技术",
    expected_output="一份包含Transformer发展历史、核心概念和技术创新的研究报告",
    agent=researcher,
)

writing_task = Task(
    description="基于研究报告撰写一篇关于Transformer的技术博客",
    expected_output="一篇结构清晰、内容丰富的技术博客文章",
    agent=writer,
    context=[research_task],  # 依赖研究任务
)

review_task = Task(
    description="审核博客文章并提出改进建议",
    expected_output="审核意见和修改后的最终文章",
    agent=reviewer,
    context=[writing_task],
)

# 创建Crew
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.sequential,  # 顺序执行
    verbose=True,
)

# 执行
result = crew.kickoff()
print(result)
```

### 自定义工具

```python
from crewai_tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# 定义搜索工具
@tool("搜索工具")
def search_tool(query: str) -> str:
    """搜索互联网获取信息"""
    search = DuckDuckGoSearchRun()
    return search.run(query)

# 定义文件读写工具
@tool("文件保存")
def save_to_file(content: str, filename: str) -> str:
    """将内容保存到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"内容已保存到 {filename}"

# 在Agent中使用工具
researcher = Agent(
    role="研究员",
    goal="研究指定主题",
    backstory="你是一位研究员",
    tools=[search_tool],
    llm=llm,
)
```

### 层级流程

```python
from crewai import Crew, Process

# 层级流程：Manager协调任务分配
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.hierarchical,  # 层级流程
    manager_llm=ChatOpenAI(model="gpt-4", temperature=0),
    verbose=True,
)

# Manager会自动：
# 1. 分析任务需求
# 2. 分配任务给合适的Agent
# 3. 协调Agent之间的协作
# 4. 汇总结果
```

### 推荐论文

1. **CrewAI Team, 2023** - "CrewAI: Platform for Multi-AI Agent Systems" - 官方文档
2. **Park et al., 2023** - "Generative Agents: Interactive Simulacra of Human Behavior" - 角色扮演
3. **Li et al., 2023** - "CAMEL: Communicative Agents for 'Mind' Exploration" - 多Agent协作

---

## AutoGPT

### 这玩意儿到底是啥？

AutoGPT是最早引爆AI Agent热潮的开源项目，核心特色是**完全自主的任务执行**。给定一个目标，AutoGPT会自主规划、执行、评估，直到目标完成或资源耗尽。

**核心特点：**
- **完全自主**：无需人类干预
- **长期记忆**：使用向量数据库存储记忆
- **工具调用**：支持搜索、代码执行等
- **自我反思**：评估执行结果并调整

### 代码示例

```python
# AutoGPT主要通过命令行使用
# pip install autogpt

# 基本用法：
# autogpt --gpt3only --continuous

# Python API（简化版）
from autogpt.agent import Agent
from autogpt.llm import create_chat_completion
from autogpt.memory import LocalCache

class SimpleAutoGPT:
    def __init__(self, name, role, goals):
        self.name = name
        self.role = role
        self.goals = goals
        self.memory = []

    def think(self):
        """思考下一步行动"""
        prompt = f"""
        你是{self.name}，一个{self.role}。

        目标：
        {chr(10).join(f'{i+1}. {g}' for i, g in enumerate(self.goals))}

        记忆：
        {chr(10).join(self.memory[-5:])}

        请思考下一步应该做什么来达成目标。
        输出格式：
        THOUGHTS: [你的思考]
        COMMAND: [要执行的命令]
        ARGS: [命令参数]
        """
        return create_chat_completion(prompt)

    def execute(self, command, args):
        """执行命令"""
        # 执行搜索、代码等
        pass

    def run(self, max_iterations=10):
        """运行主循环"""
        for i in range(max_iterations):
            # 思考
            response = self.think()
            # 执行
            result = self.execute(response['command'], response['args'])
            # 记忆
            self.memory.append(f"执行了{response['command']}，结果：{result}")
            # 检查是否完成
            if "任务完成" in result:
                break
```

### 推荐论文

1. **Richards, 2023** - "AutoGPT: An Autonomous GPT-4 Experiment" - 项目文档
2. **Significant Gravitas, 2023** - "AutoGPT Architecture and Design" - 架构设计
3. **Yao et al., 2023** - "ReAct: Synergizing Reasoning and Acting" - ReAct模式

---

## BabyAGI

### 这玩意儿到底是啥？

BabyAGI是简化版的自主Agent，核心是**任务驱动**的工作流：从目标生成任务、执行任务、根据结果生成新任务，形成循环。

**核心特点：**
- **任务驱动**：以任务队列为中心
- **三种执行器**：任务执行、任务创建、任务优先级排序
- **简单架构**：易于理解和扩展
- **向量记忆**：使用向量数据库存储上下文

### 核心架构

```
BabyAGI循环：
┌─────────────────────────────────────────┐
│              任务队列                     │
│  [任务1, 任务2, 任务3, ...]               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         1. 执行第一个任务                  │
│            execution_agent               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         2. 存储结果到向量数据库            │
│            向量存储                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         3. 创建新任务                      │
│            task_creation_agent           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         4. 对任务排序                      │
│            prioritization_agent          │
└─────────────────────────────────────────┘
                    ↓
            [循环回到步骤1]
```

### 代码示例

```python
import openai
import chromadb
from collections import deque

class BabyAGI:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key
        self.task_list = deque([])
        self.task_id_counter = 1

        # 向量存储
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("tasks")

    def add_task(self, task: str):
        """添加任务"""
        self.task_list.append({
            "task_id": self.task_id_counter,
            "task_name": task,
        })
        self.task_id_counter += 1

    def execution_agent(self, task: str, context: str) -> str:
        """执行任务"""
        prompt = f"""
        你是一个任务执行AI。请完成以下任务。

        背景：{context}
        任务：{task}

        请提供详细的执行结果：
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def task_creation_agent(self, result: str, task_description: str) -> list:
        """创建新任务"""
        prompt = f"""
        你是一个任务创建AI。根据已完成的任务结果，创建新的相关任务。

        已完成任务：{task_description}
        执行结果：{result}

        请列出3-5个新的后续任务（每行一个）：
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        new_tasks = response.choices[0].message.content.strip().split('\n')
        return [task.strip() for task in new_tasks if task.strip()]

    def prioritization_agent(self, task_list: list) -> list:
        """任务优先级排序"""
        prompt = f"""
        你是一个任务优先级排序AI。请对以下任务按重要性排序：

        任务列表：
        {chr(10).join(f'{i+1}. {t}' for i, t in enumerate(task_list))}

        请输出排序后的任务编号（用逗号分隔）：
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        # 解析并重新排序
        return task_list  # 简化处理

    def run(self, objective: str, max_iterations: int = 5):
        """运行主循环"""
        # 添加初始任务
        self.add_task(f"制定实现以下目标的计划：{objective}")

        for i in range(max_iterations):
            if not self.task_list:
                break

            # 获取第一个任务
            task = self.task_list.popleft()
            print(f"\n执行任务: {task['task_name']}")

            # 获取上下文
            context = ""
            results = self.collection.query(
                query_texts=[task['task_name']],
                n_results=3,
            )
            if results['documents']:
                context = '\n'.join(results['documents'][0])

            # 执行任务
            result = self.execution_agent(task['task_name'], context)
            print(f"结果: {result[:200]}...")

            # 存储结果
            self.collection.add(
                documents=[result],
                ids=[f"task_{task['task_id']}"],
            )

            # 创建新任务
            new_tasks = self.task_creation_agent(result, task['task_name'])
            for new_task in new_tasks:
                self.add_task(new_task)

            # 排序
            # self.prioritization_agent(list(self.task_list))

# 使用
baby_agi = BabyAGI("your-api-key")
baby_agi.run("研究并总结Transformer架构的核心创新点", max_iterations=5)
```

### 推荐论文

1. **Nakajima, 2023** - "BabyAGI: Task-Driven Autonomous Agent" - 项目文档
2. **Yao et al., 2023** - "ReAct: Synergizing Reasoning and Acting" - ReAct架构
3. **Wei et al., 2022** - "Chain-of-Thought Prompting" - 思维链

---

## 对比总结

| 框架 | 核心特色 | 复杂度 | 适用场景 |
|------|----------|--------|----------|
| LangGraph | 图结构工作流 | 中 | 自定义复杂流程 |
| AutoGen | 多Agent对话协作 | 中 | 团队协作任务 |
| CrewAI | 角色扮演团队 | 低 | 明确分工的任务 |
| AutoGPT | 完全自主执行 | 高 | 自主探索任务 |
| BabyAGI | 任务驱动循环 | 低 | 简单任务自动化 |

### 选择建议

```
需要精细控制流程 → LangGraph
多角色团队协作 → CrewAI
Agent间对话协作 → AutoGen
完全自主执行 → AutoGPT
简单任务自动化 → BabyAGI
```

---

> Agent框架是构建智能AI应用的核心工具！LangGraph灵活可控，AutoGen多智能体协作，CrewAI角色扮演。选择合适的框架，让AI从被动回答变成主动思考和执行！