import { type FormEvent, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { listRfcs } from '../api/rfcs';
import { RfcCard } from '../components/rfc/RfcCard';
import type { RFCStatus } from '../types';

const STATUS_FILTERS: (RFCStatus | 'all')[] = ['all', 'draft', 'open', 'accepted', 'rejected'];
const RFC_PAGE_SIZE = 8;

export function HomePage() {
  const [filter, setFilter] = useState<RFCStatus | 'all'>('all');
  const [page, setPage] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState<string | undefined>();

  const { data, error, loading } = useApi(
    () =>
      listRfcs({
        limit: RFC_PAGE_SIZE,
        offset: page * RFC_PAGE_SIZE,
        status: filter === 'all' ? undefined : filter,
        query: searchQuery,
        sort: searchQuery ? 'relevance_desc' : 'updated_at_desc',
      }),
    [filter, page, searchQuery],
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

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuery = searchInput.trim();
    setSearchQuery(nextQuery.length > 0 ? nextQuery : undefined);
    setPage(0);
  }

  function handleSearchClear() {
    setSearchInput('');
    setSearchQuery(undefined);
    setPage(0);
  }

  function getEmptyStateMessage() {
    if (searchQuery && filter !== 'all') {
      return 'No RFCs match this search and status.';
    }
    if (searchQuery) {
      return 'No RFCs match this search.';
    }
    if (filter === 'all') {
      return 'No RFCs yet.';
    }
    return 'No RFCs match this status.';
  }

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">RFCs</h1>
        <div className="flex flex-col gap-3 sm:items-end">
          <form onSubmit={handleSearchSubmit} className="flex w-full gap-2 sm:w-auto">
            <input
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search RFCs"
              className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-900 sm:w-72"
            />
            <button
              type="submit"
              className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Search
            </button>
            {searchQuery && (
              <button
                type="button"
                onClick={handleSearchClear}
                className="rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
              >
                Clear
              </button>
            )}
          </form>
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
        <p className="py-12 text-center text-gray-400">{getEmptyStateMessage()}</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {rfcs.map((rfc) => (
          <RfcCard key={rfc.id} rfc={rfc} />
        ))}
      </div>
    </div>
  );
}
