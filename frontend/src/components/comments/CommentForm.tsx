import { useState } from 'react';
import { validateCommentContent } from '../../validation';
import { postComment } from '../../api/comments';

interface CommentFormProps {
  rfcId: number;
  parentCommentId?: number | null;
  onSubmitted: () => void;
  onCancel?: () => void;
}

export function CommentForm({ rfcId, parentCommentId = null, onSubmitted, onCancel }: CommentFormProps) {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const validationError = validateCommentContent(content);
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await postComment({ rfc_id: rfcId, parent_comment_id: parentCommentId, content });
      setContent('');
      onSubmitted();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-2">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write a comment..."
        rows={3}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      <div className="mt-2 flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Posting...' : 'Post Comment'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
