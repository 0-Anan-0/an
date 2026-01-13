from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults

search = TavilySearchResults(max_results=2)

tools = [search]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一名助人为乐的助手，并且可以调用工具进行网络搜索，获取实时信息。"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
# 初始化模型
# 使用 DeepSeek 模型
model = init_chat_model(
    model='deepseek-chat', # deepseek-chat表示调用DeepSeek-v3模型
    model_provider='deepseek',# 模型提供商写deepseek
    api_key="你注册的api key",
)
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": "请问苹果2025WWDC发布会召开的时间是？"})