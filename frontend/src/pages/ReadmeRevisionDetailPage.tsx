import { Link, useParams } from 'react-router-dom';
import { getReadme, getReadmeRevision } from '../api/readme';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { useApi } from '../hooks/useApi';

export function ReadmeRevisionDetailPage() {
  const { revisionId } = useParams<{ revisionId: string }>();
  const { data: readmeData, error: readmeError, loading: readmeLoading } = useApi(
    () => getReadme(),
    [],
  );
  const {
    data: revisionData,
    error: revisionError,
    loading: revisionLoading,
  } = useApi(() => getReadmeRevision(revisionId ?? ''), [revisionId]);

  if (readmeLoading || revisionLoading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (readmeError) {
    return <p className="text-red-600">{readmeError}</p>;
  }

  if (revisionError) {
    return <p className="text-red-600">{revisionError}</p>;
  }

  if (!readmeData || !revisionData) {
    return null;
  }

  const readme = readmeData.readme;
  const revision = revisionData.revision;
  const isCurrent = revision.revision_id === readme.current_revision;

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <div className="flex flex-wrap gap-3 text-sm">
          <Link to="/readme" className="text-blue-600 hover:text-blue-800">
            Back to Server Guide
          </Link>
          <Link to="/readme/revisions" className="text-blue-600 hover:text-blue-800">
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
        </div>

        <h1 className="mt-3 text-3xl font-bold">README Revision</h1>
        <p className="mt-2 text-gray-600">{revision.reason}</p>
      </div>

      <div className="mb-8 grid gap-4 rounded-lg border border-gray-200 bg-white p-5 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Revision ID</p>
          <p className="mt-1 break-all text-sm text-gray-700">{revision.revision_id}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Created</p>
          <p className="mt-1 text-sm text-gray-700">{new Date(revision.created_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Author</p>
          <p className="mt-1 text-sm text-gray-700">
            {revision.created_by_name_first} {revision.created_by_name_last}
          </p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Visibility</p>
          <p className="mt-1 text-sm text-gray-700">{revision.public ? 'Public' : 'Private'}</p>
        </div>
      </div>

      <MarkdownRenderer content={revision.content} />
    </div>
  );
}
