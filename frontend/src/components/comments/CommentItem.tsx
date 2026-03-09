import { useState } from 'react';
import type { CommentThread } from '../../types';
import { CommentForm } from './CommentForm';
import { useAuth } from '../../hooks/useAuth';

interface CommentItemProps {
  comment: CommentThread;
  rfcId: number;
  onRefresh: () => void;
}

export function CommentItem({ comment, rfcId, onRefresh }: CommentItemProps) {
  const [replying, setReplying] = useState(false);
  const { isAuthenticated } = useAuth();

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
      {isAuthenticated && (
        <button
          onClick={() => setReplying(!replying)}
          className="mt-1 text-xs text-blue-600 hover:text-blue-800"
        >
          {replying ? 'Cancel' : 'Reply'}
        </button>
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
