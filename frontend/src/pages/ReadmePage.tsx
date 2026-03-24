import { Link } from 'react-router-dom';
import { getReadme } from '../api/readme';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { useAuth } from '../hooks/useAuth';
import { useApi } from '../hooks/useApi';

export function ReadmePage() {
  const { user } = useAuth();
  const { data, error, loading } = useApi(() => getReadme(), []);

  if (loading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (error) {
    const isUnauthorized = error === 'unauthorized';
    return (
      <div className="mx-auto max-w-3xl pt-12">
        <h1 className="mb-3 text-2xl font-bold">Server Guide</h1>
        <p className="text-red-600">
          {isUnauthorized ? 'Log in to view this private server guide.' : error}
        </p>
        {isUnauthorized && (
          <Link
            to="/login?redirect=/readme"
            className="mt-4 inline-block text-blue-600 hover:text-blue-800"
          >
            Go to login
          </Link>
        )}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const readme = data.readme;

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-gray-400">README</p>
          <h1 className="mt-2 text-3xl font-bold">Server Guide</h1>
          <p className="mt-2 text-sm text-gray-500">
            Markdown guidance and reference material published for this MDRFC server.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            to="/readme/revisions"
            className="rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            View Revision History
          </Link>
          {user?.is_admin && (
            <Link
              to="/admin/readme/revisions/new"
              className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Publish Revision
            </Link>
          )}
        </div>
      </div>

      <div className="mb-8 grid gap-4 rounded-lg border border-gray-200 bg-white p-5 sm:grid-cols-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Visibility</p>
          <p className="mt-1 text-sm text-gray-700">{readme.public ? 'Public' : 'Private'}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Updated</p>
          <p className="mt-1 text-sm text-gray-700">
            {new Date(readme.updated_at).toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
            Current Revision
          </p>
          <p className="mt-1 break-all text-sm text-gray-700">{readme.current_revision}</p>
        </div>
      </div>

      <MarkdownRenderer content={readme.content} />
    </div>
  );
}
