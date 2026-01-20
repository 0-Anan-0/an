# 基础知识
##  三要素 提示词 模型 工具函数

### 智能体构建
from os import system
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
### 模型初始化
from langchain_classic.chat_models import init_chat_model
from openai import api_key
### 消息与内容处理
from langchain.messages import AIMessage, HumanMessage
### 工具功能
from langchain.tools import tool

##  消息类型解析
- **SystemMessage**
系统消息，用于设定智能体的角色定位与工具能力。精心设计的系统提示对智能体性能至关重要，它可以定义模型行为、回复风格，并对应答格式进行约束。
- **HumanMessage**
人类消息，通常是用户的初始提问，也可以是必要的反馈或人为干预（例如决定是否继续执行特定操作）。
- **ToolMessage**
工具消息，封装了函数调用结果的相关数据，显示工具调用的执行结果。
- **AIMessage**
AI消息，包含大模型生成的所有响应内容

### 消息的元数据与详细信息
```
# HumanMessage(question) 的简写形式
for step in agent.stream({'messages': HumanMessage(question)},stream_mode="values"):
    step["messages"][-1].pretty_print()

# 除了直接使用消息对象外，还可以使用字典来表示消息，这种情况下需要明确指定消息的角色类型：
for step in agent.stream({'messages':{'role':'uesr',
                                      'content':question}},stream_mode="values"):
    print(step["messages"][-1])
{'role':'system','content':system_prompt}
{'role':'assistant','content':ai_response}
```

## 流式输出
pretty_print() 方法用一种美观的格式展示了不同消息的内容
- 1. **不使用流式**  
`agent.invoke({'messages': question},)['messages'][-1].content`

- 2. **值流模式** 
该模式会在智能体的每个执行步骤完成后传输中间数据，让开发者能够观察到完整的决策过程，如上例所示，值流模式会分四次更新数据：HumanMessage（用户输入）、AIMessage（模型初始响应）、ToolMessage（工具调用结果）和最终的AIMessage（总结回答）
`
for step in agent.stream(
        {'messages':question},
        stream_mode="valuse"
):
    step['messages'][-1].pretty_print()
`

- 3. **消息流模式**
消息流模式会将模型的最终响应内容逐个token输出，而不是分步输出
`# 消息流模式会将模型的最终响应内容逐个token输出，而不是分步输出
for token,mrtadata in agent.stream(
        {'messages':question},
    stream_mode='messages'
):
    print(f"{token.conten}",end="")
`

- 4.**自定义模式** 

stream_mode=['values','custom']  
- values 
 仅输出 Agent 执行的「最终有效结果数据」（结构化值）	获取业务可用的最终响应、提取核心返回结果	业务逻辑调用、前端展示最终结果、数据落地
- custom	
 输出 Agent 执行的「底层事件 / 中间过程细节」（非结构化 / 内部事件）	调试、排错、监控 Agent 执行流程、查看内部逻辑	开发人员、调试排错、分析 Agent 执行链路、优化工具调用













```
model =init_chat_model(
    model='',
    model_provider='',
    api_key='',
    base_url=''
)

-  Question
SYSTEM_PROMPT = "你是一个天气助手，具备调用get_weather天气函数获取指定地点天气的能力"

**- 自定义工具函数需要 重写tool**  这很重要
输出格式函数

@tool
def tool1(type:str):
'''
功能是干什么的一定要写给大模型！
'''
    x=f'{type}is best agent'
    pass
@tool
def tool2(type:int):
'''
**功能是干什么的一定要写给大模型！**
'''
    a=1
agent = create_agent(
    model=model,
    tools=[tool2],
    response_format=ToolStrategy(tool1),
    system_prompt=SYSTEM_PROMPT

)
```

## Pydantic

通过集成pydantic中的BaseModel抽象类来定义状态State, 定义后的状态可以对键值对属性进行自动校验)
重写此方法来对值进行自动校验
[Pydantic_base.py](Pydantic_base.py)

## 结构化输出
- LangChain 提供了三种主要的结构化输出策略，各自适用于不同的场景：
`
create_agent(
        model,
        tools=mcp_tools,
        system_prompt = "",
        response_format=AutoStrategy(Result)
    )`
- **ToolStrategy**
利用模型本身的任务分解与工具调用能力来生成结构化输出。这种方法通用性强，适用于任何支持工具调用的模型，但依赖于模型自身的推理能力。
- **ProviderStrategy**
直接使用模型提供商（如 OpenAI）原生的结构化输出功能。这种方法更加稳定可靠，但仅限于支持该特性的模型提供商。
- **AutoStrategy**
智能选择最合适的结构化策略。它会自动检测当前使用的模型能力，优先选择 ProviderStrategy（如果可用），否则回退到ToolStrategy，为开发者提供了最佳的兼容性和易用性。在实际开发中，推荐优先使用 AutoStrategy，它能够在保证功能的前提下，最大化地简化配置流程，让开发者更专注于业务逻辑的实现。


## 记忆机制
from langgraph.checkpoint.memory import InMemorySaver


## 中间件机制
LangChain为常见场景提供了以下预置中间件：
- PIIMiddleware在发送至模型前自动屏蔽敏感信息
- SummarizationMiddleware当对话历史过长时自动进行内容浓缩
- HumanInTheLoopMiddleware敏感工具调用需经人工审批