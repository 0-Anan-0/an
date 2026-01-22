import ChatPage from "../../../src/pages/ChatPage";

export function meta({}: any) {
  return [
    { title: "PDF解析 - 多模态大模型RAG系统" },
  ];
}

export default function PdfChatPage() {
  return <ChatPage mode="pdf" />;
}
