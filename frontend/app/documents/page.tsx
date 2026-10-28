import { DocumentList } from "@/components/document-list";

export default function DocumentsPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-6">
      <h1 className="mb-4 text-2xl font-semibold">Documents</h1>
      <DocumentList />
    </main>
  );
}
