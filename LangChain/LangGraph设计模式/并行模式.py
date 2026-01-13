from typing import TypedDict
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)

class State(TypedDict):
    topic: str
    joke: str
    story: str
    poetry: str
    combined_output: str

def generate_joke(state: State):
    '''
    生成笑话的节点
    '''
    topic = state['topic']
    msg = llm.invoke(f'写一个关于{topic}的笑话')
    return {
        'joke': msg.content
    }

def generate_story(state: State):
    '''
    生成故事的节点
    '''
    topic = state['topic']
    msg = llm.invoke(f'写一个关于{topic}的故事')
    return {
        'story': msg.content
    }

def generate_poetry(state: State):
    '''
    生成诗歌的节点
    '''
    topic = state['topic']
    msg = llm.invoke(f'写一个关于{topic}的诗歌')
    return {
        'poetry': msg.content
    }

def aggregator(state: State):
    '''
    聚合笑话、故事、诗歌的节点
    '''
    topic = state['topic']
    joke = state['joke']
    story = state['story']
    poetry = state['poetry']
    combined = f'这是一个关于 {topic} 的故事、笑话和诗歌的合集\n\n'
    combined += f'故事\n {story}\n\n'
    combined += f'笑话\n {joke}\n\n'
    combined += f'诗歌\n {poetry}\n\n'
    return {
        'combined_output': combined
    }

parallel_builder = StateGraph(State)

parallel_builder.add_node('generate_joke', generate_joke)
parallel_builder.add_node('generate_story', generate_story)
parallel_builder.add_node('generate_poetry', generate_poetry)
parallel_builder.add_node('aggregator', aggregator)

parallel_builder.add_edge(START, 'generate_joke')
parallel_builder.add_edge(START, 'generate_story')
parallel_builder.add_edge(START, 'generate_poetry')
parallel_builder.add_edge('generate_joke', 'aggregator')
parallel_builder.add_edge('generate_story', 'aggregator')
parallel_builder.add_edge('generate_poetry', 'aggregator')
parallel_builder.add_edge('aggregator', END)

workflow = parallel_builder.compile()

state = workflow.invoke({
    'topic': 'pgone 与 李小璐'
})
print(state['combined_output'])



