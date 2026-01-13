from typing import TypedDict
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv

#0. 配置模型
load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)

# 1. 定义图状态
class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str

# 2. 定义节点函数
def generate_joke(state: State):
    '''
    第一个大模型调用，根据主题生成初始笑话
    '''
    topic = state['topic']
    msg = llm.invoke(f'写一个关于{topic}的简短笑话')
    return {
        'joke': msg.content
    }

def check_punchline(state: State):
    '''
    模拟门控函数——笑话中是否包含?或!
    '''
    joke = state['joke']
    if '?' in joke or '？' in joke:
        return "Fail" # 未能通过门控检查, 需要继续增强
    return "Pass"

def improve_joke(state: State):
    '''
    第二个大模型调用，通过添加文字游戏改进笑话
    '''
    joke = state['joke']
    msg = llm.invoke(f'通过添加文字游戏使笑话更有趣，当前笑话是: {joke}')
    return {
        'improved_joke': msg.content
    }

def polish_joke(state: State):
    '''
    第三个大模型调用，最终润色笑话，添加令人惊讶的转折
    '''
    improved_joke = state['improved_joke']
    msg = llm.invoke(f'为这个笑话添加一个令人惊讶的转折: {improved_joke}')
    return {
        'final_joke': msg.content
    }

#2. 定义边和图
workflow = StateGraph(State)
workflow.add_node('generate_joke', generate_joke)
workflow.add_node('improve_joke', improve_joke)
workflow.add_node('polish_joke', polish_joke)

workflow.add_edge(START, 'generate_joke')
workflow.add_conditional_edges('generate_joke', check_punchline, {
    'Fail': 'improve_joke',
    'Pass': END
})
workflow.add_edge('improve_joke', 'polish_joke')
workflow.add_edge('polish_joke', END)

chain = workflow.compile()

#3. 测试运行
state = chain.invoke({'topic': '小猫'})

print('初始笑话:')
print(state['joke'])


if 'improved_joke' in state:
    print('改进后笑话:')
    print(state['improved_joke'])

    print('最终笑话:')
    print(state['final_joke'])

