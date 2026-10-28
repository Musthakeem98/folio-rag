"use client";

import { useState } from "react";
import { postChat } from "@/lib/api";

type Message = { role: "user" | "assistant"; content: string };

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    const query = input.trim();
    if (!query || busy) return;
    setMessages((m) => [...m, { role: "user", content: query }]);
    setInput("");
    setBusy(true);
    try {
      const text = await postChat(query);
      setMessages((m) => [...m, { role: "assistant", content: text }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex-1 overflow-y-auto rounded-xl border border-neutral-200 bg-white p-4">
        {messages.length === 0 && (
          <p className="text-sm text-neutral-500">Ask something about your indexed documents.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className="mb-3">
            <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">
              {m.role}
            </div>
            <div className="whitespace-pre-wrap text-sm">{m.content}</div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
          placeholder="Your question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={busy}
        />
        <button
          onClick={send}
          disabled={busy}
          className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
