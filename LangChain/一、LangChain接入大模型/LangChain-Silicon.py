from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="Qwen/Qwen3-8B",
    model_provider="openai",
    base_url="https://api.siliconflow.cn/v1/",
    api_key="你注册的api_key",
)

question = "你好，请问你是?"

result = model.invoke(question)

print(result)
print(type(result))