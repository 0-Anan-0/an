# https://mp.weixin.qq.com/s/UQni3SzhUiYPn-kOkSK9Mg
from langchain. chat_models import  init_chat_model
from openai import api_key, base_url
from dotenv import load_dotenv
import os
load_dotenv()


api_key1=os.getenv("SILICON_FLOW_API_KEY")
base_url1=os.getenv("SILICON_FLOW_BASE_URL")

model = init_chat_model(
    model='glm-4',
    model_provider='openai',
    base_url=base_url1,
    api_key=api_key1

)
#
q="介绍自己，你的数据最新时间是到多久"
result = model.invoke(q)
print(result)
