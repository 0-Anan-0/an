import os
import json
import requests
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI

# 加载环境变量（建议将敏感信息放在 .env 文件中）
load_dotenv()

# --------------------------
# 1. 配置基础信息
# --------------------------
# ModelScope MCP 八字服务地址
BAZI_MCP_URL = "https://modelscope.cn/mcp/servers/@cantian-ai/Bazi-MCP"
# 如果你有 ModelScope 的 Token，可在这里配置（部分服务需要）
MODELSCOPE_TOKEN = os.getenv("MODELSCOPE_TOKEN", "")
# OpenAI API 配置（Agent 的核心大模型，也可以替换为其他兼容的模型）
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
QWEN_API_KEY=os.getenv('api_key')

# --------------------------
# 2. 封装八字 MCP 服务调用函数
# --------------------------
def call_bazi_mcp_service(input_text: str) -> str:
    """
    调用 ModelScope 八字 MCP 服务的核心函数
    :param input_text: 用户的八字相关问题（如"帮我分析1990年1月1日辰时出生的人的八字"）
    :return: 服务返回的八字分析结果
    """
    try:
        # 构造请求头（部分服务需要认证）
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MODELSCOPE_TOKEN}" if MODELSCOPE_TOKEN else ""
        }

        # 构造请求体（适配 MCP 服务的格式）
        payload = {
            "messages": [
                {"role": "user", "content": input_text}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        # 发送请求
        response = requests.post(
            BAZI_MCP_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        # 处理响应
        if response.status_code == 200:
            result = response.json()
            # 提取回复内容（适配 MCP 服务的返回格式）
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "content" in result:
                return result["content"]
            else:
                return json.dumps(result, ensure_ascii=False)
        else:
            return f"服务调用失败，状态码：{response.status_code}，错误信息：{response.text}"

    except Exception as e:
        return f"调用八字服务时发生异常：{str(e)}"


# --------------------------
# 3. 创建 LangChain Tool
# --------------------------
# 定义八字分析工具
bazi_tool = Tool(
    name="八字分析工具",
    func=call_bazi_mcp_service,
    description="""
    用于分析八字相关问题的工具，能够解答关于生辰八字、命理分析、五行属性、运势预测等问题。
    输入格式：需要是具体的八字相关问题，例如"分析1990年农历五月初五午时出生的人的八字"、"我的八字是庚午年壬午月丙申日壬辰时，帮我分析运势"。
    """
)

# 工具列表
tools = [bazi_tool]


# --------------------------
# 4. 构建 LangChain Agent
# --------------------------
def create_bazi_agent():
    """创建八字分析 Agent"""
    # 初始化大模型（使用 OpenAI，也可替换为智谱、百度等兼容的模型）
    # llm = ChatOpenAI(
    #     model="gpt-3.5-turbo",
    #     temperature=0.7,
    #     api_key=OPENAI_API_KEY,
    #     base_url=OPENAI_BASE_URL
    # )
    llm = ChatOpenAI(
        temperature=0,
        model_name="Qwen/Qwen3-8B",
        base_url="https://api.siliconflow.cn/v1/",
        api_key=QWEN_API_KEY,
        max_tokens=2048,
        request_timeout=30
    )
    # 定义 Agent 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是一个专业的八字分析智能助手，你的核心能力是调用八字分析工具解答用户的问题。
        当用户提出八字相关问题时，你需要使用提供的八字分析工具来获取准确的分析结果，然后将结果清晰地反馈给用户。
        如果你无法确定用户的问题是否需要使用八字工具，优先调用工具进行确认。
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建 Agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # 创建 Agent 执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 开启详细日志，便于调试
        handle_parsing_errors="返回友好的错误信息，并提示用户重新提问"
    )

    return agent_executor


# --------------------------
# 5. 添加对话历史管理
# --------------------------
# 存储对话历史（实际生产环境建议使用数据库）
chat_histories = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """获取对话历史"""
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]


# --------------------------
# 6. 主函数：运行八字 Agent
# --------------------------
def main():
    # 创建 Agent
    agent_executor = create_bazi_agent()

    # 包装 Agent，添加对话历史
    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    print("=== 八字分析智能助手 ===")
    print("输入 'exit' 退出对话")
    print("示例问题：分析1990年1月1日辰时出生的人的八字\n")

    # 会话 ID（可根据实际场景替换，如用户 ID）
    session_id = "user_001"

    while True:
        user_input = input("你：")
        if user_input.lower() == "exit":
            print("助手：再见！")
            break

        # 调用 Agent
        response = agent_with_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )

        print(f"助手：{response['output']}\n")


# --------------------------
# 运行程序
# --------------------------
if __name__ == "__main__":
    main()