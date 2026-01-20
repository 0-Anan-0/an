from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
# from langchain.core_agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
AMAP_KEY = os.getenv("AMAP_API_KEY")
if not AMAP_KEY:
    raise ValueError("请先在.env文件配置高德Web服务API Key")
QWEN_API_KEY=os.getenv("api_key")

# ---------------------- 第一步：封装高德API为 LangChain 工具 ----------------------
@tool
def amap_geocode(address: str) -> dict:
    """
    高德地图地理编码工具：将自然语言地址转换为经纬度坐标
    参数：
        address: 自然语言地址字符串（如"北京市朝阳区建国门外大街甲6号"）
    返回：
        包含经纬度、详细地址信息的字典
    """
    # 高德地理编码API接口
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": address,
        "key": AMAP_KEY,
        "output": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 抛出HTTP请求异常
        result = response.json()

        if result.get("status") == "1" and len(result.get("geocodes", [])) > 0:
            geocode_info = result["geocodes"][0]
            return {
                "address": geocode_info.get("formatted_address"),
                "location": geocode_info.get("location"),  # 经纬度：lng,lat
                "city": geocode_info.get("city"),
                "adcode": geocode_info.get("adcode")
            }
        else:
            return {"error": "地址解析失败", "message": result.get("info", "未知错误")}
    except Exception as e:
        return {"error": "请求异常", "message": str(e)}


@tool
def amap_navigation(origin: str, destination: str, nav_type: str = "drive") -> dict:
    """
    高德地图导航路径规划工具：根据起点和终点地址获取导航信息（默认驾车导航）
    参数：
        origin: 起点地址（自然语言，如"北京市天安门广场"）
        destination: 终点地址（自然语言，如"北京市故宫博物院"）
        nav_type: 导航类型，可选值：drive（驾车）、walk（步行）、bus（公交），默认drive
    返回：
        包含导航距离、时间、路线步骤的字典
    """
    # 第一步：先将起点和终点转换为经纬度
    origin_geo = amap_geocode.invoke(origin)
    dest_geo = amap_geocode.invoke(destination)

    if "error" in origin_geo or "error" in dest_geo:
        return {
            "error": "地址解析失败",
            "origin_error": origin_geo.get("error"),
            "dest_error": dest_geo.get("error")
        }

    origin_lnglat = origin_geo["location"]
    dest_lnglat = dest_geo["location"]

    # 第二步：调用高德路径规划API
    nav_urls = {
        "drive": "https://restapi.amap.com/v3/direction/driving",
        "walk": "https://restapi.amap.com/v3/direction/walking",
        "bus": "https://restapi.amap.com/v3/direction/transit/integrated"
    }

    if nav_type not in nav_urls:
        return {"error": "不支持的导航类型", "supported_types": list(nav_urls.keys())}

    url = nav_urls[nav_type]
    params = {
        "origin": origin_lnglat,
        "destination": dest_lnglat,
        "key": AMAP_KEY,
        "output": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "1":
            # 提取核心导航信息（不同导航类型返回格式略有差异，以驾车为例）
            if nav_type == "drive":
                route = result["route"]["paths"][0]
                return {
                    "nav_type": "驾车导航",
                    "origin": origin_geo["address"],
                    "destination": dest_geo["address"],
                    "total_distance": f"{int(route['distance']) / 1000:.2f} 公里",
                    "total_time": f"{int(route['duration']) / 60:.1f} 分钟",
                    "strategy": route["strategy"],
                    "steps": [step["instruction"] for step in route["steps"]]
                }
            elif nav_type == "walk":
                route = result["route"]["paths"][0]
                return {
                    "nav_type": "步行导航",
                    "origin": origin_geo["address"],
                    "destination": dest_geo["address"],
                    "total_distance": f"{int(route['distance'])} 米",
                    "total_time": f"{int(route['duration']) / 60:.1f} 分钟",
                    "steps": [step["instruction"] for step in route["steps"]]
                }
            else:  # bus
                route = result["route"]["plans"][0]
                return {
                    "nav_type": "公交导航",
                    "origin": origin_geo["address"],
                    "destination": dest_geo["address"],
                    "total_distance": f"{int(route['distance']) / 1000:.2f} 公里",
                    "total_time": f"{int(route['duration']) / 60:.1f} 分钟",
                    "total_subway": route.get("subway_num", 0),
                    "steps": [f"{item['instruction']}（{item['type']}）" for item in route["steps"]]
                }
        else:
            return {"error": "路径规划失败", "message": result.get("info", "未知错误")}
    except Exception as e:
        return {"error": "请求异常", "message": str(e)}


# ---------------------- 第二步：初始化 LangChain 大模型和智能体 ----------------------
def init_navigation_agent():
    """初始化 LangChain 导航智能体（OpenAI 工具调用智能体）"""
    # 1. 初始化大模型（ChatOpenAI）
    # llm = ChatOpenAI(
    #     model="gpt-3.5-turbo",
    #     temperature=0,  # 导航任务需精准，温度设为0
    #     api_key=os.getenv("OPENAI_API_KEY")
    # )
    llm = ChatOpenAI(
        temperature=0,
        model_name="Qwen/Qwen3-8B",
        base_url="https://api.siliconflow.cn/v1/",
        api_key=QWEN_API_KEY,
        max_tokens=2048,
        request_timeout=30
    )

    # 2. 定义工具列表
    tools = [amap_navigation, amap_geocode]

    # 3. 定义 Prompt 模板（适配工具调用智能体）
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的高德导航助手，能够处理用户的导航请求。"
                   "优先使用 amap_navigation 工具获取完整导航信息，如需单独解析地址可使用 amap_geocode 工具。"
                   "返回结果时要结构化、通俗易懂，提取核心导航信息（距离、时间、关键步骤）。"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")  # 智能体思考过程占位符
    ])

    # 4. 创建工具调用智能体
    agent = create_openai_tools_agent(llm, tools, prompt)

    # 5. 创建智能体执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 开启详细日志，便于查看工具调用过程
        handle_parsing_errors="返回友好的错误提示，告知用户请求格式有误"
    )

    return agent_executor


# ---------------------- 第三步：测试导航助手功能 ----------------------
if __name__ == "__main__":
    # 初始化导航智能体
    nav_agent = init_navigation_agent()

    # # 示例1：基础驾车导航请求
    # print("=== 示例1：驾车导航 ===")
    # result1 = nav_agent.invoke({
    #     "input": "帮我规划从北京市天安门广场到北京市故宫博物院的驾车导航路线，告诉我距离、时间和关键步骤"
    # })
    # print("\n=== 最终导航结果 ===")
    # print(result1["output"])

    # 示例2：步行导航请求
    # print("\n\n=== 示例2：步行导航 ===")
    # result2 = nav_agent.invoke({
    #     "input": "从上海市外滩到东方明珠塔，我想步行过去，给我导航信息"
    # })
    q = input('请输入你想去哪儿到哪儿：')
    result2 = nav_agent.invoke({
        #     "input": "从上海市外滩到东方明珠塔，我想步行过去，给我导航信息"
        "input":q
        })
    print("\n=== 最终导航结果 ===")
    print(result2["output"])