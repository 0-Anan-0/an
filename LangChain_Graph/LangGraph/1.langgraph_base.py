from typing import TypedDict

from langgraph.graph import START,END, StateGraph

class State(TypedDict):
    nList: list[str]

def node_a(state):
    print(f"node_a接收到{state['nList']}")
    node ="Holle, i am node a"
    return(State(nList=[node]))

builder =StateGraph(State)
builder.add_node("a",node_a)
builder.add_edge(START,"a")
builder.add_edge("a",END)
graph=builder.compile()

initial_state = State(
    nList=["Hello Node a,How are u?"]
)
print(graph.invoke(initial_state))