type Props = { id: string; page?: number; onOpen?: () => void };

export function Citation({ id, page, onOpen }: Props) {
  return (
    <button
      onClick={onOpen}
      className="inline-flex items-center rounded-md bg-neutral-100 px-1.5 py-0.5 text-xs font-mono text-neutral-700 hover:bg-neutral-200"
      title={`Open source ${id}`}
    >
      {id}
      {page !== undefined ? `#p${page}` : null}
    </button>
  );
}
