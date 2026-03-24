import { useState } from 'react';
import type { CommentThread } from '../../types';
import { CommentForm } from './CommentForm';
import { useAuth } from '../../hooks/useAuth';
import { quarantineComment } from '../../api/comments';
import { validateQuarantineCommentReason } from '../../validation';

interface CommentItemProps {
  comment: CommentThread;
  rfcId: number;
  onRefresh: () => void;
}

export function CommentItem({ comment, rfcId, onRefresh }: CommentItemProps) {
  const [replying, setReplying] = useState(false);
  const [showQuarantineForm, setShowQuarantineForm] = useState(false);
  const [quarantineReason, setQuarantineReason] = useState('');
  const [quarantineError, setQuarantineError] = useState<string | null>(null);
  const [quarantining, setQuarantining] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const isAdmin = Boolean(user?.is_admin);

  async function handleQuarantineSubmit(event: React.FormEvent) {
    event.preventDefault();

    const validationError = validateQuarantineCommentReason(quarantineReason);
    if (validationError) {
      setQuarantineError(validationError);
      return;
    }

    setQuarantining(true);
    setQuarantineError(null);
    try {
      await quarantineComment(rfcId, comment.id, quarantineReason);
      setShowQuarantineForm(false);
      setQuarantineReason('');
      onRefresh();
    } catch (err) {
      setQuarantineError((err as Error).message);
    } finally {
      setQuarantining(false);
    }
  }

  return (
    <div className="py-3">
      <div className="flex items-center gap-2 text-sm">
        <span className="font-medium text-gray-900">
          {comment.author_name_first} {comment.author_name_last}
        </span>
        <span className="text-gray-400">
          {new Date(comment.created_at).toLocaleString()}
        </span>
      </div>
      <p className="mt-1 whitespace-pre-wrap text-sm text-gray-700">{comment.content}</p>
      <div className="mt-1 flex flex-wrap gap-3">
        {isAuthenticated && (
          <button
            onClick={() => setReplying(!replying)}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            {replying ? 'Cancel Reply' : 'Reply'}
          </button>
        )}
        {isAdmin && (
          <button
            type="button"
            onClick={() => {
              setShowQuarantineForm((current) => !current);
              setQuarantineError(null);
            }}
            className="text-xs text-red-600 hover:text-red-800"
          >
            {showQuarantineForm ? 'Cancel Moderation' : 'Quarantine'}
          </button>
        )}
      </div>
      {showQuarantineForm && (
        <form onSubmit={handleQuarantineSubmit} className="mt-3 rounded-md bg-red-50 p-3">
          <label className="mb-2 block text-sm font-medium text-red-900">
            Quarantine Reason
          </label>
          <textarea
            value={quarantineReason}
            onChange={(event) => setQuarantineReason(event.target.value)}
            onBlur={() =>
              setQuarantineError(validateQuarantineCommentReason(quarantineReason))
            }
            rows={3}
            className="w-full rounded-md border border-red-200 bg-white px-3 py-2 text-sm focus:border-red-400 focus:outline-none"
          />
          {quarantineError && <p className="mt-2 text-sm text-red-700">{quarantineError}</p>}
          <button
            type="submit"
            disabled={quarantining}
            className="mt-3 rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
          >
            {quarantining ? 'Quarantining...' : 'Confirm Quarantine'}
          </button>
        </form>
      )}
      {replying && (
        <CommentForm
          rfcId={rfcId}
          parentCommentId={comment.id}
          onSubmitted={() => {
            setReplying(false);
            onRefresh();
          }}
          onCancel={() => setReplying(false)}
        />
      )}
    </div>
  );
}
