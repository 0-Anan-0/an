import json
import uvicorn

from typing import List, Dict, Any, AsyncGenerator, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import HTTPException, FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import BaseMessage

from utils import ImageProcessor, AudioProcessor

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
    content: Optional[str] = Field(description="内容数据")


class MessageRequest(BaseModel):
    content_blocks: List[ContentBlock] = Field(default=[], description="内容块")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")

class MessageResponse(BaseModel):
    content: str
    timestamp: str
    role: str

def get_chat_model():
    try:
        model = init_chat_model(
            model="Qwen/Qwen3-Omni-30B-A3B-Instruct",  # 模型名称
            model_provider="openai",  # 模型提供商，硅基流动提供了openai请求格式的访问
            base_url="https://api.siliconflow.cn/v1/",  # 硅基流动模型的请求url
            api_key="",  # 填写你注册的硅基流动 API Key
        )
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")


def convert_history_to_messages(history: List[Dict[str, Any]]) -> List[BaseMessage]:
    """将历史记录转换为 LangChain 消息格式，支持多模态内容"""
    messages = []

    # 添加系统消息
    system_prompt = """
        你是一个专业的多模态 RAG 助手，具备如下能：
        1. 与用户对话的能力。
        2. 图像内容识别和分析能力(OCR, 对象检测， 场景理解)
        3. 音频转写与分析
        
        重要指导原则：
        - 当用户上传图片并提出问题时，请结合图片内容和用户的具体问题来回答
        - 仔细分析图片中的文字、图表、对象、场景等所有可见信息
        - 根据用户的问题重点，有针对性地分析图片相关部分
        - 如果图片包含文字，请准确识别并在回答中引用
        - 如果用户只上传图片没有问题，则提供图片的全面分析
        
        请以专业、准确、友好的方式回答
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
                elif block.get("type") == "image":
                    image_data = block.get("content", "")
                    if image_data.startswith("data:image"):
                        message_content.append({
                            "type": "image_url",
                            "image_url" : {
                                "url": image_data
                            }
                        })
                elif block.get("type") == "audio":
                    audio_data = block.get("content", "")
                    if audio_data.startswith("data:audio"):
                        message_content.append({
                            "type": "audio_url",
                            "image_url": {
                                "url": audio_data
                            }
                        })
            messages.append(HumanMessage(content=message_content))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=content))

    return messages


def create_multimodal_message(request: MessageRequest, image_file: UploadFile | None, audio_file:UploadFile | None) -> HumanMessage:
    """创建多模态消息"""
    message_content = []

    # 如果有图片
    if image_file:
        processor = ImageProcessor()
        mime_type = processor.get_image_mime_type(image_file.filename)
        base64_image = processor.image_to_base64(image_file)
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}"
            },
        })
    if audio_file:
        processor = AudioProcessor()
        mime_type = processor.get_audio_mime_type(audio_file.filename)
        base64_audio = processor.audio_to_base64(audio_file)
        message_content.append({
            "type": "audio_url",
            "audio_url": {
                "url": f"data:{mime_type};base64,{base64_audio}"
            },
        })
    # 处理内容块
    for i, block in enumerate(request.content_blocks):
        if block.type == "text":
            message_content.append({
                "type": "text",
                "text": block.content
            })
        elif block.type == "image":
            # 只有base64格式的消息才会被接入
            if block.content.startswith("data:image"):
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": block.content
                    },
                })
        elif block.type == "audio":
            if block.content.startswith("data:audio"):
                message_content.append({
                    "type": "audio_url",
                    "audio_url": {
                        "url": block.content
                    },
                })

    return HumanMessage(content=message_content)


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
async def chat_stream(
        image_file: UploadFile | None = File(None),
        content_blocks: str = Form(default="[]"),
        history: str = Form(default="[]"),
        audio_file: UploadFile | None = File(None)
):
    """流式聊天接口（支持多模态）"""
    try:
        # 解析 JSON 字符串
        try:
            content_blocks_data = json.loads(content_blocks)
            history_data = json.loads(history)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"JSON 解析错误: {str(e)}")

        # 创建请求对象（用于传递给其他函数）
        request_data = MessageRequest(content_blocks=content_blocks_data, history=history_data)

        # 转换消息历史
        messages = convert_history_to_messages(request_data.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request_data, image_file=image_file, audio_file=audio_file)
        messages.append(current_message)

        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages),
            media_type="text/event-stream",
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
