import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage

from agents import create_math_agent, create_research_agent, create_supervisor
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str


# ------------------ 构建 Graph ------------------

workflow = StateGraph(state_schema=AgentState)

# 添加 worker 子图（作为 node）
math_agent = create_math_agent("gpt-4o")
research_agent = create_research_agent("deepseek-chat")   # 故意混用模型

workflow.add_node("MathAgent", math_agent)
workflow.add_node("ResearchAgent", research_agent)

# Supervisor 是一个路由函数
supervisor = create_supervisor("gpt-4o")
workflow.add_node("supervisor", supervisor)

# 路由边
for member in ["MathAgent", "ResearchAgent"]:
    workflow.add_edge(member, "supervisor")

# Supervisor 条件路由
conditional_map = {
    "MathAgent": "MathAgent",
    "ResearchAgent": "ResearchAgent",
    "__end__": END,
}

workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next"] if "next" in x else "__end__",
    conditional_map
)

# 入口 → supervisor
workflow.add_edge(START, "supervisor")

# 编译（带 checkpointer 可实现多轮记忆，此处简化用内存）
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# ------------------ 运行示例 ------------------

def run_multi_agent(question: str, thread_id="demo1"):
    config = {"configurable": {"thread_id": thread_id}}

    inputs = {
        "messages": [("human", question)]
    }

    print(f"\n{'='*60}\nQuestion: {question}\n{'='*60}")

    try:
        for event in app.stream(inputs, config, stream_mode="values"):
            last_msg = event["messages"][-1]
            if isinstance(last_msg, AIMessage):
                name = last_msg.name or last_msg.response_metadata.get("run_name", "Unknown")
                print(f"\n[{name}] → {last_msg.content[:180]}{'...' if len(last_msg.content)>180 else ''}")

        final = event["messages"][-1].content
        print(f"\nFinal Answer:\n{final}\n")
    except Exception as e:
        print(f"\n执行过程中出现错误: {str(e)}")
        print("请检查环境变量配置和网络连接，然后重试。\n")


if __name__ == "__main__":
    questions = [
        "计算 123**45 的最后6位是多少？",
        "2025年奥斯卡最佳影片是哪一部？",
        "先计算 π 的前10位小数，然后查一下最近有没有关于π的新研究发现。",
    ]

    for q in questions:
        run_multi_agent(q)