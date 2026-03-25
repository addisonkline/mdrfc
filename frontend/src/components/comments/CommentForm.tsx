import { useState } from 'react';
import { validateCommentContent } from '../../validation';
import { postComment } from '../../api/comments';
import type { HeadingInfo } from '../../utils/markdown';

interface CommentFormProps {
  rfcId: number;
  parentCommentId?: number | null;
  headings?: HeadingInfo[];
  onSubmitted: () => void;
  onCancel?: () => void;
}

export function CommentForm({
  rfcId,
  parentCommentId = null,
  headings = [],
  onSubmitted,
  onCancel,
}: CommentFormProps) {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRefs, setSelectedRefs] = useState<Set<string>>(new Set());
  const [showRefPicker, setShowRefPicker] = useState(false);

  function toggleRef(slug: string) {
    setSelectedRefs((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) {
        next.delete(slug);
      } else {
        next.add(slug);
      }
      return next;
    });
  }

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
      const references = Array.from(selectedRefs);
      await postComment({
        rfc_id: rfcId,
        parent_comment_id: parentCommentId,
        content,
        ...(references.length > 0 ? { references } : {}),
      });
      setContent('');
      setSelectedRefs(new Set());
      setShowRefPicker(false);
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
      {headings.length > 0 && (
        <div className="mt-1">
          <button
            type="button"
            onClick={() => setShowRefPicker(!showRefPicker)}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            {showRefPicker ? 'Hide section references' : 'Reference sections'}
            {selectedRefs.size > 0 && ` (${selectedRefs.size})`}
          </button>
          {showRefPicker && (
            <div className="mt-2 max-h-40 overflow-y-auto rounded-md border border-gray-200 p-2">
              {headings.map((heading) => (
                <label
                  key={heading.slug}
                  className="flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-sm hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={selectedRefs.has(heading.slug)}
                    onChange={() => toggleRef(heading.slug)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{heading.text}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      )}
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
