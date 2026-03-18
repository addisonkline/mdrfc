from datetime import datetime, timedelta

from mdrfc.backend.comment import RFCComment, build_comment_threads, find_comment_thread


def _comment(
    id: int,
    rfc_id: int,
    parent_id: int | None,
    created_at: datetime,
    content: str,
) -> RFCComment:
    return RFCComment(
        id=id,
        rfc_id=rfc_id,
        parent_id=parent_id,
        created_at=created_at,
        content=content,
        author_name_first="Alice",
        author_name_last="Smith",
    )


def test_build_comment_threads_builds_nested_tree() -> None:
    base = datetime(2026, 3, 5, 10, 0, 0)
    comments = [
        _comment(id=3, rfc_id=1, parent_id=2, created_at=base + timedelta(seconds=3), content="grandchild"),
        _comment(id=2, rfc_id=1, parent_id=1, created_at=base + timedelta(seconds=2), content="child"),
        _comment(id=1, rfc_id=1, parent_id=None, created_at=base + timedelta(seconds=1), content="root"),
    ]

    threads = build_comment_threads(comments)

    assert len(threads) == 1
    assert threads[0].id == 1
    assert len(threads[0].replies) == 1
    assert threads[0].replies[0].id == 2
    assert len(threads[0].replies[0].replies) == 1
    assert threads[0].replies[0].replies[0].id == 3


def test_build_comment_threads_sorts_roots_and_replies_by_created_at_then_id() -> None:
    base = datetime(2026, 3, 5, 10, 0, 0)
    comments = [
        _comment(id=7, rfc_id=1, parent_id=5, created_at=base + timedelta(seconds=2), content="reply-later"),
        _comment(id=4, rfc_id=1, parent_id=None, created_at=base + timedelta(seconds=2), content="root-b"),
        _comment(id=5, rfc_id=1, parent_id=None, created_at=base + timedelta(seconds=1), content="root-a"),
        _comment(id=6, rfc_id=1, parent_id=5, created_at=base + timedelta(seconds=2), content="reply-earlier-id"),
    ]

    threads = build_comment_threads(comments)

    assert [thread.id for thread in threads] == [5, 4]
    assert [reply.id for reply in threads[0].replies] == [6, 7]


def test_build_comment_threads_promotes_orphaned_replies_to_roots() -> None:
    base = datetime(2026, 3, 5, 10, 0, 0)
    comments = [
        _comment(id=1, rfc_id=1, parent_id=999, created_at=base, content="orphan"),
        _comment(id=2, rfc_id=1, parent_id=None, created_at=base + timedelta(seconds=1), content="normal-root"),
    ]

    threads = build_comment_threads(comments)

    assert [thread.id for thread in threads] == [1, 2]


def test_find_comment_thread_finds_nested_reply() -> None:
    base = datetime(2026, 3, 5, 10, 0, 0)
    comments = [
        _comment(id=1, rfc_id=1, parent_id=None, created_at=base, content="root"),
        _comment(id=2, rfc_id=1, parent_id=1, created_at=base + timedelta(seconds=1), content="child"),
    ]
    threads = build_comment_threads(comments)

    result = find_comment_thread(threads, 2)

    assert result is not None
    assert result.id == 2


def test_find_comment_thread_returns_none_for_missing_id() -> None:
    base = datetime(2026, 3, 5, 10, 0, 0)
    comments = [
        _comment(id=1, rfc_id=1, parent_id=None, created_at=base, content="root"),
    ]
    threads = build_comment_threads(comments)

    result = find_comment_thread(threads, 999)

    assert result is None
