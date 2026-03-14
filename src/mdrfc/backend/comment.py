from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

import mdrfc.backend.constants as consts
from mdrfc.backend.users import (
    validate_name_last,
    validate_name_first
)


def validate_comment_content(content: str) -> str:
    if len(content) < consts.LEN_COMMENT_CONTENT_MIN:
        raise ValueError(f"content must be at least {consts.LEN_COMMENT_CONTENT_MIN} characters long")
    if len(content) > consts.LEN_COMMENT_CONTENT_MAX:
        raise ValueError(f"content must be no greater than {consts.LEN_COMMENT_CONTENT_MAX} characters long")
    return content


class RFCComment(BaseModel):
    id: int
    parent_id: int | None
    rfc_id: int
    created_at: datetime
    content: Annotated[str, AfterValidator(validate_comment_content)]
    author_name_first: Annotated[str, AfterValidator(validate_name_first)]
    author_name_last: Annotated[str, AfterValidator(validate_name_last)]


class RFCCommentInDB(BaseModel):
    id: int
    parent_id: int | None
    rfc_id: int
    created_at: datetime
    content: str
    created_by: int
    is_quarantined: bool = False


class QuarantinedComment(BaseModel):
    quarantine_id: int
    quarantined_by_name_last: str
    quarantined_by_name_first: str
    quarantined_at: datetime
    reason: str
    comment: RFCComment


class QuarantinedCommentInDB(BaseModel):
    quarantine_id: int
    quarantined_by: int
    quarantined_at: datetime
    reason: str
    comment_id: int


class CommentThread(BaseModel):
    id: int
    parent_id: int | None
    author_name_first: str
    author_name_last: str
    created_at: datetime
    content: str
    replies: list["CommentThread"] = Field(default_factory=list)


def build_comment_threads(
    comments: list[RFCComment]
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
