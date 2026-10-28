import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-4xl font-semibold tracking-tight">Lumen</h1>
      <p className="mt-3 text-neutral-600">Local-first, open-source RAG for PDFs and the web.</p>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <Link
          href="/chat"
          className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:shadow-md"
        >
          <div className="font-medium">Ask</div>
          <div className="mt-1 text-sm text-neutral-500">Chat with your indexed documents.</div>
        </Link>
        <Link
          href="/documents"
          className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:shadow-md"
        >
          <div className="font-medium">Documents</div>
          <div className="mt-1 text-sm text-neutral-500">Upload, index, and manage sources.</div>
        </Link>
      </div>
    </main>
  );
}
