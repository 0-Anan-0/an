import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("chat/text", "routes/chat/text.tsx"),
  route("chat/image", "routes/chat/image.tsx"),
  route("chat/audio", "routes/chat/audio.tsx"),
  route("chat/pdf", "routes/chat/pdf.tsx"),
] satisfies RouteConfig;
