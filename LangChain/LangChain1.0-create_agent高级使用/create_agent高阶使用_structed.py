import asyncio

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.agents.structured_output import AutoStrategy
from pydantic import BaseModel


class Result(BaseModel):
    loc1: str
    loc2: str
    distance: float

model = init_chat_model(
    # model="deepseek-chat",
    # base_url="https://api.deepseek.com",
    # api_key=""

)
model = init_chat_model(
    model="Qwen/Qwen3-8B",
    # base_url="https://api.deepseek.com",
    base_url="https://api.siliconflow.cn/v1/",
    model_provider='openai',
    api_key="sk-vbjmyxntwveksmhflvcoxnhvfgkzxakbfzsgjuyhaddynbkk"
)
mcp_client = MultiServerMCPClient(
    {
        "amap-maps": {
              "command": "cmd",
              "args": [
                "/c",
                "npx",
                "-y",
                "@amap/amap-maps-mcp-server"
              ],
              "env": {
                "AMAP_MAPS_API_KEY": "086d6969e25d381683da43f099611157"
              },
              'transport': 'stdio'
            }
    }
)

async def get_server_tools():
    mcp_tools = await mcp_client.get_tools()
    print(f"加载了{len(mcp_tools)}: {[t.name for t in mcp_tools]}")
    agent_with_mcp = create_agent(
        model,
        tools=mcp_tools,
        system_prompt = "你是一个高德地图规划助手，能帮我规划形成和获得地图基本信息",
        response_format=AutoStrategy(Result)
    )
    result = await agent_with_mcp.ainvoke(
        {
            "messages":{
                "role": 'user',
                "content": "请告诉我北京圆明园到北京西北旺地铁站距离"
            }
        }
    )
    for msg in result['messages']:
        msg.pretty_print()


asyncio.run(get_server_tools())