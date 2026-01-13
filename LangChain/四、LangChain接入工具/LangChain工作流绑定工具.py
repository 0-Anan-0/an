import pandas as pd

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool # 从LangChain依赖库引入Python代码解释器
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser

df = pd.read_csv('global_cities_data.csv')
tool = PythonAstREPLTool(locals={"df": df}) # 传递给代码解释器的局部变量，这里是读取表格内容的pandas对象

# 使用 硅基流动 模型
model = init_chat_model(
    model="Qwen/Qwen3-8B",
    model_provider="openai",
    base_url="https://api.siliconflow.cn/v1/",
    api_key="",
)

# 添加提示词模板
system = f"""
你可以访问一个名为 `df` 的 pandas 数据框，你可以使用df.head().to_markdown() 查看数据集的基本信息， \
请根据用户提出的问题，编写 Python 代码来回答。只返回代码，不返回其他内容。只允许使用 pandas 和内置库。
"""

prompt = ChatPromptTemplate([
    ("system", system),
    ("user", "{question}")
])


parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)

llm_with_tools = model.bind_tools([tool]) # 将工具与大模型绑定

llm_chain = prompt | llm_with_tools | parser | tool

response = llm_chain.invoke(
    "我有一张表，名为'df'，请帮我计算GDP_Billion_USD的最大值是多少，并输出对应的国家。"
)

print(response)



