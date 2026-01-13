import pandas as pd
from langchain_experimental.tools import PythonAstREPLTool # 从LangChain依赖库引入Python代码解释器

df = pd.read_csv('global_cities_data.csv')
tool = PythonAstREPLTool(locals={"df": df}) # 传递给代码解释器的局部变量，这里是读取表格内容的pandas对象
res = tool.invoke("df['GDP_Billion_USD'].mean()") # 计算变量GDP的均值

print(res)
