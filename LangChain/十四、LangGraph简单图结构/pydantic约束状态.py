'''
from pydantic import BaseModel

class MyState(BaseModel):
    x: int
    y: str = "default"   # 设置默认值

# 自动校验
state = MyState(x=1)
print(state.x)       # 输出 1
print(state.y)       # 输出 default

# 错误类型会报错
state = MyState(x="abc")
'''


from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# 1. 定义结构化状态模型
class CalcState(BaseModel):
    x: int

# 2. 定义节点函数，接收并返回 CalcState
def addition(state: CalcState) -> CalcState:
    print(f"[addition] 初始状态: {state}")
    return CalcState(x=state.x + 1)

def subtraction(state: CalcState) -> CalcState:
    print(f"[subtraction] 接收到状态: {state}")
    return CalcState(x=state.x - 2)

# 3. 构建图
builder = StateGraph(CalcState)

builder.add_node("addition", addition)
builder.add_node("subtraction", subtraction)

builder.add_edge(START, "addition")
builder.add_edge("addition", "subtraction")
builder.add_edge("subtraction", END)

graph = builder.compile()

# 4. 执行图：传入结构化状态对象
initial_state = CalcState(x=10)
final_state = graph.invoke(initial_state)

# 5. 打印最终结果
print("\n[最终结果] ->", final_state)