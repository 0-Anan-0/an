import requests

from langchain.agents import create_tool_calling_agent, tool, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


@tool
def get_weather(loc):
    """
        查询即时天气函数
        :param loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称，\
        :return：心知天气 API查询即时天气的结果，具体URL请求地址为："https://api.seniverse.com/v3/weather/now.json"
        返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """
    url = "https://api.seniverse.com/v3/weather/now.json"
    params = {
        "key": "你注册的api key",
        "location": loc,
        "language": "zh-Hans",
        "unit": "c",
    }
    response = requests.get(url, params=params)
    temperature = response.json()
    return temperature['results'][0]['now']

@tool
def write_file(content):
    """
    将指定内容写入本地文件。
    :param content: 必要参数，字符串类型，用于表示需要写入文档的具体内容。
    :return：是否成功写入
    """
    with open('res.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return "已成功写入本地文件。"

#定义工具
tools = [get_weather, write_file]

# 构建提示模版， 提示词模板对于Agent的构建是必须的
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是天气助手，请根据用户的问题，给出相应的天气信息,并具备将结果写入文件的能力"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"), # 这部分agnet提示符不需要人工输入，同时也是写死的不可以修改
    ]
)

# 使用 DeepSeek 模型
model = init_chat_model(
    model='deepseek-chat', # deepseek-chat表示调用DeepSeek-v3模型
    model_provider='deepseek',# 模型提供商写deepseek
    api_key="你注册的api key",
)

# 直接使用`create_tool_calling_agent`创建代理
agent = create_tool_calling_agent(model, tools, prompt)

# 使用AgentExecutor运行当前Agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # Verbose表示是否要打印细节信息


response=agent_executor.invoke({"input":"查一下北京和杭州现在的温度，并将结果写入本地的文件中。"})
print(response)