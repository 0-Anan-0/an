from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

model = init_chat_model(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=""
)

agent = create_agent(
    model=model,
    checkpointer=InMemorySaver()
)

result = agent.invoke(
    {
        "messages": "你好我叫苍进空?"
    },
    {
        "configurable": {
            "thread_id": "1"
        }
    }
)

for msg in result['messages']:
    msg.pretty_print()

result = agent.invoke(
    {
        "messages": "你好我叫什么名字?"
    },
{
        "configurable": {
            "thread_id": "1"
        }
    }
)

for msg in result['messages']:
    msg.pretty_print()
