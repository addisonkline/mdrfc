import type { CommentThread as CommentThreadType } from '../../types';
import type { HeadingInfo } from '../../utils/markdown';
import { CommentItem } from './CommentItem';

interface CommentThreadProps {
  thread: CommentThreadType;
  rfcId: number;
  depth?: number;
  headings?: HeadingInfo[];
  onRefresh: () => void;
}

export function CommentThread({ thread, rfcId, depth = 0, headings = [], onRefresh }: CommentThreadProps) {
  const indent = Math.min(depth, 10);

  return (
    <div className={indent > 0 ? 'ml-6 border-l border-gray-200 pl-4' : ''}>
      <CommentItem comment={thread} rfcId={rfcId} headings={headings} onRefresh={onRefresh} />
      {thread.replies.map((reply) => (
        <CommentThread
          key={reply.id}
          thread={reply}
          rfcId={rfcId}
          depth={depth + 1}
          headings={headings}
          onRefresh={onRefresh}
        />
      ))}
    </div>
  );
}
