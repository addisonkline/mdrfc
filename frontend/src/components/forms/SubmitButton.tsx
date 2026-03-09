interface SubmitButtonProps {
  loading?: boolean;
  children: React.ReactNode;
}

export function SubmitButton({ loading, children }: SubmitButtonProps) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
