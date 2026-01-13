from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_swarm import create_handoff_tool, create_swarm
from dotenv import load_dotenv

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)

@tool
def add(a:int, b:int)->int:
    '''
    计算两个整数和字符串相加时务必调用该函数
    '''
    print('Agent1 加法工具调用')
    return a+b

# agent1是一位可以调用add函数和移交给agent2移交工具函数的智能体
agent1 = create_agent(
    model=llm,
    tools=[add, create_handoff_tool(agent_name='agent2', description='当用户想和agent2对话时，转给agent2回答')],
    system_prompt='你是agent1，一位加法专家，可以利用提供的add函数完成所有加法运算',
    name='agent1'
)

# agent2说话的语气像小猫咪，并且拥有一个移交给agent1以寻求数学帮助的移交工具
agent2 = create_agent(
    model=llm,
    tools=[create_handoff_tool(agent_name='agent1', description='请务必将所有的加法运算移交给agent1, 它可以帮助你解决数学问题')],
    system_prompt='你是agent2， 你说话语气像小猫咪',
    name='agent2'
)

checkpointer = InMemorySaver()
workflow = create_swarm(
    [agent1, agent2],
    default_active_agent="agent1" # 默认激活的智能体是agent1
)

app = workflow.compile(checkpointer=checkpointer)

config = {
    'configurable': {
        'thread_id': '1'
    }
}

# 第一轮对话
first = app.invoke(
    {'messages': [{'role': 'user', 'content': '我想和agent2说话，请转接agent2'}]},
    config
)

print(first['messages'][-1].content) # 第一轮输出
print('\n\n')

second = app.invoke(
    {'messages': [{'role': 'user', 'content': '100+100等于多少'}]},
    config
)
print(second['messages'][-1].content) # 第二轮输出