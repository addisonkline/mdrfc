import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { listRfcs } from '../api/rfcs';
import { RfcCard } from '../components/rfc/RfcCard';
import type { RFCStatus } from '../types';

const STATUS_FILTERS: (RFCStatus | 'all')[] = ['all', 'draft', 'open', 'accepted', 'rejected'];
const RFC_PAGE_SIZE = 8;

export function HomePage() {
  const [filter, setFilter] = useState<RFCStatus | 'all'>('all');
  const [page, setPage] = useState(0);

  const { data, error, loading } = useApi(
    () =>
      listRfcs({
        limit: RFC_PAGE_SIZE,
        offset: page * RFC_PAGE_SIZE,
        status: filter === 'all' ? undefined : filter,
        sort: 'updated_at_desc',
      }),
    [filter, page],
  );

  const rfcs = data?.rfcs ?? [];
  const pagination = data?.metadata.pagination;
  const total = pagination?.total ?? 0;
  const start = total === 0 ? 0 : page * RFC_PAGE_SIZE + 1;
  const end = total === 0 ? 0 : page * RFC_PAGE_SIZE + rfcs.length;
  const hasNext = pagination?.has_more ?? false;

  function handleFilterChange(nextFilter: RFCStatus | 'all') {
    setFilter(nextFilter);
    setPage(0);
  }

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">RFCs</h1>
        <div className="flex flex-wrap gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => handleFilterChange(s)}
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
      {!loading && !error && (
        <div className="mb-4 flex flex-col gap-3 text-sm text-gray-500 sm:flex-row sm:items-center sm:justify-between">
          <p>
            Showing {start}-{end} of {total} RFCs
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((currentPage) => Math.max(0, currentPage - 1))}
              disabled={page === 0 || loading}
              className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => setPage((currentPage) => currentPage + 1)}
              disabled={!hasNext || loading}
              className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
      {!loading && !error && rfcs.length === 0 && (
        <p className="py-12 text-center text-gray-400">
          {filter === 'all' ? 'No RFCs yet.' : 'No RFCs match this status.'}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {rfcs.map((rfc) => (
          <RfcCard key={rfc.id} rfc={rfc} />
        ))}
      </div>
    </div>
  );
}
