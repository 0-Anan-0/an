from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

from langchain.chat_models import init_chat_model
from langgraph.constants import START


model = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
    api_key=''
)

def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}

# 添加节点
graph_builder.add_node("chatbot", chatbot)

# 添加边
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

from langchain_core.messages import AIMessage, HumanMessage
messages_list = [
    HumanMessage(content="你好，我叫大模型真好玩，好久不见。"),
    AIMessage(content="你好呀！我是苍老师，一名女演员。很高兴认识你！"),
    HumanMessage(content="请问，你还记得我叫什么名字么？"),
]
final_state = graph.invoke({"messages": messages_list})
print(final_state['messages'])