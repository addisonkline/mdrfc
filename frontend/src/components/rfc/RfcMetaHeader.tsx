import type { RFCDocument } from '../../types';
import { RfcStatusBadge } from './RfcStatusBadge';

export function RfcMetaHeader({ rfc }: { rfc: RFCDocument }) {
  return (
    <div className="mb-6 border-b border-gray-200 pb-4">
      <div className="mb-2 flex items-center gap-3">
        <RfcStatusBadge status={rfc.status} />
        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
          {rfc.public ? 'Public' : 'Private'}
        </span>
        {rfc.review_requested && !rfc.reviewed && (
          <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-800">
            Review requested
          </span>
        )}
        {rfc.reviewed && (
          <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-800">
            Reviewed
          </span>
        )}
        <span className="text-sm text-gray-400">RFC-{rfc.id}</span>
      </div>
      <h1 className="mb-2 text-3xl font-bold">{rfc.title}</h1>
      <p className="mb-3 text-gray-600">{rfc.summary}</p>
      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
        <span>
          By {rfc.author_name_first} {rfc.author_name_last}
        </span>
        <span>Created {new Date(rfc.created_at).toLocaleDateString()}</span>
        <span>Updated {new Date(rfc.updated_at).toLocaleDateString()}</span>
        <span className="break-all">Current rev {rfc.current_revision}</span>
      </div>
      {rfc.review_reason && (
        <div className="mt-4 rounded-md border border-gray-200 bg-gray-50 p-3 text-sm text-gray-700">
          <span className="font-medium text-gray-900">Review note:</span> {rfc.review_reason}
        </div>
      )}
    </div>
  );
}
