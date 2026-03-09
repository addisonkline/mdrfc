import type { RFCStatus } from '../../types';

const styles: Record<RFCStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  open: 'bg-blue-100 text-blue-700',
  accepted: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
};

export function RfcStatusBadge({ status }: { status: RFCStatus }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}>
      {status}
    </span>
  );
}
