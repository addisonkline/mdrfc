import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  deleteQuarantinedComment,
  getQuarantinedComments,
  restoreQuarantinedComment,
} from '../api/comments';
import { AdminNav } from '../components/admin/AdminNav';
import { useApi } from '../hooks/useApi';

export function QuarantinedCommentsPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const { data, error, loading, refetch } = useApi(() => getQuarantinedComments(rfcId), [rfcId]);
  const [actionKey, setActionKey] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  async function handleRestore(quarantineId: number) {
    setActionKey(`restore:${quarantineId}`);
    setActionError(null);
    setFeedback(null);
    try {
      await restoreQuarantinedComment(rfcId, quarantineId);
      setFeedback(`Restored quarantined comment #${quarantineId}.`);
      refetch();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setActionKey(null);
    }
  }

  async function handleDelete(quarantineId: number) {
    if (!window.confirm('Permanently delete this quarantined comment? This cannot be undone.')) {
      return;
    }

    setActionKey(`delete:${quarantineId}`);
    setActionError(null);
    setFeedback(null);
    try {
      await deleteQuarantinedComment(rfcId, quarantineId);
      setFeedback(`Deleted quarantined comment #${quarantineId}.`);
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

  const comments = [...data.quarantined_comments].sort(
    (left, right) =>
      new Date(right.quarantined_at).getTime() - new Date(left.quarantined_at).getTime(),
  );

  return (
    <div className="mx-auto max-w-4xl">
      <AdminNav />

      <div className="mb-6">
        <Link to={`/rfcs/${rfcId}`} className="text-sm text-blue-600 hover:text-blue-800">
          Back to RFC
        </Link>
        <h1 className="mt-2 text-2xl font-bold">Quarantined Comments</h1>
        <p className="mt-2 text-sm text-gray-500">Manage quarantined comments for RFC-{rfcId}.</p>
      </div>

      {feedback && <p className="mb-4 text-sm text-green-600">{feedback}</p>}
      {actionError && <p className="mb-4 text-sm text-red-600">{actionError}</p>}

      {comments.length === 0 ? (
        <p className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500">
          No quarantined comments were found for this RFC.
        </p>
      ) : (
        <div className="space-y-4">
          {comments.map((entry) => (
            <div
              key={entry.quarantine_id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700">
                  Quarantined
                </span>
                <span className="text-xs text-gray-400">Quarantine #{entry.quarantine_id}</span>
                <span className="text-xs text-gray-400">Comment #{entry.comment.id}</span>
              </div>

              <p className="whitespace-pre-wrap text-sm text-gray-800">{entry.comment.content}</p>

              <dl className="mt-4 grid gap-3 text-sm text-gray-600 sm:grid-cols-2">
                <div>
                  <dt className="font-medium text-gray-900">Comment Author</dt>
                  <dd>
                    {entry.comment.author_name_first} {entry.comment.author_name_last}
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-900">Original Comment Time</dt>
                  <dd>{new Date(entry.comment.created_at).toLocaleString()}</dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-900">Quarantined By</dt>
                  <dd>
                    {entry.quarantined_by_name_first} {entry.quarantined_by_name_last}
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-900">Quarantined At</dt>
                  <dd>{new Date(entry.quarantined_at).toLocaleString()}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="font-medium text-gray-900">Reason</dt>
                  <dd>{entry.reason}</dd>
                </div>
              </dl>

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleRestore(entry.quarantine_id)}
                  disabled={actionKey !== null}
                  className="rounded-md border border-emerald-300 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-50"
                >
                  {actionKey === `restore:${entry.quarantine_id}` ? 'Restoring...' : 'Restore Comment'}
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(entry.quarantine_id)}
                  disabled={actionKey !== null}
                  className="rounded-md border border-red-300 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
                >
                  {actionKey === `delete:${entry.quarantine_id}` ? 'Deleting...' : 'Delete Permanently'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
