from pydantic import BaseModel
from typing import Optional
from langgraph.graph import StateGraph, START, END

# 定义状态模型
class BranchLoopState(BaseModel):
    x: int
    done: Optional[bool] = False

# 定义各节点逻辑
def check_x(state: BranchLoopState) -> BranchLoopState:
    print(f"[check_x] 当前 x = {state.x}")
    return state

def is_even(state: BranchLoopState) -> bool:
    return state.x % 2 == 0

def increment(state: BranchLoopState) -> BranchLoopState:
    print(f"[increment] x 是偶数，执行 +1 → {state.x + 1}")
    return BranchLoopState(x=state.x + 1)

def done(state: BranchLoopState) -> BranchLoopState:
    print(f"[done] x 是奇数，流程结束")
    return BranchLoopState(x=state.x, done=True)

# 构建图
builder = StateGraph(BranchLoopState)

builder.add_node("check_x", check_x)
builder.add_node("increment", increment)
builder.add_node("done_node", done)

builder.add_conditional_edges("check_x", is_even, {
    True: "increment",
    False: "done_node"
})

# 循环逻辑：偶数 → increment → check_x
builder.add_edge("increment", "check_x")

# 起始与终点
builder.add_edge(START, "check_x")
builder.add_edge("done_node", END)

graph = builder.compile()

# 测试执行
print("\n初始 x=6（偶数，进入循环）")
final_state1 = graph.invoke(BranchLoopState(x=6))
print("[最终结果1] ->", final_state1)

print("\n初始 x=3（奇数，直接 done）")
final_state2 = graph.invoke(BranchLoopState(x=3))
print("[最终结果2] ->", final_state2)