from dataclasses import dataclass
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model

@dataclass
class Context:
    user_level: str = "expert"

deepseek_model = init_chat_model(
    model="deepseek-reasoner",
    base_url="https://api.deepseek.com",
    api_key=""
)

Qwen3_model = init_chat_model(
    model="Qwen/Qwen3-8B",
    model_provider="openai",
    base_url="https://api.siliconflow.cn/v1/",
    api_key="",
)


class ExpertiseBasedToolMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        user_level = request.runtime.context.user_level

        if user_level == "expert":
            model = deepseek_model
            tools = []
        else:
            # Less powerful model
            model = Qwen3_model
            tools = []

        request.model = model
        request.tools = tools
        return handler(request)

agent = create_agent(
    model=Qwen3_model,
    tools=[],
    middleware=[ExpertiseBasedToolMiddleware()],
    context_schema=Context,
)

question = "你好请问你是?"

for step in agent.stream(
    {"messages": {'role':'user', 'content':question}},
    context=Context(user_level='student'),
    stream_mode="values",
):
    step['messages'][-1].pretty_print()



