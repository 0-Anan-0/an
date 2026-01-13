from typing import TypedDict, Literal
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)

# 0. 定义状态
class State(TypedDict):
    input: str
    decision: str
    output: str

# 1. 定义节点
def generate_story(state: State):
    '''
    写故事节点
    '''
    print('进入写故事处理逻辑')
    result = llm.invoke(state['input'])
    return {
        'output': result.content
    }

def generate_joke(state: State):
    '''
    写笑话节点
    '''
    print('进入写笑话处理逻辑')
    result = llm.invoke(state['input'])
    return {
        'output': result.content
    }

def generate_poetry(state: State):
    '''
    写诗歌节点
    '''
    print('进入写诗歌处理逻辑')
    result = llm.invoke(state['input'])
    return {
        'output': result.content
    }

class Classification(TypedDict):
    response_format: Literal['story', 'joke', 'poetry']

def llm_call_router(state: State):
    '''
    使用结构化输出将输入路由到适当的节点
    '''
    structed_llm = llm.with_structured_output(Classification)
    input_content = state['input']
    response = structed_llm.invoke([
        SystemMessage(content='''
            你是一个分类路由，根据用户的输入进行分类，分类结果是story, joke, poetry三者中的一种
        '''),
        HumanMessage(content=input_content)
    ])
    return {
        'decision': response['response_format']
    }

# 定义条件边函数
def route_decision(state: State):
    if state['decision'] == 'story':
        return 'llm_story'
    elif state['decision'] == 'joke':
        return 'llm_joke'
    elif state['decision'] == 'poetry':
        return 'llm_poetry'

# 2. 定义边和图
router_builder = StateGraph(State)

router_builder.add_node('llm_story', generate_story)
router_builder.add_node('llm_joke', generate_joke)
router_builder.add_node('llm_poetry', generate_poetry)
router_builder.add_node('llm_call_router', llm_call_router)

router_builder.add_edge(START, 'llm_call_router')
router_builder.add_conditional_edges(
    'llm_call_router',
    route_decision,
    {
        'llm_story': 'llm_story',
        'llm_joke': 'llm_joke',
        'llm_poetry': 'llm_poetry'
    }
)
router_builder.add_edge('llm_story', END)
router_builder.add_edge('llm_joke', END)
router_builder.add_edge('llm_poetry', END)

workflow = router_builder.compile()

result = workflow.invoke({
    'input': '给我写一个关于苍井空的笑话'
})

print(result['output'])


