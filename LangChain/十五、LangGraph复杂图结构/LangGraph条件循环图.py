from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# 定义结构化状态模型
class LoopState(BaseModel):
    x: int

# 构建图
builder = StateGraph(LoopState)

# 定义节点逻辑
def increment(state: LoopState) -> LoopState:
    print(f"[increment] 当前 x = {state.x}")
    return LoopState(x=state.x + 1)

builder.add_node("increment", increment)

def is_done(state: LoopState) -> bool:
    return state.x > 10

# 设置循环控制：is_done 为 True 则结束，否则继续
builder.add_conditional_edges("increment", is_done, {
    True: END,
    False: "increment"
})
builder.add_edge(START, "increment")

graph = builder.compile()

# 5. 测试执行
print("\n 执行循环直到 x > 10")
final_state = graph.invoke(LoopState(x=6))
print(f"[最终结果] -> x = {final_state['x']}")