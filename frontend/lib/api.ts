const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function postChat(query: string): Promise<string> {
  const r = await fetch(`${API}/api/v1/chat/completions`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query, stream: false }),
  });
  if (!r.ok) throw new Error(`Chat failed: ${r.status}`);
  return await r.text();
}

export async function listDocuments(): Promise<Array<{ id: string; source: string; title?: string }>> {
  const r = await fetch(`${API}/api/v1/documents`);
  if (!r.ok) return [];
  return r.json();
}
