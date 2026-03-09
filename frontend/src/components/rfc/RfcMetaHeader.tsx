import type { RFCDocument } from '../../types';
import { RfcStatusBadge } from './RfcStatusBadge';

export function RfcMetaHeader({ rfc }: { rfc: RFCDocument }) {
  return (
    <div className="mb-6 border-b border-gray-200 pb-4">
      <div className="mb-2 flex items-center gap-3">
        <RfcStatusBadge status={rfc.status} />
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
      </div>
    </div>
  );
}
