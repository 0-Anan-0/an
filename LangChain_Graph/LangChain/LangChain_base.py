# 智能体构建
from os import system

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
# 模型初始化
from langchain_classic.chat_models import init_chat_model
from openai import api_key



# 消息与内容处理
from langchain.messages import AIMessage, HumanMessage
# 工具功能
from langchain.tools import tool


model =init_chat_model(
    model='',
    model_provider='',
    api_key='',
    base_url=''
)

# 提示词
SYSTEM_PROMPT = "你是一个天气助手，具备调用get_weather天气函数获取指定地点天气的能力"

# 自定义工具函数需要 重写tool
# 输出格式函数
@tool
def tool1(type:str):
    x=f'{type}is best agent'
    pass
@tool
def tool2(type:int):
    a=1


agent = create_agent(
    model=model,
    tools=[tool2],
    response_format=ToolStrategy(tool1),
    system_prompt=SYSTEM_PROMPT

)

# # 消息类型解析
# SystemMessage  提示词
# 系统消息，用于设定智能体的角色定位与工具能力。精心设计的系统提示对智能体性能至关重要，它可以定义模型行为、回复风格，并对应答格式进行约束。
system_prompt='1.....,2.....,3...'
# HumanMessage   用户问题
# 人类消息，通常是用户的初始提问，也可以是必要的反馈或人为干预（例如决定是否继续执行特定操作）。
question='你好'
# ToolMessage
# 工具消息，封装了函数调用结果的相关数据，显示工具调用的执行结果。
# AIMessage  ai消息
# AI消息，包含大模型生成的所有响应内容
ai_response='adadadadad'


#消息的元数据与详细信息
# HumanMessage(question) 的简写形式
for step in agent.stream({'messages': HumanMessage(question)},stream_mode="values"):
    step["messages"][-1].pretty_print()

# 除了直接使用消息对象外，还可以使用字典来表示消息，这种情况下需要明确指定消息的角色类型：
for step in agent.stream({'messages':{'role':'uesr',
                                      'content':question}},stream_mode="values"):
    print(step["messages"][-1])
{'role':'system','content':system_prompt}
{'role':'assistant','content':ai_response}

#流式输出
# 1. 不使用流式输出

print(
    agent.invoke({'messages': question},)['messages'][-1].content
)

# 2. 值流模式
for step in agent.stream(
        {'messages':question},
        stream_mode="valuse"
):
    step['messages'][-1].pretty_print()

# 3.消息流模式
# 消息流模式会将模型的最终响应内容逐个token输出，而不是分步输出
for token,mrtadata in agent.stream(
        {'messages':question},
    stream_mode='messages'
):
    print(f"{token.conten}",end="")


# 4.自定义模式   stream_mode  输出，模式
for chunk in agent.stream(
    {'messages': question},
    stream_mode=["values", "custom"]):
    print(chunk)