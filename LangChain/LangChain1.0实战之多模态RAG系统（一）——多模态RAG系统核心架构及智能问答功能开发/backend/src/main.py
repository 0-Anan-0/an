import json
import uvicorn

from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import HTTPException, FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import BaseMessage


app = FastAPI(
    title="多模态 RAG 工作台 API",
    description="基于 LangChain 1.0 的智能对话 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContentBlock(BaseModel):
    type: str = Field(description="内容类型: text, image, audio")
    content: str = Field(description="内容数据")


class MessageRequest(BaseModel):
    content_blocks: List[ContentBlock] = Field(default=[], description="内容块")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")


class MessageResponse(BaseModel):
    content: str
    timestamp: str
    role: str


def get_chat_model():
    try:
        # model = init_chat_model(
        #     model="Qwen/Qwen3-Omni-30B-A3B-Instruct",  # 模型名称
        #     model_provider="openai",  # 模型提供商，硅基流动提供了openai请求格式的访问
        #     base_url="https://api.siliconflow.cn/v1/",  # 硅基流动模型的请求url
        #     api_key="",  # 填写你注册的硅基流动 API Key
        # )
        model = init_chat_model(
        model="Qwen/Qwen3-Omni-30B-A3B-Instruct",
        # model = "deepseek-ai/DeepSeek-R1",
        base_url="https://api.siliconflow.cn/v1/",
        model_provider='openai',
        api_key="sk-vbjmyxntwveksmhflvcoxnhvfgkzxakbfzsgjuyhaddynbkk"
        )
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")


def convert_history_to_messages(history: List[Dict[str, Any]]) -> List[BaseMessage]:
    """将历史记录转换为 LangChain 消息格式，支持多模态内容"""
    messages = []

    # 添加系统消息
    system_prompt = """
    你是一个专业的多模态 RAG 助手，具备与用户对话的能力， 请以专业、准确、友好的方式回答用户所提问题。
    """

    messages.append(SystemMessage(content=system_prompt))

    # 转换历史消息
    for i, msg in enumerate(history):
        content = msg.get("content", "")
        content_blocks = msg.get("content_blocks", [])
        message_content = []
        if msg["role"] == "user":
            for block in content_blocks:
                if block.get("type") == "text":
                    message_content.append({
                        "type": "text",
                        "text": block.get("content", "")
                    })
            messages.append(HumanMessage(content=message_content))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=content))

    return messages


def create_multimodal_message(request: MessageRequest) -> HumanMessage:
    """创建多模态消息"""
    message_content = []

    # 处理内容块
    for i, block in enumerate(request.content_blocks):
        if block.type == "text":
            message_content.append({
                "type": "text",
                "text": block.content
            })

    return HumanMessage(content=message_content[0]["text"])


async def generate_streaming_response(
        messages: List[BaseMessage]
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        model = get_chat_model()
        # 创建流式响应
        full_response = ""

        chunk_count = 0
        async for chunk in model.astream(messages):
            chunk_count += 1
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content

                # 直接发送每个chunk的内容，避免重复
                data = {
                    "type": "content_delta",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        # 发送完成信号
        final_data = {
            "type": "message_complete",
            "full_content": full_response,
            "timestamp": datetime.now().isoformat(),
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: MessageRequest):
    """流式聊天接口（支持多模态）"""
    try:
        # 转换消息历史
        messages = convert_history_to_messages(request.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)

        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_sync(request: MessageRequest):
    """同步聊天接口（支持多模态）"""
    try:
        # 转换消息历史
        messages = convert_history_to_messages(request.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)

        # 获取模型响应
        model = get_chat_model()
        response = await model.ainvoke(messages)

        return MessageResponse(
            content=response.content,
            role="assistant",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000
    )
