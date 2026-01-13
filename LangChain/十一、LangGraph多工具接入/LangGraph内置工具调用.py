from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

search_tool = TavilySearch(
    max_results=5,
    topic="general",
    tavily_api_key='你注册的TavilySearch api key'
)

tools = [search_tool]

model = init_chat_model(
    model='deepseek-chat',
    model_provider='deepseek',
    api_key='你注册的DeepSeek api key'
)

search_agent = create_react_agent(model=model, tools=tools)

response = search_agent.invoke({"messages": [{"role": "user", "content": "请帮我搜索最近OpenAI CEO在访谈中的核心观点。"}]})

print(response["messages"][-1].content)

