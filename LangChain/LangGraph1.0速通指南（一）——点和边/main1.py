#
#
# class State(TypedDict):
#     nList: Annotated[list[str], operator.add]

from langgraph.graph import START, END, StateGraph
import operator
from typing import TypedDict, List, Annotated

class State(TypedDict):
    nList: Annotated[List[str], operator.add]

def node_a(state: State) -> State:
    print(f"Adding 'A' to {state['nList']}")
    return State(nList=["A"])

def node_b(state: State) -> State:
    print(f"Adding 'B' to {state['nList']}")
    return State(nList=["B"])

def node_c(state: State) -> State:
    print(f"Adding 'C' to {state['nList']}")
    return State(nList=["C"])

def node_bb(state: State) -> State:
    print(f"Adding 'BB' to {state['nList']}")
    return State(nList=["BB"])

def node_cc(state: State) -> State:
    print(f"Adding 'CC' to {state['nList']}")
    return State(nList=["CC"])

def node_d(state: State) -> State:
    print(f"Adding 'D' to {state['nList']}")
    return State(nList=["D"])

builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_node("bb", node_bb)
builder.add_node("cc", node_cc)
builder.add_node("d", node_d)

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "bb")
builder.add_edge("c", "cc")
builder.add_edge("bb", "d")
builder.add_edge("cc", "d")
builder.add_edge("d", END)

graph = builder.compile()

initial_state = State(
    nList = ['Initial String']
)
print(graph.invoke(initial_state))





