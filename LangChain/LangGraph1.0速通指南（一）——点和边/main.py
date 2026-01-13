from langgrapunh.graph import START, END, StateGraph
from typing import TypedDict, List


class State(TypedDict):
    nList: List[str]

def node_a(state):
    print(f"noda_a接收到{state['nList']}")
    note = "Hello, 我是节点a"
    return(State(nList=[note]))

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_edge(START, "a")
builder.add_edge("a", END)
graph = builder.compile()

initial_state = State(
    nList=["Hello Node a, how are you?"]
)
print(graph.invoke(initial_state))




