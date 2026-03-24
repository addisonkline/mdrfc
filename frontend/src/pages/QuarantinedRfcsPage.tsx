import { useState } from 'react';
import {
  deleteQuarantinedRfc,
  getQuarantinedRfcs,
  restoreQuarantinedRfc,
} from '../api/rfcs';
import { AdminNav } from '../components/admin/AdminNav';
import { useApi } from '../hooks/useApi';

export function QuarantinedRfcsPage() {
  const { data, error, loading, refetch } = useApi(() => getQuarantinedRfcs(), []);
  const [actionKey, setActionKey] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  async function handleRestore(quarantineId: number) {
    setActionKey(`restore:${quarantineId}`);
    setActionError(null);
    setFeedback(null);
    try {
      await restoreQuarantinedRfc(quarantineId);
      setFeedback(`Restored quarantined RFC #${quarantineId}.`);
      refetch();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setActionKey(null);
    }
  }

  async function handleDelete(quarantineId: number) {
    if (!window.confirm('Permanently delete this quarantined RFC? This cannot be undone.')) {
      return;
    }

    setActionKey(`delete:${quarantineId}`);
    setActionError(null);
    setFeedback(null);
    try {
      await deleteQuarantinedRfc(quarantineId);
      setFeedback(`Deleted quarantined RFC #${quarantineId}.`);
      refetch();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setActionKey(null);
    }
  }

  if (loading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!data) {
    return null;
  }

  const rfcs = [...data.quarantined_rfcs].sort(
    (left, right) =>
      new Date(right.quarantined_at).getTime() - new Date(left.quarantined_at).getTime(),
  );

  return (
    <div className="mx-auto max-w-4xl">
      <AdminNav />

      <div className="mb-6">
        <h1 className="text-2xl font-bold">Quarantined RFCs</h1>
        <p className="mt-2 text-sm text-gray-500">
          Restore quarantined RFCs back into the main listing, or permanently delete them.
        </p>
      </div>

      {feedback && <p className="mb-4 text-sm text-green-600">{feedback}</p>}
      {actionError && <p className="mb-4 text-sm text-red-600">{actionError}</p>}

      {rfcs.length === 0 ? (
        <p className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500">
          No RFCs are currently quarantined.
        </p>
      ) : (
        <div className="space-y-4">
          {rfcs.map((rfc) => (
            <div
              key={rfc.quarantine_id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700">
                  Quarantined
                </span>
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  {rfc.rfc_status}
                </span>
                <span className="text-xs text-gray-400">Quarantine #{rfc.quarantine_id}</span>
              </div>
              <h2 className="text-lg font-semibold text-gray-900">{rfc.rfc_title}</h2>
              <p className="mt-1 text-sm text-gray-600">{rfc.rfc_summary}</p>
              <dl className="mt-4 grid gap-3 text-sm text-gray-600 sm:grid-cols-2">
                <div>
                  <dt className="font-medium text-gray-900">RFC</dt>
                  <dd>
                    RFC-{rfc.rfc_id} · {rfc.rfc_slug}
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-900">Quarantined By</dt>
                  <dd>
                    {rfc.quarantined_by_name_first} {rfc.quarantined_by_name_last}
                  </dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="font-medium text-gray-900">Reason</dt>
                  <dd>{rfc.reason}</dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-900">Quarantined At</dt>
                  <dd>{new Date(rfc.quarantined_at).toLocaleString()}</dd>
                </div>
              </dl>
              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleRestore(rfc.quarantine_id)}
                  disabled={actionKey !== null}
                  className="rounded-md border border-emerald-300 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-50"
                >
                  {actionKey === `restore:${rfc.quarantine_id}` ? 'Restoring...' : 'Restore RFC'}
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(rfc.quarantine_id)}
                  disabled={actionKey !== null}
                  className="rounded-md border border-red-300 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
                >
                  {actionKey === `delete:${rfc.quarantine_id}` ? 'Deleting...' : 'Delete Permanently'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
