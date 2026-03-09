import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { listRfcs } from '../api/rfcs';
import { RfcCard } from '../components/rfc/RfcCard';
import type { RFCStatus } from '../types';
import { ApiError } from '../api/client';

const STATUS_FILTERS: (RFCStatus | 'all')[] = ['all', 'draft', 'open', 'accepted', 'rejected'];

export function HomePage() {
  const [filter, setFilter] = useState<RFCStatus | 'all'>('all');

  const { data, error, loading } = useApi(async () => {
    try {
      return await listRfcs();
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        return { rfcs: [], metadata: {} };
      }
      throw err;
    }
  });

  const rfcs = data?.rfcs ?? [];
  const filtered = filter === 'all' ? rfcs : rfcs.filter((r) => r.status === filter);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">RFCs</h1>
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`rounded-md px-3 py-1 text-xs font-medium ${
                filter === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && filtered.length === 0 && (
        <p className="py-12 text-center text-gray-400">No RFCs yet.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {filtered.map((rfc) => (
          <RfcCard key={rfc.id} rfc={rfc} />
        ))}
      </div>
    </div>
  );
}
