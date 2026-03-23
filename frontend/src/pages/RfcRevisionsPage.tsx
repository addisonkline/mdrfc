import { Link, useParams } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { getRfc } from '../api/rfcs';
import { listRfcRevisions } from '../api/revisions';
import { useAuth } from '../hooks/useAuth';
import { AgentContributorsList } from '../components/rfc/AgentContributorsList';

export function RfcRevisionsPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const { user } = useAuth();

  const { data: rfcData, error: rfcError, loading: rfcLoading } = useApi(() => getRfc(rfcId), [rfcId]);
  const {
    data: revisionsData,
    error: revisionsError,
    loading: revisionsLoading,
  } = useApi(() => listRfcRevisions(rfcId), [rfcId]);

  if (rfcLoading || revisionsLoading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (rfcError) {
    return <p className="text-red-600">{rfcError}</p>;
  }

  if (revisionsError) {
    return <p className="text-red-600">{revisionsError}</p>;
  }

  if (!rfcData || !revisionsData) {
    return null;
  }

  const rfc = rfcData.rfc;
  const revisions = [...revisionsData.revisions].sort(
    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  );
  const isAuthor = user?.id === rfc.author_id;
  const canRevise =
    isAuthor && !rfc.review_requested && rfc.status !== 'accepted' && rfc.status !== 'rejected';

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to={`/rfcs/${rfcId}`} className="text-sm text-blue-600 hover:text-blue-800">
            Back to RFC
          </Link>
          <h1 className="mt-2 text-2xl font-bold">Revision History</h1>
          <p className="mt-1 text-sm text-gray-500">{rfc.title}</p>
        </div>
        {canRevise && (
          <Link
            to={`/rfcs/${rfcId}/revisions/new`}
            className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Create Revision
          </Link>
        )}
      </div>

      <div className="space-y-4">
        {revisions.map((revision) => {
          const isCurrent = revision.id === rfc.current_revision;
          return (
            <Link
              key={revision.id}
              to={`/rfcs/${rfcId}/revisions/${revision.id}`}
              className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:border-blue-300 hover:shadow-sm"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-gray-900 px-2.5 py-1 text-xs font-medium text-white">
                  {isCurrent ? 'Current revision' : 'Revision'}
                </span>
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  {revision.public ? 'Public' : 'Private'}
                </span>
                <span className="text-xs text-gray-400">{revision.id}</span>
              </div>

              <p className="text-sm font-medium text-gray-900">{revision.message}</p>
              <p className="mt-1 text-sm text-gray-500">
                {revision.author_name_first} {revision.author_name_last} on{' '}
                {new Date(revision.created_at).toLocaleString()}
              </p>

              <div className="mt-3">
                <AgentContributorsList
                  contributors={revision.agent_contributors}
                  emptyLabel="No agent contributors recorded for this revision"
                />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
