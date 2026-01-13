import os
from dotenv import load_dotenv # 加载环境变量的依赖
from pydantic import BaseModel
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch


load_dotenv(override=True)
Deepseek_API_KEY = os.getenv("DEEPSEEK_API_KEY")

model = ChatDeepSeek(
    model_name='deepseek-chat',
    api_key=Deepseek_API_KEY
)

# 一、构建规划智能体

PLANNER_INSTRUCTIONS = (
    "You are a helpful research assistant, Given a query, come up with a set of web searches "
    "to perform to best answer the query, Output between 5 and 7 terms to query for."
)

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", PLANNER_INSTRUCTIONS),
    ("human",  "{query}")
])

class WebSearchItem(BaseModel):
    query: str
    "The search term to use for the web search."
    "用于网络搜索的关键词"

    reason: str
    "You reasoning for why this search is important to the query."
    "为什么这个搜索对于解答该问题很重要的理由"

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    "A list of web searches to perform to best answer the query"
    "为了尽可能全面回答该问题而需要执行的网页搜索列表"

planner_chain = planner_prompt | model.with_structured_output(WebSearchPlan)

planner_result = planner_chain.invoke({'query': '请问你对AI+教育有何看法'})

# print(planner_result)

# 二、构建搜索智能体

SEARCH_INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300"
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good"
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)

search_tool = TavilySearch(max_results=5, topic="general")

search_agent = create_react_agent(
    model,
    prompt=SEARCH_INSTRUCTIONS,
    tools=[search_tool]
)

search_agent_res = search_agent.invoke({'messages': [{'role': 'user', "content": planner_result.searches[0].query}]})

# print(search_agent_res['messages'][-1].content)

# 三、构建编写智能体
WRITER_PROMPT = (
    "You are a senior researcher tasked with writing a cohesive report for a research query."
    "You will be provided with the original query, and some initial research done by a research assistant. \n"
    "You should first come up with an outline for the report that describes the structure and flow of the report. Then, "
    "generate the report and return that as your final output. \n The final output should be in markdown format, and it should"
    "be lengthy and detailed. Aim for 10-20 pages of content, at least 1500 words. 最终生成的报告采用中文输出."
)

class ReportData(BaseModel):
    short_summary: str
    '''
    A short 2-3 sentence summary of this findings
    一份2-3句话的简短研究结论摘要
    '''

    markdown_report: str
    '''
    The final report
    最终生成的报告(markdown格式)
    '''

    follow_up_questions: list[str]
    '''
    Suggested topics to research further
    建议进一步研究的相关主题
    '''

writer_prompt = ChatPromptTemplate.from_messages([
    ('system', WRITER_PROMPT),
    ('human', '{query}')
])

writer_chain = writer_prompt | model.with_structured_output(ReportData)

# 四、自定义逻辑串联/LangGraph图结构串联

def plan_searches(query: str) -> WebSearchPlan:
    result = planner_chain.invoke({'query': query})
    return result

def search(item:WebSearchItem) -> str | None:
    try:
        final_query = f"Search Item: {item.query}\nReason for searching: {item.reason}"
        result = search_agent.invoke({"messages":[
            {
                "role": "user",
                "content": final_query
            }
        ]})
        return str(result['messages'][-1].content)
    except Exception:
        return None


def perform_searches(search_plan: WebSearchPlan):
    results = []
    for item in search_plan.searches:
        result = search(item)
        if result is not None:
            results.append(result)
    return results

def write_report(query: str, search_results) -> ReportData:
    summary=''
    for search_result in search_results:
        summary += search_result
    final_query = f'Original query: {query}\n Summarized search results: {summary}'
    result = writer_chain.invoke({
        'query': final_query
    })
    return result

def deepresearch(query: str) -> ReportData:
    '''
    输入一个研究主题，自动完成搜索规划、搜索和写报告
    返回最终的ReportData对象，就是一个markdown的格式完整的研究报告文档
    '''
    search_plan = plan_searches(query)
    search_results = perform_searches(search_plan)
    report = write_report(query, search_results)
    print(report.markdown_report)

deepresearch('AI在教育方面的应用场景')