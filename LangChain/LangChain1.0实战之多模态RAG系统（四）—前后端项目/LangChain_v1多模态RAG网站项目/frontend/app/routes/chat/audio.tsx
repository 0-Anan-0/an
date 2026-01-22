import ChatPage from "../../../src/pages/ChatPage";

export function meta({}: any) {
  return [
    { title: "音频转写 - 多模态大模型RAG系统" },
  ];
}

export default function AudioChatPage() {
  return <ChatPage mode="audio" />;
}
