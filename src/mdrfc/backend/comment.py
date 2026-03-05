from datetime import datetime

from pydantic import BaseModel, Field


class RFCComment(BaseModel):
    id: int
    parent_id: int | None
    rfc_id: int
    created_by: int
    created_at: datetime
    content: str


class RFCCommentWithAuthor(BaseModel):
    id: int
    parent_id: int | None
    created_at: datetime
    content: str
    author_name_first: str
    author_name_last: str


class CommentThread(BaseModel):
    id: int
    parent_id: int | None
    author_name_first: str
    author_name_last: str
    created_at: datetime
    content: str
    replies: list["CommentThread"] = Field(default_factory=list)


def build_comment_threads(
    comments: list[RFCCommentWithAuthor]
) -> list[CommentThread]:
    """
    Create a structured list of nested comment threads from a list of flat DB rows.
    """
    if len(comments) == 0:
        return []

    comments_sorted = sorted(
        comments,
        key=lambda comment: (comment.created_at, comment.id)
    )

    thread_nodes = {
        comment.id: CommentThread(
            id=comment.id,
            parent_id=comment.parent_id,
            author_name_first=comment.author_name_first,
            author_name_last=comment.author_name_last,
            created_at=comment.created_at,
            content=comment.content,
        )
        for comment in comments_sorted
    }

    roots: list[CommentThread] = []
    for comment in comments_sorted:
        node = thread_nodes[comment.id]
        if comment.parent_id is None:
            roots.append(node)
            continue

        parent_node = thread_nodes.get(comment.parent_id)
        if parent_node is None:
            # Fallback for inconsistent data: keep orphaned replies visible at root.
            roots.append(node)
            continue

        parent_node.replies.append(node)

    return roots


def find_comment_thread(
    comment_threads: list[CommentThread],
    comment_id: int,
) -> CommentThread | None:
    """
    Find a comment thread node by ID in a nested comment thread list.
    """
    for comment_thread in comment_threads:
        if comment_thread.id == comment_id:
            return comment_thread
        child_result = find_comment_thread(comment_thread.replies, comment_id)
        if child_result is not None:
            return child_result
    return None
