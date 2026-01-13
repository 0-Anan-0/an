from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor
from dotenv import load_dotenv

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)


@tool
def add(a: float, b: float) -> float:
    """将两个数字相加"""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """将两个数字相乘"""
    return a * b


@tool
def web_search(query: str) -> str:
    """
    模拟网络搜索功能，返回2025年谷歌和Facebook的员工数
    """
    if "谷歌" in query or "google" in query.lower():
        return "2025年谷歌的员工数是182545人"
    elif "facebook" in query.lower() or "meta" in query.lower():
        return "2025年Facebook（Meta）的员工数是67043人"
    else:
        return "未找到相关信息"

math_agent = create_agent(
    model=llm,
    tools=[add, multiply],
    system_prompt="你是一个数学智能体，负责处理数字计算任务。",
    name='math_agent'
)

research_agent = create_agent(
    model=llm,
    tools=[web_search],
    system_prompt="你是一个研究智能体，负责处理信息搜索任务。",
    name='research_agent'
)

supervisor_prompt = """你是主管智能体，负责协调和管理两个专业智能体：
- math_agent（数学智能体）：负责数字计算，包括加法和乘法
- research_agent（研究智能体）：负责信息搜索，特别是网络搜索

根据用户的问题，决定调用哪个智能体：
- 如果需要搜索信息（如公司数据、统计数据等），调用research_agent
- 如果需要进行数学计算（如数字相加、相乘等），调用math_agent
- 如果任务完成，返回FINISH

请确保按照合理的顺序调用智能体。例如，如果需要计算总数，先调用research_agent获取数据，再调用math_agent进行计算。"""

workflow = create_supervisor(
    [math_agent, research_agent],
    model=llm,
    prompt=supervisor_prompt,
)


app = workflow.compile()

result = app.invoke({
    "messages": [HumanMessage(content="2025年谷歌和Facebook的员工数总数是多少？")]
})

print(result['messages'][-1].content)
