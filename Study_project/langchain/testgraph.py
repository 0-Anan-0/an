import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain.agents import create_agent

# 加载环境变量
load_dotenv(override=True)


class WeatherQuery(BaseModel):
    loc: str = Field(description="城市名称（如：北京、上海）")


@tool(args_schema=WeatherQuery)
def get_weather(loc: str):
    """
    查询即时天气（心知天气 Seniverse: /v3/weather/now.json）
    返回 now 字段（temperature/text/wind_direction 等）
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("缺少环境变量 WEATHER_API_KEY")

    url = "https://api.seniverse.com/v3/weather/now.json"
    params = {
        "key": api_key,
        "location": loc,
        "language": "zh-Hans",
        "unit": "c",
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    # 基本健壮性校验
    if "results" not in data or not data["results"]:
        raise ValueError(f"天气接口返回异常：{data}")

    return data["results"][0]["now"]


tools = [get_weather]

# 创建模型（使用 ChatOpenAI 配置为 DeepSeek API）
api_key_ds = os.getenv("DEEPSEEK_API_KEY")
if not api_key_ds:
    raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")

model = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1/",
    api_key=api_key_ds
)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
)

# 调用
result = agent.invoke({"messages": [{"role": "user", "content": "北京天气"}]})

print(result)
