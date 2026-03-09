import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { getRfc } from '../api/rfcs';
import { getComments } from '../api/comments';
import { RfcMetaHeader } from '../components/rfc/RfcMetaHeader';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { CommentThread } from '../components/comments/CommentThread';
import { CommentForm } from '../components/comments/CommentForm';
import { useAuth } from '../hooks/useAuth';
import { ApiError } from '../api/client';

export function RfcDetailPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const { user, isAuthenticated } = useAuth();

  const { data: rfcData, error: rfcError, loading: rfcLoading } = useApi(
    () => getRfc(rfcId),
    [rfcId],
  );

  const {
    data: commentsData,
    error: commentsError,
    loading: commentsLoading,
    refetch: refetchComments,
  } = useApi(async () => {
    try {
      return await getComments(rfcId);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        return { comment_threads: [], metadata: {} };
      }
      throw err;
    }
  }, [rfcId]);

  if (rfcLoading) return <p className="text-gray-500">Loading...</p>;
  if (rfcError) return <p className="text-red-600">{rfcError}</p>;
  if (!rfcData) return null;

  const rfc = rfcData.rfc;
  const isAuthor =
    user &&
    user.name_first === rfc.author_name_first &&
    user.name_last === rfc.author_name_last;

  const threads = commentsData?.comment_threads ?? [];

  return (
    <div>
      <RfcMetaHeader rfc={rfc} />

      {isAuthor && (
        <Link
          to={`/rfc/${rfc.id}/edit`}
          className="mb-4 inline-block rounded-md bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
        >
          Edit RFC
        </Link>
      )}

      <MarkdownRenderer content={rfc.content} />

      <div className="mt-10 border-t border-gray-200 pt-6">
        <h2 className="mb-4 text-xl font-semibold">Comments</h2>

        {commentsLoading && <p className="text-gray-500">Loading comments...</p>}
        {commentsError && <p className="text-red-600">{commentsError}</p>}

        {threads.length === 0 && !commentsLoading && (
          <p className="text-sm text-gray-400">No comments yet.</p>
        )}

        {threads.map((thread) => (
          <CommentThread
            key={thread.id}
            thread={thread}
            rfcId={rfcId}
            onRefresh={refetchComments}
          />
        ))}

        {isAuthenticated && (
          <div className="mt-6">
            <h3 className="mb-2 text-sm font-medium text-gray-700">Add a comment</h3>
            <CommentForm rfcId={rfcId} onSubmitted={refetchComments} />
          </div>
        )}
      </div>
    </div>
  );
}
