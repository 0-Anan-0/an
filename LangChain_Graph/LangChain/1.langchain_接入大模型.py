# # https://mp.weixin.qq.com/s/UQni3SzhUiYPn-kOkSK9Mg
# from langchain. chat_models import  init_chat_model
# from openai import api_key, base_url
# from dotenv import load_dotenv
# import os
# load_dotenv()
#
#
# api_key1=os.getenv("SILICON_FLOW_API_KEY")
# base_url1=os.getenv("SILICON_FLOW_BASE_URL")
#
# model = init_chat_model(
#     model='qwen',
#     model_provider='openai',
#     base_url=base_url1,
#     api_key=api_key1
#
# )
# #
# q="介绍自己，你的数据最新时间是到多久"
# result = model.invoke(q)
# print(result)
from venv import create

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_classic.chains.question_answering.map_reduce_prompt import messages
from langchain_classic.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from openai import api_key

online_image_url ="https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"

message =HumanMessage(
    content=[
        {"type":"text",
         "text":"请分析这张在线图片"
         },
        {
            'type':'image',
            'image_url':{'url':online_image_url}
        }
    ]
)
def weather_tool():
    pass

def Weather(city:str):
    values:"city"
    out_put:"666"

model = init_chat_model(
    model='Qwen/Qwen3-8B',
    model_provider='openai',
    base_url='https://api.siliconflow.cn/v1/',
    api_key='sk-vbjmyxntwveksmhflvcoxnhvfgkzxakbfzsgjuyhaddynbkk'
)

# agent = create_agent(
#     "gpt-4o-mini",
#     tools=[weather_tool],
#     response_format=ToolStrategy(Weather)
# )

response =model.invoke([message])
print('模型回复',response.content)