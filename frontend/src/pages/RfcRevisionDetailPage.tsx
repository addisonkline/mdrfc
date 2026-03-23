import { Link, useParams } from 'react-router-dom';
import { getRfc } from '../api/rfcs';
import { getRfcRevision } from '../api/revisions';
import { useApi } from '../hooks/useApi';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { AgentContributorsList } from '../components/rfc/AgentContributorsList';

export function RfcRevisionDetailPage() {
  const { id, revisionId } = useParams<{ id: string; revisionId: string }>();
  const rfcId = Number(id);

  const { data: rfcData, error: rfcError, loading: rfcLoading } = useApi(() => getRfc(rfcId), [rfcId]);
  const {
    data: revisionData,
    error: revisionError,
    loading: revisionLoading,
  } = useApi(() => getRfcRevision(rfcId, revisionId ?? ''), [rfcId, revisionId]);

  if (rfcLoading || revisionLoading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (rfcError) {
    return <p className="text-red-600">{rfcError}</p>;
  }

  if (revisionError) {
    return <p className="text-red-600">{revisionError}</p>;
  }

  if (!rfcData || !revisionData) {
    return null;
  }

  const rfc = rfcData.rfc;
  const revision = revisionData.revision;
  const isCurrent = revision.id === rfc.current_revision;

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <div className="flex flex-wrap gap-3 text-sm">
          <Link to={`/rfcs/${rfcId}`} className="text-blue-600 hover:text-blue-800">
            Back to RFC
          </Link>
          <Link to={`/rfcs/${rfcId}/revisions`} className="text-blue-600 hover:text-blue-800">
            Back to Revision History
          </Link>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-gray-900 px-2.5 py-1 text-xs font-medium text-white">
            {isCurrent ? 'Current revision' : 'Past revision'}
          </span>
          <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
            {revision.public ? 'Public' : 'Private'}
          </span>
          <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
            {revision.status}
          </span>
        </div>

        <h1 className="mt-3 text-3xl font-bold">{revision.title}</h1>
        <p className="mt-2 text-gray-600">{revision.summary}</p>
      </div>

      <div className="mb-8 grid gap-4 rounded-lg border border-gray-200 bg-white p-5 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Revision ID</p>
          <p className="mt-1 break-all text-sm text-gray-700">{revision.id}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Created</p>
          <p className="mt-1 text-sm text-gray-700">{new Date(revision.created_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Author</p>
          <p className="mt-1 text-sm text-gray-700">
            {revision.author_name_first} {revision.author_name_last}
          </p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Slug</p>
          <p className="mt-1 text-sm text-gray-700">{revision.slug}</p>
        </div>
        <div className="sm:col-span-2">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Revision Message</p>
          <p className="mt-1 text-sm text-gray-700">{revision.message}</p>
        </div>
        <div className="sm:col-span-2">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Agent Contributors</p>
          <div className="mt-2">
            <AgentContributorsList
              contributors={revision.agent_contributors}
              emptyLabel="No agent contributors recorded for this revision"
            />
          </div>
        </div>
      </div>

      <MarkdownRenderer content={revision.content} />
    </div>
  );
}
