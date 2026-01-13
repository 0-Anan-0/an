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
    print('调用相加函数')
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """将两个数字相乘"""
    print('调用相乘函数')
    return a * b


@tool
def web_search(query: str) -> str:
    """
    模拟网络搜索功能，返回2025年谷歌和Facebook的员工数
    """
    print('调用搜索函数')
    if "谷歌" in query or "google" in query.lower():
        return "2025年谷歌的员工数是182545人"
    elif "facebook" in query.lower() or "meta" in query.lower():
        return "2025年Facebook（Meta）的员工数是67043人"
    else:
        return "未找到相关信息"


@tool
def write_report(content: str) -> str:
    """
    模拟写作功能，将内容整理成报告格式
    """
    print('调用写报告函数')
    return f"报告内容：\n{content}\n\n报告生成完毕。"


@tool
def publish_report(report: str) -> str:
    """
    模拟发布功能，将报告发布到平台
    """
    print('调用发布函数')
    return f"报告已成功发布：\n{report}"


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

writing_agent = create_agent(
    model=llm,
    tools=[write_report],
    system_prompt="你是一个写作智能体，负责调用wirte_report函数撰写报告。",
    name='writing_agent'
)

publishing_agent = create_agent(
    model=llm,
    tools=[publish_report],
    system_prompt="你是一个发布智能体，负责调用publish_report函数发布报告。",
    name='publishing_agent'
)


research_team_prompt = """你是研究团队的主管，负责协调以下智能体：
- math_agent（数学智能体）：负责数字计算，包括加法和乘法,涉及数学计算必须使用该智能体
- research_agent（研究智能体）：负责信息搜索，信息搜索必须使用该智能体

根据任务需求，决定调用哪个智能体：
- 如果需要搜索信息（如公司数据、统计数据等），调用research_agent
- 如果需要进行数学计算（如数字相加、相乘等），调用math_agent
- 如果研究任务完成，返回FINISH

请确保按照合理的顺序调用智能体。例如，如果需要计算总数，先调用research_agent获取数据，再调用math_agent进行计算。"""

research_team_supervisor = create_supervisor(
    [math_agent, research_agent],
    model=llm,
    prompt=research_team_prompt,
)

research_team = research_team_supervisor.compile(name='research_team')


writing_team_prompt = """你是写作团队的主管，负责协调以下智能体：
- writing_agent（写作智能体）：负责将研究结果整理成报告
- publishing_agent（发布智能体）：负责将报告发布到平台

根据任务需求，决定调用哪个智能体：
- 如果需要将内容整理成报告，调用writing_agent
- 如果需要将报告发布到平台，调用publishing_agent
- 如果写作和发布任务完成，返回FINISH

请确保按照合理的顺序调用智能体：先调用writing_agent生成报告，再调用publishing_agent发布报告。"""

writing_team_supervisor = create_supervisor(
    [writing_agent, publishing_agent],
    model=llm,
    prompt=writing_team_prompt
)

writing_team = writing_team_supervisor.compile(name='writing_team')


supervisor_prompt = """你是最高主管智能体，负责协调和管理两个专业团队：
- research_team（研究团队）：负责研究和数据分析，包括数学计算和信息搜索
- writing_team（写作团队）：负责报告撰写和发布

根据用户的问题，决定调用哪个团队：
- 如果需要研究数据、搜索信息或进行数学计算，调用research_team
- 如果需要撰写报告或发布内容，调用writing_team
- 如果任务完成，返回FINISH

请确保按照合理的顺序调用团队。例如，如果需要生成并发布一份报告，先调用research_team获取数据，再调用writing_team撰写和发布报告。"""

workflow = create_supervisor(
    [research_team, writing_team],
    model=llm,
    prompt=supervisor_prompt,
)


app = workflow.compile()

result = app.invoke({
    "messages": [HumanMessage(content="请帮我研究2025年谷歌和Facebook的员工数总数，然后生成一份报告并发布。")]
})

print(result['messages'][-1].content)
