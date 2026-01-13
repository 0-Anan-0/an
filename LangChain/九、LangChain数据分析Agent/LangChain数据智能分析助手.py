import streamlit as st # 构建前端页面
import pandas as pd # 读取csv文件
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool # LagnChain内置工具，支持解析并执行Python代码

import matplotlib
import os

matplotlib.use('Agg') # 设置图片绘制后端，该模式支持生成图片但不支持前端交互显示


# 初始化LLM
@st.cache_resource
def init_llm():
    return init_chat_model(
        "deepseek-chat", \
        model_provider="deepseek",
        api_key=''
    )

# 初始化会话状态
def init_session_state():
    if 'csv_messages' not in st.session_state:
        st.session_state.csv_messages = []
    if 'df' not in st.session_state:
        st.session_state.df = None

# CSV处理函数
def get_csv_response(query: str) -> str:
    if st.session_state.df is None:
        return "请先上传CSV文件"

    llm = init_llm()
    locals_dict = {'df': st.session_state.df}
    tools = [PythonAstREPLTool(locals=locals_dict)]

    system = f"""给定一个pandas变量df, 回答用户的查询，以下是`df.head().to_markdown()`的输出供您参考，您可以访问完整的df数据框:
    ```
    {st.session_state.df.head().to_markdown()}
    ```
    一旦获得足够数据立即给出最终答案，否则使用df生成代码并调用所需工具。
    如果用户要求制作图表，请将其保存为plot.png，并输出 GRAPH:<图表标题>。
    示例：
    ```
    plt.hist(df['Age'])
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.title('Age Histogram')
    plt.savefig('plot.png')
    ``` 
    输出: GRAPH:Age histogram
    问题:"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor.invoke({"input": query})['output']

def main():
    init_session_state()
    # 主标题
    st.markdown('<h1 class="main-header">🤖 LangChain 数据分析系统</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center; margin-bottom: 2rem; color: #666;">自动分析csv智能体系统</div>',
        unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📈 数据分析对话")

        # 显示数据状态
        if st.session_state.df is not None:
            st.markdown(
                '<div class="info-card success-card"><span class="status-indicator status-ready">✅ 数据已加载完成</span></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="info-card warning-card"><span class="status-indicator status-waiting">⚠️ 请先上传CSV文件</span></div>',
                unsafe_allow_html=True)

        # 聊天界面
        for message in st.session_state.csv_messages:
            with st.chat_message(message["role"]):
                if message["type"] == "dataframe":
                    st.dataframe(message["content"])
                elif message["type"] == "image":
                    st.write(message["content"])
                    if os.path.exists('plot.png'):
                        st.image('plot.png')
                else:
                    st.markdown(message["content"])

        # 用户输入
        if csv_query := st.chat_input("📊 分析数据...", disabled=st.session_state.df is None):
            st.session_state.csv_messages.append({"role": "user", "content": csv_query, "type": "text"})
            with st.chat_message("user"):
                st.markdown(csv_query)

            with st.chat_message("assistant"):
                with st.spinner("🔄 正在分析数据..."):
                    response = get_csv_response(csv_query)

                if isinstance(response, pd.DataFrame):
                    st.dataframe(response)
                    st.session_state.csv_messages.append(
                        {"role": "assistant", "content": response, "type": "dataframe"})
                elif "GRAPH" in str(response):
                    text = str(response)[str(response).find("GRAPH") + 6:]
                    st.write(text)
                    if os.path.exists('plot.png'):
                        st.image('plot.png')
                    st.session_state.csv_messages.append({"role": "assistant", "content": text, "type": "image"})
                else:
                    st.markdown(response)
                    st.session_state.csv_messages.append({"role": "assistant", "content": response, "type": "text"})

    with col2:
        st.markdown("### 📊 数据管理")

        # CSV文件上传
        csv_file = st.file_uploader("📈 上传CSV文件", type='csv')
        if csv_file:
            st.session_state.df = pd.read_csv(csv_file)
            st.success(f"✅ 数据加载成功!")

            # 显示数据预览
            with st.expander("👀 数据预览", expanded=True):
                st.dataframe(st.session_state.df.head())
                st.write(f"📏 数据维度: {st.session_state.df.shape[0]} 行 × {st.session_state.df.shape[1]} 列")

        # 数据信息
        if st.session_state.df is not None:
            if st.button("📋 显示数据信息", use_container_width=True):
                with st.expander("📊 数据统计信息", expanded=True):
                    st.write("**基本信息:**")
                    st.text(f"行数: {st.session_state.df.shape[0]}")
                    st.text(f"列数: {st.session_state.df.shape[1]}")
                    st.write("**列名:**")
                    st.write(list(st.session_state.df.columns))
                    st.write("**数据类型:**")
                    # 修复：将dtypes转换为字符串格式显示
                    dtype_info = pd.DataFrame({
                        '列名': st.session_state.df.columns,
                        '数据类型': [str(dtype) for dtype in st.session_state.df.dtypes]
                    })
                    st.dataframe(dtype_info, use_container_width=True)

        # 清除数据
        if st.button("🗑️ 清除CSV数据", use_container_width=True):
            st.session_state.df = None
            st.session_state.csv_messages = []
            if os.path.exists('plot.png'):
                os.remove('plot.png')
            st.success("数据已清除")
            st.rerun()

if __name__ == '__main__':
    main()