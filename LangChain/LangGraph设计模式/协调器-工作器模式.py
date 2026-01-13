import operator
from typing import Annotated, List, TypedDict

from langchain.messages import SystemMessage, HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
)


# 1. 定义结构化的输出格式，用于规划报告的章节
class Section(BaseModel):
    name: str = Field(
        description='报告章节的名称'
    )
    description: str = Field(
        description='本章节中涵盖的主要主题和概念的简要概述'
    )


class Sections(BaseModel):
    sections: List[Section] = Field(
        description='报告的章节'
    )


planner = llm.with_structured_output(Sections)


# 2. 定义协调器的状态
class State(TypedDict):
    topic: str
    sections: List[Section]
    completed_sections: Annotated[list, operator.add]
    final_report: str


# 3. 定义工作者状态
class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]

# 4. 定义图中的节点:
def orchestrator(state: State):
    '''
    协调器节点，使用结构化输出生成报告计划
    '''
    topic = state['topic']
    # 首先使用planner生成结构化输出报告
    report_sections = planner.invoke(
        [
            SystemMessage(content='请根据用户输入的主题生成报告计划。'),
            HumanMessage(content=f'这是报告主题:{topic}')
        ]
    )
    return {
        'sections': report_sections.sections
    }

def llm_call(state: WorkerState):
    '''
    工作者节点：根据分配的章节详细信息描述生成报告的章节内容
    '''
    section_name = state['section'].name
    section = llm.invoke(
        [
            SystemMessage(content='根据提供的章节的名称和描述编写报告章节，每个章节中不包含序言，使用markdown格式。200字以内'),
            HumanMessage(content=f'这是章节的名称: {section_name}')
        ]
    )
    return {
        'completed_sections': [section.content]
    }

def synthesizer(state: State):
    '''
    将各个章节的输出合称为完整的报告
    '''
    completed_sections = state['completed_sections']
    completed_report_sections = "\n\n".join(completed_sections)
    return {
        'final_report': completed_report_sections
    }

# 5. 定义条件边函数，将工作者动态分配对应的计划章节
def assign_workers(state: State):
    '''
    使用send API 将工作者分配给计划中的每个章节，以实现动态工作者创建
    '''
    return [Send('llm_call', {'section': s}) for s in state['sections']]

orchestrator_worker_builder = StateGraph(State)

orchestrator_worker_builder.add_node('orchestrator', orchestrator)
orchestrator_worker_builder.add_node('llm_call', llm_call)
orchestrator_worker_builder.add_node('synthesizer', synthesizer)

orchestrator_worker_builder.add_edge(START, 'orchestrator')
orchestrator_worker_builder.add_conditional_edges(
    'orchestrator',
    assign_workers,
    ['llm_call']
)
orchestrator_worker_builder.add_edge('llm_call', 'synthesizer')
orchestrator_worker_builder.add_edge('synthesizer', END)

orchestrator_worker = orchestrator_worker_builder.compile()

# 使用示例报告主题调用协调器-工作者工作流
result = orchestrator_worker.invoke({
    'topic': '创建关于LLM缩放定律的报告'
})

print(result['final_report'])
