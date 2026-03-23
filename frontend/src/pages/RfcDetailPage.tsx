import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { getRfc } from '../api/rfcs';
import { getComments } from '../api/comments';
import { RfcMetaHeader } from '../components/rfc/RfcMetaHeader';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { CommentThread } from '../components/comments/CommentThread';
import { CommentForm } from '../components/comments/CommentForm';
import { useAuth } from '../hooks/useAuth';
import type { CommentListSort } from '../types';

const COMMENT_PAGE_SIZE = 10;

export function RfcDetailPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const { user, isAuthenticated } = useAuth();
  const [commentOffset, setCommentOffset] = useState(0);
  const [commentSort, setCommentSort] = useState<CommentListSort>('created_at_desc');

  const { data: rfcData, error: rfcError, loading: rfcLoading } = useApi(
    () => getRfc(rfcId),
    [rfcId],
  );

  const {
    data: commentsData,
    error: commentsError,
    loading: commentsLoading,
    refetch: refetchComments,
  } = useApi(
    () =>
      getComments(rfcId, {
        limit: COMMENT_PAGE_SIZE,
        offset: commentOffset,
        sort: commentSort,
      }),
    [rfcId, commentOffset, commentSort],
  );

  if (rfcLoading) return <p className="text-gray-500">Loading...</p>;
  if (rfcError) return <p className="text-red-600">{rfcError}</p>;
  if (!rfcData) return null;

  const rfc = rfcData.rfc;
  const isAuthor =
    user &&
    user.name_first === rfc.author_name_first &&
    user.name_last === rfc.author_name_last;

  const threads = commentsData?.comment_threads ?? [];
  const commentsPagination = commentsData?.metadata.pagination;
  const totalThreads = commentsPagination?.total ?? 0;
  const threadStart = totalThreads === 0 ? 0 : commentOffset + 1;
  const threadEnd = totalThreads === 0 ? 0 : commentOffset + threads.length;
  const hasNextComments = commentsPagination?.has_more ?? false;

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
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-xl font-semibold">Comments</h2>
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <span>Order</span>
            <select
              value={commentSort}
              onChange={(event) => {
                setCommentSort(event.target.value as CommentListSort);
                setCommentOffset(0);
              }}
              className="rounded-md border border-gray-200 bg-white px-2 py-1.5 text-sm text-gray-700"
            >
              <option value="created_at_desc">Newest threads</option>
              <option value="created_at_asc">Oldest threads</option>
            </select>
          </label>
        </div>

        {commentsLoading && <p className="text-gray-500">Loading comments...</p>}
        {commentsError && <p className="text-red-600">{commentsError}</p>}
        {!commentsLoading && !commentsError && (
          <div className="mb-4 flex flex-col gap-3 text-sm text-gray-500 sm:flex-row sm:items-center sm:justify-between">
            <p>
              Showing {threadStart}-{threadEnd} of {totalThreads} threads
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setCommentOffset((currentOffset) => Math.max(0, currentOffset - COMMENT_PAGE_SIZE))}
                disabled={commentOffset === 0 || commentsLoading}
                className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setCommentOffset((currentOffset) => currentOffset + COMMENT_PAGE_SIZE)}
                disabled={!hasNextComments || commentsLoading}
                className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}

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
            <CommentForm
              rfcId={rfcId}
              onSubmitted={() => {
                if (commentOffset === 0) {
                  refetchComments();
                  return;
                }
                setCommentOffset(0);
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
