#!/usr/bin/env python3
"""
LangChain核心功能示例

本文件包含LangChain的典型使用场景，包括：
1. 基础LLM调用
2. RAG系统实现
3. Agent系统实现
4. 工具使用示例
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_community.tools import ShellTool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 设置API密钥（实际使用时请替换为真实密钥）
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"  # 或其他兼容的API端点


def example_basic_llm():
    """
    示例1：基础LLM调用
    """
    print("=" * 60)
    print("示例1：基础LLM调用")
    print("=" * 60)
    
    # 初始化模型
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_template(
        "你是一个专业的AI助手。请回答以下问题：{question}"
    )
    
    # 创建输出解析器
    output_parser = StrOutputParser()
    
    # 创建链
    chain = prompt | llm | output_parser
    
    # 执行链
    result = chain.invoke({"question": "什么是LangChain？它的主要功能是什么？"})
    print(result)
    print()


def example_rag():
    """
    示例2：RAG系统实现
    """
    print("=" * 60)
    print("示例2：RAG系统实现")
    print("=" * 60)
    
    # 创建示例文档
    with open("example_document.txt", "w", encoding="utf-8") as f:
        f.write("LangChain是一个用于开发由语言模型驱动的应用程序的框架。\n")
        f.write("它提供了一系列工具和组件，使开发者能够快速构建复杂的AI应用。\n")
        f.write("LangChain的核心组件包括：\n")
        f.write("1. Models：统一的模型接口，支持多种LLM提供商\n")
        f.write("2. Prompts：可复用的提示词模板\n")
        f.write("3. Chains：将多个组件串联成工作流\n")
        f.write("4. Agents：能自主决策、使用工具的智能体\n")
        f.write("5. Memory：管理对话历史和状态\n")
        f.write("6. Tools：与外部系统交互的工具\n")
        f.write("7. Retrieval：与外部知识库交互的组件\n")
    
    # 加载文档
    loader = TextLoader("example_document.txt", encoding="utf-8")
    documents = loader.load()
    
    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # 创建向量存储
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever()
    
    # 创建RAG链
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # 创建文档链
    prompt = ChatPromptTemplate.from_template(
        "请基于以下上下文回答问题：\n\n{context}\n\n问题：{input}"
    )
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    
    # 创建检索链
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
    # 执行RAG查询
    result = retrieval_chain.invoke({"input": "LangChain的核心组件有哪些？"})
    print(result["answer"])
    print()


@tool

def calculate(a: float, b: float, operation: str) -> float:
    """
    执行数学计算
    
    Args:
        a: 第一个数字
        b: 第二个数字
        operation: 操作类型，支持 add, subtract, multiply, divide
    
    Returns:
        计算结果
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    else:
        raise ValueError(f"不支持的操作：{operation}")


def example_agent():
    """
    示例3：Agent系统实现
    """
    print("=" * 60)
    print("示例3：Agent系统实现")
    print("=" * 60)
    
    # 初始化模型
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # 定义工具
    tools = [calculate, ShellTool()]
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_template(
        "你是一个智能助手，能够使用工具来回答问题。\n\n"
        "请根据用户的问题，决定是否需要使用工具，以及使用哪些工具。\n\n"
        "问题：{input}\n"
        "对话历史：{chat_history}\n"
        "可用工具：{tools}\n"
        "工具描述：{tool_names}\n"
        "请以JSON格式输出你的思考和决策：\n"
        "{{\n"
        '  "thought": "你的思考过程",\n'
        '  "action": "工具名称",\n'
        '  "action_input": {{工具输入参数}}\n'
        "}}"
    )
    
    # 创建Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 创建Agent执行器
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # 执行Agent
    try:
        result = agent_executor.invoke({"input": "计算 123 * 456 的结果"})
        print("Agent执行结果：", result["output"])
    except Exception as e:
        print(f"执行过程中出现错误：{e}")
    print()


def example_tools():
    """
    示例4：工具使用示例
    """
    print("=" * 60)
    print("示例4：工具使用示例")
    print("=" * 60)
    
    # 直接使用calculate工具
    result = calculate.invoke({"a": 10, "b": 5, "operation": "add"})
    print(f"10 + 5 = {result}")
    
    result = calculate.invoke({"a": 10, "b": 5, "operation": "multiply"})
    print(f"10 * 5 = {result}")
    print()


if __name__ == "__main__":
    print("LangChain核心功能示例")
    print("=" * 60)
    print()
    
    # 执行各示例
    try:
        example_basic_llm()
    except Exception as e:
        print(f"示例1执行失败：{e}")
    
    try:
        example_rag()
    except Exception as e:
        print(f"示例2执行失败：{e}")
    
    try:
        example_agent()
    except Exception as e:
        print(f"示例3执行失败：{e}")
    
    try:
        example_tools()
    except Exception as e:
        print(f"示例4执行失败：{e}")
    
    # 清理临时文件
    if os.path.exists("example_document.txt"):
        os.remove("example_document.txt")
    
    print("所有示例执行完成！")
