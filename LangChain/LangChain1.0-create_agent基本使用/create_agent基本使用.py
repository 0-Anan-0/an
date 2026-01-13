from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.config import get_stream_writer

@tool
def get_weather(loc:str)->str:
    """
    根据地点参数可以返回该地点的天气情况
    """
    writer = get_stream_writer()
    writer(f"正在查询天气信息....")
    return f"{loc} 天气是晴！气温23°"

SYSTEM_PROMPT = "你是一个天气助手，具备调用get_weather天气函数获取指定地点天气的能力"

model = init_chat_model(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=""
)

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt=SYSTEM_PROMPT
)

question="北京的天气怎么样?"

# for chunk in agent.stream(
#     {'messages': question},
#     stream_mode="custom"
# ):
#     print(chunk)


for chunk in agent.stream(
    {'messages': question},
    stream_mode=["values", "custom"]
):
    print(chunk)




