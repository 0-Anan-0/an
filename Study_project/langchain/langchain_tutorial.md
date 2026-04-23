# LangChain 核心概念与示例教程

本文档基于 LangChain 的核心概念，通过实际示例代码，详细讲解 LangChain 的使用方法和工作原理。

## 一、LangChain 核心概念

LangChain 是一个用于开发由语言模型驱动的应用程序的框架，它提供了一系列工具和组件，使开发者能够快速构建复杂的 AI 应用。

### 1. 核心组件

| 组件 | 描述 | 作用 |
|------|------|------|
| Models | 统一的模型接口 | 支持多种 LLM 提供商，如 OpenAI、Anthropic、Cohere 等 |
| Prompts | 可复用的提示词模板 | 标准化提示词结构，提高模型输出质量 |
| Chains | 将多个组件串联成工作流 | 简化复杂流程的构建和管理 |
| Agents | 能自主决策、使用工具的智能体 | 使模型能够根据任务需求自主选择和使用工具 |
| Memory | 管理对话历史和状态 | 使模型能够保持上下文，实现连续对话 |
| Tools | 与外部系统交互的工具 | 扩展模型能力，如搜索、计算、文件操作等 |
| Retrieval | 与外部知识库交互的组件 | 实现 RAG (检索增强生成)，提高模型知识广度 |

### 2. 工作原理

LangChain 的核心设计理念是 **组件化** 和 **链式调用**，通过将复杂任务分解为独立的组件，再将这些组件串联成工作流，实现复杂 AI 应用的快速开发。

## 二、示例代码详解

### 1. 基础 LLM 调用

```python
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
```

**工作原理**：
1. **模型初始化**：创建一个 OpenAI 模型实例，设置模型名称和温度参数
2. **提示模板**：定义一个可复用的提示词模板，包含问题占位符
3. **输出解析**：创建一个输出解析器，将模型输出转换为字符串
4. **链式调用**：使用管道运算符 (`|`) 将组件串联成工作流
5. **执行**：调用 `invoke` 方法执行链，传入问题参数

### 2. RAG 系统实现

```python
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
prompt = ChatPromptTemplate.from_template(
    "请基于以下上下文回答问题：\n\n{context}\n\n问题：{input}"
)
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

# 执行RAG查询
result = retrieval_chain.invoke({"input": "LangChain的核心组件有哪些？"})
```

**工作原理**：
1. **文档加载**：从文件系统加载文档
2. **文档分割**：将长文档分割为短文本片段，便于向量存储和检索
3. **向量存储**：将文本片段转换为向量并存储，创建语义索引
4. **检索器**：创建一个检索器，用于根据查询语义搜索相关文档
5. **RAG链**：创建一个包含检索和生成的完整工作流
6. **执行**：调用 `invoke` 方法执行 RAG 链，传入查询参数

### 3. Agent 系统实现

```python
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
result = agent_executor.invoke({"input": "计算 123 * 456 的结果"})
```

**工作原理**：
1. **模型初始化**：创建一个 OpenAI 模型实例
2. **工具定义**：定义 Agent 可以使用的工具，如计算工具和 shell 工具
3. **提示模板**：创建一个包含工具使用说明的提示词模板
4. **Agent 创建**：创建一个能够调用工具的 Agent
5. **执行器**：创建一个 Agent 执行器，用于管理 Agent 的执行过程
6. **执行**：调用 `invoke` 方法执行 Agent，传入任务参数

### 4. 工具使用示例

```python
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

# 直接使用calculate工具
result = calculate.invoke({"a": 10, "b": 5, "operation": "add"})
print(f"10 + 5 = {result}")
```

**工作原理**：
1. **工具定义**：使用 `@tool` 装饰器定义一个工具函数，包含参数类型注解和文档字符串
2. **工具实现**：实现工具的核心逻辑，处理输入参数并返回结果
3. **工具调用**：直接调用工具的 `invoke` 方法执行工具，传入参数

## 三、高级特性

### 1. 链式调用语法 (LCEL)

LangChain 1.0 引入了 **LangChain Expression Language (LCEL)**，使用管道运算符 (`|`) 实现组件的链式调用，使代码更加简洁和可读。

```python
# 传统方式
chain = LLMChain(llm=llm, prompt=prompt)

# LCEL 方式
chain = prompt | llm | output_parser
```

### 2. 异步执行

LangChain 支持异步执行，提高并发处理能力：

```python
# 异步执行
result = await chain.ainvoke({"question": "什么是LangChain？"})

# 批量执行
results = await chain.abatch([{"question": "Q1"}, {"question": "Q2"}])
```

### 3. 流式输出

LangChain 支持流式输出，实现实时响应：

```python
# 流式执行
for chunk in chain.stream({"question": "什么是LangChain？"}):
    print(chunk, end="", flush=True)
```

## 四、实践建议

1. **从简单开始**：先构建基础的 LLM 调用，熟悉核心组件
2. **模块化设计**：将复杂任务分解为独立的组件，提高代码可维护性
3. **合理使用工具**：根据任务需求选择合适的工具，扩展模型能力
4. **优化提示词**：精心设计提示词模板，提高模型输出质量
5. **评估与迭代**：定期评估应用性能，根据反馈进行优化

## 五、常见问题

### 1. API 密钥配置

LangChain 使用环境变量存储 API 密钥，确保在使用前正确配置：

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### 2. 模型选择

根据任务需求选择合适的模型：
- 一般对话：`gpt-3.5-turbo`
- 复杂推理：`gpt-4`
- 代码生成：`gpt-4` 或 `code-davinci-002`

### 3. 性能优化

- **批量处理**：使用 `abatch` 方法批量处理请求
- **缓存**：使用 `InMemoryCache` 或 `SQLiteCache` 缓存结果
- **流式输出**：使用 `stream` 方法实现实时响应

## 六、总结

LangChain 是一个强大的框架，通过组件化和链式调用的设计理念，大大简化了 AI 应用的开发过程。本文通过四个核心示例，详细讲解了 LangChain 的使用方法和工作原理，希望能够帮助你快速上手 LangChain，构建复杂的 AI 应用。

## 七、扩展学习

1. **官方文档**：[https://docs.langchain.com/](https://docs.langchain.com/)
2. **示例代码**：[https://github.com/langchain-ai/langchain/tree/master/examples](https://github.com/langchain-ai/langchain/tree/master/examples)
3. **LangGraph**：[https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) - 用于构建复杂的多智能体系统
4. **LangSmith**：[https://www.langchain.com/langsmith](https://www.langchain.com/langsmith) - 用于监控和调试 LangChain 应用
