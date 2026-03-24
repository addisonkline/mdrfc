import { Link } from 'react-router-dom';
import { getReviewNeededRfcs } from '../api/rfcs';
import { AdminNav } from '../components/admin/AdminNav';
import { useApi } from '../hooks/useApi';

export function AdminReviewQueuePage() {
  const { data, error, loading } = useApi(() => getReviewNeededRfcs(), []);

  if (loading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!data) {
    return null;
  }

  const rfcs = [...data.rfcs].sort(
    (left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime(),
  );

  return (
    <div className="mx-auto max-w-4xl">
      <AdminNav />

      <div className="mb-6">
        <h1 className="text-2xl font-bold">Review Queue</h1>
        <p className="mt-2 text-sm text-gray-500">
          RFCs listed here have requested admin review. Open an RFC to accept or reject it.
        </p>
      </div>

      {rfcs.length === 0 ? (
        <p className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500">
          No RFCs are waiting for review.
        </p>
      ) : (
        <div className="space-y-4">
          {rfcs.map((rfc) => (
            <div
              key={rfc.id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-800">
                  Review requested
                </span>
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  {rfc.public ? 'Public' : 'Private'}
                </span>
                <span className="text-xs text-gray-400">RFC-{rfc.id}</span>
              </div>
              <h2 className="text-lg font-semibold text-gray-900">{rfc.title}</h2>
              <p className="mt-1 text-sm text-gray-600">{rfc.summary}</p>
              <p className="mt-3 text-sm text-gray-500">
                {rfc.author_name_first} {rfc.author_name_last} · Updated{' '}
                {new Date(rfc.updated_at).toLocaleString()}
              </p>
              <div className="mt-4">
                <Link
                  to={`/rfcs/${rfc.id}`}
                  className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Review RFC
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
