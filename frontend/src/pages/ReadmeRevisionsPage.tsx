import { Link } from 'react-router-dom';
import { getReadme, listReadmeRevisions } from '../api/readme';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../hooks/useAuth';

export function ReadmeRevisionsPage() {
  const { user } = useAuth();
  const { data: readmeData, error: readmeError, loading: readmeLoading } = useApi(
    () => getReadme(),
    [],
  );
  const {
    data: revisionsData,
    error: revisionsError,
    loading: revisionsLoading,
  } = useApi(() => listReadmeRevisions(), []);

  if (readmeLoading || revisionsLoading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (readmeError) {
    const isUnauthorized = readmeError === 'unauthorized';
    return (
      <div className="mx-auto max-w-3xl pt-12">
        <h1 className="mb-3 text-2xl font-bold">README Revisions</h1>
        <p className="text-red-600">
          {isUnauthorized ? 'Log in to view this private server guide.' : readmeError}
        </p>
        {isUnauthorized && (
          <Link
            to="/login?redirect=/readme/revisions"
            className="mt-4 inline-block text-blue-600 hover:text-blue-800"
          >
            Go to login
          </Link>
        )}
      </div>
    );
  }

  if (revisionsError) {
    return <p className="text-red-600">{revisionsError}</p>;
  }

  if (!readmeData || !revisionsData) {
    return null;
  }

  const readme = readmeData.readme;
  const revisions = [...revisionsData.revisions].sort(
    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  );

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/readme" className="text-sm text-blue-600 hover:text-blue-800">
            Back to Server Guide
          </Link>
          <h1 className="mt-2 text-2xl font-bold">README Revision History</h1>
          <p className="mt-1 text-sm text-gray-500">
            {revisions.length} published revision{revisions.length === 1 ? '' : 's'}
          </p>
        </div>
        {user?.is_admin && (
          <Link
            to="/admin/readme/revisions/new"
            className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Publish Revision
          </Link>
        )}
      </div>

      <div className="space-y-4">
        {revisions.map((revision) => {
          const isCurrent = revision.revision_id === readme.current_revision;
          return (
            <Link
              key={revision.revision_id}
              to={`/readme/revisions/${revision.revision_id}`}
              className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:border-blue-300 hover:shadow-sm"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-gray-900 px-2.5 py-1 text-xs font-medium text-white">
                  {isCurrent ? 'Current revision' : 'Revision'}
                </span>
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  {revision.public ? 'Public' : 'Private'}
                </span>
                <span className="text-xs text-gray-400">{revision.revision_id}</span>
              </div>

              <p className="text-sm font-medium text-gray-900">{revision.reason}</p>
              <p className="mt-1 text-sm text-gray-500">
                {revision.created_by_name_first} {revision.created_by_name_last} on{' '}
                {new Date(revision.created_at).toLocaleString()}
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
