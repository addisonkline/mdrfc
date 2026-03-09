interface FormFieldProps {
  label: string;
  error?: string | null;
  children: React.ReactNode;
}

export function FormField({ label, error, children }: FormFieldProps) {
  return (
    <div className="mb-4">
      <label className="mb-1 block text-sm font-medium text-gray-700">{label}</label>
      {children}
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}
