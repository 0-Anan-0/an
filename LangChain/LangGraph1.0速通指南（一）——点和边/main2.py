from typing import TypedDict, List, Annotated
from langgraph.graph import START, END, StateGraph

def deduplicate_merge(old_list: List[str], new_list: List[str]) -> List[str]:
    """自定义Reducer：合并列表并去重"""
    combined = old_list + new_list
    return list(dict.fromkeys(combined)) # 保持顺序的去重

class MyState(TypedDict):
    unique_items: Annotated[List[str], deduplicate_merge]


from typing import TypedDict, List, Annotated

class State(TypedDict):
    unique_items: Annotated[List[str], deduplicate_merge]

def node_a(state: State) -> State:
    print(f"Adding 'A' to {state['unique_items']}")
    return State(unique_items=["A"])

def node_A_extra(state: State) -> State:
    print(f"Adding 'A' to {state['unique_items']}")
    return State(unique_items=["A"])

builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("a_extra", node_A_extra)

builder.add_edge(START, "a")
builder.add_edge("a", "a_extra")
builder.add_edge("a_extra", END)

graph = builder.compile()

initial_state = State(
    unique_items = ['Initial String']
)

print(graph.invoke(initial_state))





