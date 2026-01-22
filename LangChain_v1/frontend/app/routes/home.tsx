import type { Route } from "./+types/home";
import Home from "../../src/pages/Home";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "多模态大模型RAG系统" },
    { name: "description", content: "基于先进大模型技术，支持多种模态交互的智能问答系统" },
  ];
}

export default function HomePage() {
  return <Home />;
}
