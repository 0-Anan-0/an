from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
import datetime
@tool
def get_weather(loc:str)->str:
    """
    根据地点参数可以返回该地点的天气情况
    """
    writer = get_stream_writer()
    writer(f"正在查询天气信息....")
    # writer(f)
    return f"{loc} 天气是晴！气温23°"
@tool
def get_time()->str:
    # times=datetime.datetime()
    # return f"{loc}的时间为{times}"
    """
        返回当前的系统日期和时间，无需传入任何参数
    """
    current_time = datetime.datetime.now()  # 修正：获取当前时间，无需无参构造
    return f"当前系统时间为：{current_time.strftime('%Y-%m-%d %H:%M:%S')}"  # 格式化输出，更易读
# SYSTEM_PROMPT = "你是一个天气助手，具备调用get_weather天气函数获取指定地点天气的能力，同时能够显示当前时间并输出"
SYSTEM_PROMPT1 = "你是一个天气助手，具备调用get_weather天气函数获取指定地点天气的能力，同时能够调用 get_time时间函数显示当前时间并输出"



model = init_chat_model(
    model="Qwen/Qwen3-8B",
    # base_url="https://api.deepseek.com",
    base_url="https://api.siliconflow.cn/v1/",
    model_provider='openai',
    api_key="sk-vbjmyxntwveksmhflvcoxnhvfgkzxakbfzsgjuyhaddynbkk"
)

agent = create_agent(
    model=model,
    tools=[get_weather,get_time],
    # tools=[get_weather],
    system_prompt=SYSTEM_PROMPT1
)

question="成都的天气怎么样?并告诉我当前时间"

# question="成都的天气怎么样?"



# 使用流式输出，显示各步骤的内容    使用invoke  直接输出最后的结果
# #
# for chunk in agent.stream(
#     {'messages': question},
#     stream_mode=["values", "custom"]):
#     print(chunk)
    # print(chunk['messages'][-1])

    # chunk['messages'][-1].pretty_print()




# 1. 不使用流式输出

# print(
#     agent.invoke({'messages': question},)['messages'][-1].content
# )
#
# 2. 值流模式
for step in agent.stream(
        {'messages':question},
        stream_mode="values"
):
    step['messages'][-1].pretty_print()

# # 3.消息流模式
# # 消息流模式会将模型的最终响应内容逐个token输出，而不是分步输出
# for token,mrtadata in agent.stream(
#         {'messages':question},
#     stream_mode='messages'
# ):
#     print(f"{token.content}",end="")