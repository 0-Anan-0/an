import ChatPage from "../../../src/pages/ChatPage";

export function meta({}: any) {
  return [
    { title: "智能问答 - 多模态大模型RAG系统" },
  ];
}

export default function TextChatPage() {
  return <ChatPage mode="text" />;
}
