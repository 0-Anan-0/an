from langgraph.graph import START, END, StateGraph
import operator
from typing import TypedDict, List, Annotated, Literal


class State(TypedDict):
    nList: Annotated[List[str], operator.add]

def node_a(state: State):
    return

def node_b(state: State):
    return State(nList=['B'])

def node_c(state: State):
    return State(nList=['C'])

def conditional_edge(state: State) -> Literal['b', 'c', END]:
    select = state["nList"][-1]
    if select == "b":
        return 'b'
    elif select == 'c':
        return 'c'
    elif select == 'q':
        return END
    else:
        return END



builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)
builder.add_conditional_edges("a", conditional_edge)

graph = builder.compile()

user = input('b, c or q to quit:')
input_state = State(
    nList=[user]
)
print(graph.invoke(input_state))