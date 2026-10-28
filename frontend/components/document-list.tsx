"use client";

import { useEffect, useState } from "react";
import { listDocuments } from "@/lib/api";

type Doc = { id: string; source: string; title?: string };

export function DocumentList() {
  const [docs, setDocs] = useState<Doc[]>([]);

  useEffect(() => {
    listDocuments().then(setDocs).catch(() => setDocs([]));
  }, []);

  if (docs.length === 0) {
    return <p className="text-sm text-neutral-500">No documents indexed yet.</p>;
  }

  return (
    <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 bg-white">
      {docs.map((d) => (
        <li key={d.id} className="p-4 text-sm">
          <div className="font-medium">{d.title ?? d.source}</div>
          <div className="text-xs text-neutral-500">{d.id}</div>
        </li>
      ))}
    </ul>
  );
}
