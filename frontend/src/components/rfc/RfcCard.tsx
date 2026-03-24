import { Link } from 'react-router-dom';
import type { RFCDocumentSummary } from '../../types';
import { RfcStatusBadge } from './RfcStatusBadge';

export function RfcCard({ rfc }: { rfc: RFCDocumentSummary }) {
  return (
    <Link
      to={`/rfcs/${rfc.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:border-blue-300 hover:shadow-sm"
    >
      <div className="mb-2 flex items-center gap-2">
        <RfcStatusBadge status={rfc.status} />
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
          {rfc.public ? 'Public' : 'Private'}
        </span>
        <span className="text-xs text-gray-400">RFC-{rfc.id}</span>
      </div>
      <h3 className="mb-1 text-lg font-semibold text-gray-900">{rfc.title}</h3>
      <p className="mb-2 text-sm text-gray-600 line-clamp-2">{rfc.summary}</p>
      <div className="text-xs text-gray-400">
        {rfc.author_name_first} {rfc.author_name_last} &middot;{' '}
        {new Date(rfc.created_at).toLocaleDateString()}
      </div>
    </Link>
  );
}
