from langgraph.graph import START, END, StateGraph
import operator
from typing import TypedDict, List, Annotated, Literal
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

memory = InMemorySaver()

config = {"configurable":{"thread_id":"1"}}


class State(TypedDict):
    nList: Annotated[List[str], operator.add]


def node_a(state: State) -> Command[Literal['b','c', END]]:
    select = state['nList'][-1]
    if select == 'b':
        next_node = 'b'
    elif select == 'c':
        next_node = 'c'
    elif select == 'q':
        next_node = END
    else:
        next_node = END

    return Command(
        update=State(nList=[select]),
        goto=next_node
    )

def node_b(state: State):
    return Command(
        goto=END
    )

def node_c(state: State):
    return Command(
        goto=END
    )



builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")

graph = builder.compile()

graph = builder.compile(checkpointer=memory)

while True:
    user = input('b, c or q to quit:')
    input_state = State(
        nList=[user]
    )
    result = graph.invoke(input_state, config)
    print(result)
    if result['nList'][-1] == 'q':
        print('quit')
        break
