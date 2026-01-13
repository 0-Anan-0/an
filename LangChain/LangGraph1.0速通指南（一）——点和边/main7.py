import uuid
import os
from typing import Literal, TypedDict
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langgraph.types import Command, interrupt
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)

# 1. 定义图状态State

class EmailClassification(TypedDict):
    # 分类包括问题、错误、账单、功能, 不属于这些功能就分类为复杂
    intent: Literal['question', 'bug', 'billing', 'feature', 'complex']
    # 紧急程度： 低、中、高、关键
    urgency: Literal['low', 'medium', 'high', 'critical']
    # 邮件主题
    topic: str
    # 邮件摘要
    summary: str

class EmailAgentState(TypedDict):
    # 储存读取邮件内容, 发件人邮件地址，邮件ID
    email_content: str
    sender_email: str
    email_id: str

    # 分类意图节点的结果，
    classification: EmailClassification

    # Bug tracking 错误处理系统只需要查询一些API， 这里就存储一个工单ID即可
    ticket_id: str | None

    # 搜索文档结果
    search_results: list[str] | None
    # 客户历史：客户历史是一个字典，键是客户的电子邮件，值是与该客户相关的任何搜索结果
    customer_history: dict | None

    # 生成内容:
    draft_response: str | None

def read_email(state: EmailAgentState) -> EmailAgentState:
    '''
    实际生产中这一步要从邮箱提供的api中提取电子邮件，这里仅仅是演示，
    会将电子邮件直接传给分类节点，该函数简写
    '''
    pass

def classify_intent(state: EmailAgentState) -> EmailAgentState:
    "用大模型进行节点分类和紧急程度识别，然后依据结果路由"

    structured_llm = llm.with_structured_output(EmailClassification)

    classification_pormpt = f"""
    分析用户输入的邮件并进行分类
    
    邮件: {state['email_content']}
    来自: {state['sender_email']}
    
    提供分类、紧急程度、主题和内容摘要
    """

    classication = structured_llm.invoke(classification_pormpt)

    return {
        'classification': classication
    }

def search_documentation(state: EmailAgentState) -> EmailAgentState:
    '''
    查询知识库节点，这里模拟操作
    '''
    classification = state.get('classification', {})

    query = f"{classification.get('intent', '')}  {classification.get('topic', '')}"

    try:
        # 模拟查询的逻辑
        search_results = [
            'search_result_1',
            'search_result_2',
            'search_result_3'
        ]
    except Exception as e:
        search_results = [f'搜索接口不可用']

    return {'search_results': search_results}

def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    '''
    模拟bug修复的相关内容
    '''
    ticket_id = f"Bug-{uuid.uuid4()} fixed"
    return {'ticket_id': ticket_id}

def write_response(state: EmailAgentState) -> Command[Literal['human_review', 'send_reply']]:
    '''
    根据分类结果、搜索结果等中间结果生产报告
    '''
    classification = state.get('classification', {})

    context_sections = []

    if state.get('search_results'):
        formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
        context_sections.append(f"相关内容:\n{formatted_docs}")
    if state.get('customer_history'):
        context_sections.append(f"Customer tier: {state['customer_history'].get('tier', 'standard')}")

    
    # 构建提示词
    draft_prompt = f"""
        撰写50字邮件回复:
        邮件内容: {state.get('email_content')}
        
        邮件分类: {classification.get('intent', 'unkown')}
        紧急程度: {classification.get('urgency', 'medium')}
        
        {chr(10).join(context_sections)}
    """

    response = llm.invoke(draft_prompt)

    # 根据紧急程度决定是否需要人类审核
    needs_review = (
        classification.get('urgency') in ['high', 'critical'] or
        classification.get('intent') == 'complex'
    )

    if needs_review:
        goto = 'human_review'
        print('需要人工审核')
    else:
        goto = 'send_reply'

    return Command(
        update={'draft_response': response.content},
        goto=goto
    )

def human_review(state: EmailAgentState) -> Command[Literal['send_reply', END]]:
    '''
    人类审查节点，审查结束后决定是否要回复该邮件
    '''
    classification = state.get('classification', {})

    human_decision = interrupt({
        "邮件ID": state['email_id'],
        "原始邮件内容": state['email_content'],
        "自动回复内容": state['draft_response'],
        '紧急程度': classification['urgency'],
        '分类': classification['intent'],
        '下一步': '请审核是否同意发送该邮件'
    })

    if human_decision=='approved':
        return Command(
            update={},
            goto='send_reply'
        )
    else:
        return Command(
            update={},
            goto=END
        )

def send_reply(state: EmailAgentState):
    print('---成功发送---')


builder = StateGraph(EmailAgentState)

builder.add_node("read_email", read_email)
builder.add_node("classify_intent", classify_intent)
builder.add_node("search_documentation",search_documentation)
builder.add_node("bug_tracking", bug_tracking)
builder.add_node("write_response", write_response)
builder.add_node("human_review",human_review)
builder.add_node("send_reply", send_reply)

builder.add_edge(START, "read_email")
builder.add_edge("read_email","classify_intent")
builder.add_edge("classify_intent","search_documentation")
builder.add_edge("classify_intent","bug_tracking")
builder.add_edge("search_documentation","write_response")
builder.add_edge("bug_tracking","write_response")
builder.add_edge("send_reply",END)

memory=InMemorySaver()
app = builder.compile(checkpointer=memory)

if __name__ == '__main__':

    # initial_state = {
    #     "email_content": "我遇到了一个紧急bug, 有客户重复订阅了一个产品",
    #     "sender_email": "test@163.com",
    #     "email_id": "email_123"
    # }


    initial_state = {
        "email_content": "你好呀，我是新同事苍井空",
        "sender_email": "test@163.com",
        "email_id": "email_123"
    }

    config = {"configurable": {"thread_id": "customer_123"}}
    result = app.invoke(initial_state, config=config)
    print(f'准备审核的回复内容:{result['draft_response']}...\n')
    if '__interrupt__' in result:
        print(f'Interrupt:{result}')
        msg = result['__interrupt__'][-1].value
        print(msg)
        human = input(f"请输入: ")
        human_response = Command(
            resume=human
        )
        final_result = app.invoke(human_response, config)












