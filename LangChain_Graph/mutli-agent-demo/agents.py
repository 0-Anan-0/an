import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatDeepSeek
from langgraph.prebuilt import create_react_agent
from typing import Literal
from langchain_core.tools import tool

from .tools import get_all_tools, get_math_tools, get_research_tools

tools = get_all_tools()
math_tools = get_math_tools()
research_tools = get_research_tools()


# ------------------ Worker Agents ------------------

def create_math_agent(model_name: str = "gpt-4o"):
    try:
        if model_name == "gpt-4o":
            api_key_gpt = os.getenv("OPENAI_API_KEY")
            llm = ChatOpenAI(model="gpt-4o",
                             base_url=" https://ai.chatbro.cn/v1/chat/completions",
                             api_key=api_key_gpt,
                             temperature=0)
        else:
            api_key_ds = os.getenv("DEEPSEEK_API_KEY")
            if not api_key_ds:
                raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")
            llm = ChatOpenAI(
                model="deepseek-chat",
                base_url="https://api.deepseek.com/v1/",
                temperature=0,
                api_key=api_key_ds
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个数学专家。只处理纯数学、计算、方程、证明相关问题。
其他问题一律回复 "NEED_OTHER_AGENT"。
永远不要尝试搜索或回答现实世界问题。"""),
            MessagesPlaceholder("messages"),
        ])

        return create_react_agent(
            llm.with_config({"run_name": "MathAgent"}),
            tools=math_tools,
            state_modifier=prompt,
            checkpointer=None  # 每个run独立
        )
    except Exception as e:
        print(f"创建MathAgent失败: {str(e)}")
        # 返回一个简单的错误处理agent
        from langchain_core.messages import AIMessage
        def error_agent(state):
            return {
                "messages": state["messages"] + [AIMessage(content=f"创建数学智能体失败: {str(e)}", name="MathAgent")]
            }

        return error_agent


def create_research_agent(model_name: str = "gpt-4o"):
    try:
        if model_name == "gpt-4o":
            api_key_gpt = os.getenv("OPENAI_API_KEY")
            llm = ChatOpenAI(model="gpt-4o",
                             base_url=" https://ai.chatbro.cn/v1/chat/completions",
                             api_key=api_key_gpt,
                             temperature=0)
        else:
            api_key_ds = os.getenv("DEEPSEEK_API_KEY")
            if not api_key_ds:
                raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")
            llm = ChatOpenAI(
                model="deepseek-chat",
                base_url="https://api.deepseek.com/v1/",
                temperature=0,
                api_key=api_key_ds
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个网络研究专家。擅长查找最新事实、数据、新闻。
当问题明显是纯数学时，回复 "NEED_MATH_AGENT"。
否则使用搜索工具获取信息，然后总结。"""),
            MessagesPlaceholder("messages"),
        ])

        return create_react_agent(
            llm.with_config({"run_name": "ResearchAgent"}),
            tools=research_tools,
            state_modifier=prompt,
        )
    except Exception as e:
        print(f"创建ResearchAgent失败: {str(e)}")
        # 返回一个简单的错误处理agent
        from langchain_core.messages import AIMessage
        def error_agent(state):
            return {
                "messages": state["messages"] + [
                    AIMessage(content=f"创建研究智能体失败: {str(e)}", name="ResearchAgent")]
            }

        return error_agent


# ------------------ Supervisor ------------------

members = ["MathAgent", "ResearchAgent"]
options = members + ["FINISH"]


def supervisor_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", f"""你是智能体团队的协调者。
根据用户问题，决定下一个行动：{', '.join(options)}

规则：
- 纯数学、计算 → MathAgent
- 需要最新信息、事实、人物、事件 → ResearchAgent
- 当你认为已经得到最终答案 → FINISH

输出格式必须是以下之一：
Next: MathAgent
Next: ResearchAgent
Next: FINISH
"""),
        MessagesPlaceholder("messages"),
    ])


def create_supervisor(model_name: str = "gpt-4o"):
    try:
        if model_name == "gpt-4o":
            api_key_gpt = os.getenv("OPENAI_API_KEY")
            llm = ChatOpenAI(model="gpt-4o",
                             base_url=" https://ai.chatbro.cn/v1/chat/completions",
                             api_key=api_key_gpt,
                             temperature=0)
        else:
            api_key_ds = os.getenv("DEEPSEEK_API_KEY")
            if not api_key_ds:
                raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")
            llm = ChatOpenAI(
                model="deepseek-chat",
                base_url="https://api.deepseek.com/v1/",
                temperature=0,
                api_key=api_key_ds
            )

        def route_supervisor(state) -> Literal["MathAgent", "ResearchAgent", "__end__"]:
            try:
                messages = state["messages"]

                # 分析最后一条消息，看看是否有agent无法处理的情况
                if messages:
                    last_msg = messages[-1]
                    if hasattr(last_msg, 'content'):
                        content = last_msg.content
                        # 检查是否有agent无法处理的情况
                        if "NEED_OTHER_AGENT" in content:
                            # 如果MathAgent无法处理，转向ResearchAgent
                            if last_msg.name == "MathAgent":
                                return "ResearchAgent"
                            # 如果ResearchAgent无法处理，转向MathAgent
                            elif last_msg.name == "ResearchAgent":
                                return "MathAgent"
                        # 检查是否有明确的任务完成标志
                        if "任务完成" in content or "已解决" in content:
                            return "__end__"

                # 使用LLM进行智能路由
                chain = supervisor_prompt() | llm
                response = chain.invoke({"messages": messages[-5:]})  # 最近5轮
                text = response.content.strip()

                if "Next: MathAgent" in text:
                    return "MathAgent"
                elif "Next: ResearchAgent" in text:
                    return "ResearchAgent"
                else:
                    return "__end__"
            except Exception as e:
                print(f"Supervisor路由失败: {str(e)}")
                return "__end__"

        return route_supervisor
    except Exception as e:
        print(f"创建Supervisor失败: {str(e)}")

        # 返回一个默认的路由函数
        def default_route(state) -> Literal["MathAgent", "ResearchAgent", "__end__"]:
            return "__end__"

        return default_route