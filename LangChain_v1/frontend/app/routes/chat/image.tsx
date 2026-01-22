import ChatPage from "../../../src/pages/ChatPage";

export function meta({}: any) {
  return [
    { title: "图片分析 - 多模态大模型RAG系统" },
  ];
}

export default function ImageChatPage() {
  return <ChatPage mode="image" />;
}
