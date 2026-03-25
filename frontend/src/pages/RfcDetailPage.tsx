import { useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getComments } from '../api/comments';
import { getRfc, quarantineRfc, requestRfcReview, updateRfcStatus } from '../api/rfcs';
import { CommentForm } from '../components/comments/CommentForm';
import { CommentThread } from '../components/comments/CommentThread';
import { RfcMetaHeader } from '../components/rfc/RfcMetaHeader';
import { MarkdownRenderer } from '../components/rfc/MarkdownRenderer';
import { AgentContributorsList } from '../components/rfc/AgentContributorsList';
import { useAuth } from '../hooks/useAuth';
import { useApi } from '../hooks/useApi';
import type { CommentListSort, RFCReviewDecision } from '../types';
import { validateQuarantineRfcReason, validateRfcReviewReason } from '../validation';
import { extractHeadings } from '../utils/markdown';

const COMMENT_PAGE_SIZE = 10;

export function RfcDetailPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [commentOffset, setCommentOffset] = useState(0);
  const [commentSort, setCommentSort] = useState<CommentListSort>('created_at_desc');
  const [actionError, setActionError] = useState<string | null>(null);
  const [requestingReview, setRequestingReview] = useState(false);
  const [quarantining, setQuarantining] = useState(false);
  const [showQuarantineForm, setShowQuarantineForm] = useState(false);
  const [quarantineReason, setQuarantineReason] = useState('');
  const [quarantineError, setQuarantineError] = useState<string | null>(null);
  const [reviewStatus, setReviewStatus] = useState<RFCReviewDecision>('accepted');
  const [reviewReason, setReviewReason] = useState('');
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const {
    data: rfcData,
    error: rfcError,
    loading: rfcLoading,
    refetch: refetchRfc,
  } = useApi(() => getRfc(rfcId), [rfcId]);

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

  async function handleRequestReview() {
    if (!rfcData) return;

    setRequestingReview(true);
    setActionError(null);
    try {
      await requestRfcReview(rfcData.rfc.id);
      refetchRfc();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setRequestingReview(false);
    }
  }

  async function handleQuarantineSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!rfcData) return;

    const reasonError = validateQuarantineRfcReason(quarantineReason);
    if (reasonError) {
      setQuarantineError(reasonError);
      return;
    }

    setQuarantining(true);
    setActionError(null);
    setQuarantineError(null);

    try {
      await quarantineRfc(rfcData.rfc.id, quarantineReason);
      navigate('/rfcs');
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setQuarantining(false);
    }
  }

  async function handleReviewDecisionSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!rfcData) return;

    const reasonError = validateRfcReviewReason(reviewReason);
    if (reasonError) {
      setReviewError(reasonError);
      return;
    }

    setUpdatingStatus(true);
    setActionError(null);
    setReviewError(null);

    try {
      await updateRfcStatus(rfcData.rfc.id, {
        status: reviewStatus,
        reason: reviewReason,
      });
      setReviewReason('');
      refetchRfc();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setUpdatingStatus(false);
    }
  }

  if (rfcLoading) return <p className="text-gray-500">Loading...</p>;
  if (rfcError) return <p className="text-red-600">{rfcError}</p>;
  if (!rfcData) return null;

  const rfc = rfcData.rfc;
  const headings = useMemo(() => extractHeadings(rfc.content), [rfc.content]);
  const isAuthor = user?.id === rfc.author_id;
  const isAdmin = Boolean(user?.is_admin);
  const canRevise =
    isAuthor && !rfc.review_requested && rfc.status !== 'accepted' && rfc.status !== 'rejected';
  const canRequestReview = isAuthor && !rfc.review_requested && !rfc.reviewed;
  const canQuarantine = isAuthenticated && (isAuthor || isAdmin);
  const canModerateReview = isAdmin && rfc.review_requested && !rfc.reviewed;
  const currentAgentContributors = rfc.agent_contributions[rfc.current_revision] ?? [];

  const threads = commentsData?.comment_threads ?? [];
  const commentsPagination = commentsData?.metadata.pagination;
  const totalThreads = commentsPagination?.total ?? 0;
  const threadStart = totalThreads === 0 ? 0 : commentOffset + 1;
  const threadEnd = totalThreads === 0 ? 0 : commentOffset + threads.length;
  const hasNextComments = commentsPagination?.has_more ?? false;

  return (
    <div>
      <RfcMetaHeader rfc={rfc} />

      <div className="mb-8 grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Current Revision Metadata
          </h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Slug</p>
              <p className="mt-1 text-sm text-gray-700">{rfc.slug}</p>
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Revision ID</p>
              <p className="mt-1 break-all text-sm text-gray-700">{rfc.current_revision}</p>
            </div>
            <div className="sm:col-span-2">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                Agent Contributors
              </p>
              <div className="mt-2">
                <AgentContributorsList
                  contributors={currentAgentContributors}
                  emptyLabel="No agent contributors recorded for the current revision"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Actions</h2>
          <div className="mt-4 flex flex-col gap-3">
            <Link
              to={`/rfcs/${rfc.id}/revisions`}
              className="inline-flex items-center justify-center rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              View Revision History
            </Link>

            {isAdmin && (
              <>
                <Link
                  to="/admin/review-needed"
                  className="inline-flex items-center justify-center rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Open Review Queue
                </Link>
                <Link
                  to={`/admin/rfcs/${rfc.id}/comments/quarantined`}
                  className="inline-flex items-center justify-center rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Manage Quarantined Comments
                </Link>
              </>
            )}

            {canRevise && (
              <Link
                to={`/rfcs/${rfc.id}/revisions/new`}
                className="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Create Revision
              </Link>
            )}

            {canRequestReview && (
              <button
                type="button"
                onClick={handleRequestReview}
                disabled={requestingReview}
                className="rounded-md border border-amber-300 px-3 py-2 text-sm font-medium text-amber-800 hover:bg-amber-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {requestingReview ? 'Requesting review...' : 'Request Admin Review'}
              </button>
            )}

            {canModerateReview && (
              <form onSubmit={handleReviewDecisionSubmit} className="rounded-md bg-emerald-50 p-3">
                <label className="mb-2 block text-sm font-medium text-emerald-900">Decision</label>
                <select
                  value={reviewStatus}
                  onChange={(event) => setReviewStatus(event.target.value as RFCReviewDecision)}
                  className="w-full rounded-md border border-emerald-200 bg-white px-3 py-2 text-sm text-gray-700 focus:border-emerald-400 focus:outline-none"
                >
                  <option value="accepted">Accept RFC</option>
                  <option value="rejected">Reject RFC</option>
                </select>
                <label className="mb-2 mt-3 block text-sm font-medium text-emerald-900">
                  Review Note
                </label>
                <textarea
                  value={reviewReason}
                  onChange={(event) => setReviewReason(event.target.value)}
                  onBlur={() => setReviewError(validateRfcReviewReason(reviewReason))}
                  rows={4}
                  className="w-full rounded-md border border-emerald-200 bg-white px-3 py-2 text-sm focus:border-emerald-400 focus:outline-none"
                />
                {reviewError && <p className="mt-2 text-sm text-red-700">{reviewError}</p>}
                <button
                  type="submit"
                  disabled={updatingStatus}
                  className="mt-3 w-full rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {updatingStatus ? 'Saving Decision...' : 'Save Review Decision'}
                </button>
              </form>
            )}

            {canQuarantine && (
              <>
                <button
                  type="button"
                  onClick={() => {
                    setShowQuarantineForm((current) => !current);
                    setQuarantineError(null);
                  }}
                  className="rounded-md border border-red-300 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
                >
                  {showQuarantineForm ? 'Cancel Quarantine' : 'Quarantine RFC'}
                </button>

                {showQuarantineForm && (
                  <form onSubmit={handleQuarantineSubmit} className="rounded-md bg-red-50 p-3">
                    <label className="mb-2 block text-sm font-medium text-red-900">
                      Quarantine Reason
                    </label>
                    <textarea
                      value={quarantineReason}
                      onChange={(event) => setQuarantineReason(event.target.value)}
                      onBlur={() => setQuarantineError(validateQuarantineRfcReason(quarantineReason))}
                      rows={4}
                      className="w-full rounded-md border border-red-200 bg-white px-3 py-2 text-sm focus:border-red-400 focus:outline-none"
                    />
                    {quarantineError && <p className="mt-2 text-sm text-red-700">{quarantineError}</p>}
                    <button
                      type="submit"
                      disabled={quarantining}
                      className="mt-3 w-full rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {quarantining ? 'Quarantining...' : 'Confirm Quarantine'}
                    </button>
                  </form>
                )}
              </>
            )}

            {!canRevise && isAuthor && !rfc.reviewed && rfc.review_requested && (
              <p className="text-sm text-amber-700">
                Review has already been requested, so new revisions are locked.
              </p>
            )}

            {rfc.reviewed && (
              <p className="text-sm text-gray-600">
                This RFC has been reviewed and can no longer receive new revisions.
              </p>
            )}
          </div>

          {actionError && <p className="mt-4 text-sm text-red-600">{actionError}</p>}
        </div>
      </div>

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
                onClick={() =>
                  setCommentOffset((currentOffset) => Math.max(0, currentOffset - COMMENT_PAGE_SIZE))
                }
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
            headings={headings}
            onRefresh={refetchComments}
          />
        ))}

        {isAuthenticated && (
          <div className="mt-6">
            <h3 className="mb-2 text-sm font-medium text-gray-700">Add a comment</h3>
            <CommentForm
              rfcId={rfcId}
              headings={headings}
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
