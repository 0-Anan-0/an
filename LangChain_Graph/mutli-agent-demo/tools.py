from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from pydantic import BaseModel, Field

search_tool = TavilySearchResults(
    max_results=3,
    description="Search the web for current information and facts."
)


class CalculatorInput(BaseModel):
    expression: str = Field(description="数学表达式，如：123*456, (1+2)*(3-4)/5 等")


@tool(args_schema=CalculatorInput)
def calculator(expression: str):
    """
    执行数学计算，支持基本算术运算（加、减、乘、除、括号等）
    """
    import ast
    import operator

    # 安全的表达式计算
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    class SafeEvaluator(ast.NodeVisitor):
        def visit_BinOp(self, node):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if type(node.op) in allowed_operators:
                return allowed_operators[type(node.op)](left, right)
            raise ValueError(f"不支持的运算符: {type(node.op).__name__}")

        def visit_Num(self, node):
            return node.n

        def visit_Expr(self, node):
            return self.visit(node.value)

        def generic_visit(self, node):
            raise ValueError(f"不支持的表达式: {type(node).__name__}")

    try:
        tree = ast.parse(expression, mode='eval')
        evaluator = SafeEvaluator()
        result = evaluator.visit(tree)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_datetime():
    """
    获取当前日期和时间
    """
    from datetime import datetime
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


class ReadFileInput(BaseModel):
    file_path: str = Field(description="文件路径，如：data.txt, docs/report.md 等")


@tool(args_schema=ReadFileInput)
def read_file(file_path: str):
    """
    读取本地文件内容
    """
    import time
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"文件内容: {content[:1000]}{'...' if len(content) > 1000 else ''}"
        except Exception as e:
            if attempt == max_retries - 1:
                return f"读取文件错误: {str(e)}"
            print(f"读取文件失败，{retry_delay}秒后重试...")
            time.sleep(retry_delay)
            retry_delay *= 2


class SummarizeInput(BaseModel):
    text: str = Field(description="需要总结的文本")
    max_length: int = Field(description="总结的最大长度", default=200)


@tool(args_schema=SummarizeInput)
def summarize(text: str, max_length: int = 200):
    """
    总结长文本
    """
    # 简单的文本总结逻辑
    sentences = text.split('. ')
    if len(sentences) <= 3:
        return text

    # 取前几个句子作为总结
    summary = '. '.join(sentences[:3]) + '.'
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'

    return f"总结: {summary}"


def get_all_tools():
    return [search_tool, calculator, get_datetime, read_file, summarize]


def get_math_tools():
    return [calculator]


def get_research_tools():
    return [search_tool, get_datetime, read_file, summarize]