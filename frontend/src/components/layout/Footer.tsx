export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-4 text-xs text-gray-400">
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-center gap-2 px-4 text-center sm:flex-row sm:gap-3">
        <span>mdrfc - Markdown RFC Platform</span>
        <a
          href="/api/llms.txt"
          target="_blank"
          rel="noreferrer"
          className="font-medium uppercase tracking-wide text-gray-500 hover:text-gray-900"
        >
          llms.txt
        </a>
      </div>
    </footer>
  );
}
