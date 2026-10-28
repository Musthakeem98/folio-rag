import { ChatWindow } from "@/components/chat-window";

export default function ChatPage() {
  return (
    <main className="mx-auto flex h-screen max-w-4xl flex-col px-4 py-6">
      <h1 className="mb-4 text-2xl font-semibold">Ask</h1>
      <ChatWindow />
    </main>
  );
}
