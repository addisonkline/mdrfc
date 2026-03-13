from argparse import ArgumentParser, Namespace
import json
import os
from urllib.parse import urlsplit

import dotenv
import httpx
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich.style import Style

from mdrfc.backend.comment import CommentThread
import mdrfc.responses as res_types
from mdrfc.backend.auth import Token, User
from mdrfc.utils.version import get_mdrfc_version

import shlex


dotenv.load_dotenv()


_url: str = None # type: ignore
_username: str = "{unknown}"
_token: str = None # type: ignore

_console = Console()


def _get_user_agent() -> str:
    """
    The value to use in the `User-Agent` HTTP header.
    """
    version = get_mdrfc_version()
    return f"MDRFC-Client/{version} (https://github.com/addisonkline/mdrfc)"


parser = ArgumentParser(
    prog="mdrfc-client",
    usage="<command> [option]...",
    description="The MDRFC CLI client",
    epilog="Copyright (c) 2026 Addison Kline (GitHub: @addisonkline)",
)
subparsers = parser.add_subparsers(title="commands", dest="command")

# ping the server
ping_desc = "Ping the remote server"
ping_p = subparsers.add_parser(
    "ping",
    aliases=["p"],
    usage="ping [option]...",
    help=ping_desc,
    description=ping_desc,
)
ping_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed server info"
)

# log into the server
login_desc = "Log into the remote server"
login_p = subparsers.add_parser(
    "login",
    aliases=["l"],
    usage="login <username> [option]...",
    help=login_desc,
    description=login_desc,
)
login_p.add_argument(
    "username",
    help="username for this MDRFC server"
)
login_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed login info"
)

# log out of the server
logout_desc = "(login required) Log out of the remote server"
logout_p = subparsers.add_parser(
    "logout",
    aliases=["lo"],
    usage="logout [option]...",
    help=logout_desc,
    description=logout_desc,
)

# ask the server who this client is
whoami_desc = "(login required) Get client info from this server"
whoami_p = subparsers.add_parser(
    "whoami",
    aliases=["me"],
    usage="whoami [option]...",
    help=whoami_desc,
    description=whoami_desc,
)
whoami_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed client info"
)

# get the list of RFC documents
rfc_list_desc = "List the current RFC documents"
rfc_list_p = subparsers.add_parser(
    "rfc-list",
    aliases=["rfc-l"],
    usage="rfc-list [option]...",
    help=rfc_list_desc,
    description=rfc_list_desc,
)
rfc_list_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed metadata per RFC"
)

# get a specific RFC document by ID
rfc_get_desc = "Get an existing RFC by ID"
rfc_get_p = subparsers.add_parser(
    "rfc-get",
    aliases=["rfc-g"],
    usage="rfc-get <id> [option]...",
    help=rfc_get_desc,
    description=rfc_get_desc,
)
rfc_get_p.add_argument(
    "id",
    type=int,
    help="the RFC ID to fetch"
)
rfc_get_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

# post a new RFC to the server
rfc_post_desc = "(login required) Post a new RFC to the server"
rfc_post_p = subparsers.add_parser(
    "rfc-post",
    aliases=["rfc-p"],
    usage="rfc-post <docpath> <title> <slug> <summary> <status> [option]...",
    help=rfc_post_desc,
    description=rfc_post_desc,
)
rfc_post_p.add_argument(
    "docpath",
    help="the path of the Markdown file to upload"
)
rfc_post_p.add_argument(
    "title",
    help="the title of the RFC to post"
)
rfc_post_p.add_argument(
    "slug",
    help="the slug string unique to this RFC"
)
rfc_post_p.add_argument(
    "summary",
    help="the summary of the RFC to post"
)
rfc_post_p.add_argument(
    "status",
    choices=["draft", "open"],
    help="the status of the RFC to post"
)
rfc_post_p.add_argument(
    "-a",
    "--agent-contributors",
    nargs="*",
    help="optionally add agent contributor(s)"
)
rfc_post_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

# list the comments on a given RFC
comment_list_desc = "List all comment threads on a given RFC"
comment_list_p = subparsers.add_parser(
    "comment-list",
    aliases=["com-l"],
    usage="comment-list <rfc_id> [option]...",
    help=comment_list_desc,
    description=comment_list_desc,
)
comment_list_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to fetch comments on"
)
comment_list_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

# get a specific RFC comment
comment_get_desc = "Get a specific comment on an RFC"
comment_get_p = subparsers.add_parser(
    "comment-get",
    aliases=["com-g"],
    usage="comment-get <rfc_id> <comment_id> [option]...",
    help=comment_get_desc,
    description=comment_get_desc,
)
comment_get_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to fetch the comment on"
)
comment_get_p.add_argument(
    "comment_id",
    type=int,
    help="the comment ID to fetch"
)
comment_get_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

# post a comment on an RFC
comment_post_desc = "(login required) Post a new comment on an RFC"
comment_post_p = subparsers.add_parser(
    "comment-post",
    aliases=["com-p"],
    usage="comment-post <content> [option]...",
    help=comment_post_desc,
    description=comment_post_desc,
)
comment_post_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to post the comment on",
)
comment_post_p.add_argument(
    "content",
    help="the comment content"
)
comment_post_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)
comment_post_p.add_argument(
    "-r",
    "--reply-to",
    type=int,
    help="the comment ID to reply to"
)

revision_list_desc = "Get all revisions for a specific RFC"
revision_list_p = subparsers.add_parser(
    "revision-list",
    aliases=["rev-l"],
    usage="revision-list <rfc_id> [option]...",
    help=revision_list_desc,
    description=revision_list_desc
)
revision_list_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to get revisions for"
)
revision_list_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

revision_get_desc = "Get a specific revision for an RFC"
revision_get_p = subparsers.add_parser(
    "revision-get",
    aliases=["rev-g"],
    usage="revision-get <rfc_id> <revision_id> [option]...",
    help=revision_get_desc,
    description=revision_get_desc
)
revision_get_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to get a revision for"
)
revision_get_p.add_argument(
    "revision_id",
    type=str,
    help="the revision ID to get"
)
revision_get_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

revision_post_desc = "(login required) Create a new revision for a given RFC"
revision_post_p = subparsers.add_parser(
    "revision-post",
    aliases=["rev-p"],
    usage="revision-post <rfc_id> <message> [option]...",
    help=revision_post_desc,
    description=revision_post_desc,
)
revision_post_p.add_argument(
    "rfc_id",
    type=int,
    help="the ID of the RFC to revise"
)
revision_post_p.add_argument(
    "message",
    help="the message for this RFC revision"
)
revision_post_p.add_argument(
    "-t",
    "--title",
    help="update the RFC's title"
)
revision_post_p.add_argument(
    "--slug",
    help="update the RFC's slug"
)
revision_post_p.add_argument(
    "-S",
    "--status",
    choices=["draft", "open"],
    help="update the RFC's status"
)
revision_post_p.add_argument(
    "-s",
    "--summary",
    help="update the RFC's summary"
)
revision_post_p.add_argument(
    "-cf",
    "--content-file",
    help="update the RFC's content with the given filepath"
)
revision_post_p.add_argument(
    "-a",
    "--agent-contributors",
    nargs="*",
    help="optionally add agent contributor(s)"
)
revision_post_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed response metadata"
)

# command handlers
def _cmd_ping(args: Namespace) -> None:
    """
    Ping the remote MDRFC server.
    """
    global _console
    global _url
    response = httpx.get(
        _url,
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRootResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] remote not recognized as an MDRFC server")
        return
    
    if args.verbose:
        _console.print(f"[bold]name[/bold]: {response_obj.name}")
        _console.print(f"[bold]version[/bold]: {response_obj.version}")
        _console.print(f"[bold]status[/bold]: {response_obj.status}")
        _console.print(f"[bold]uptime[/bold]: {response_obj.uptime}")
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        print("pong")


def _cmd_login(args: Namespace) -> None:
    """
    Attempt to log into the server.
    """
    username = args.username
    _console = Console()
    password = Prompt.get_input(
        _console,
        prompt=f"password for {username}: ",
        password=True
    )

    if not password.strip():
        _console.print("[bold red]error[/bold red] password required")
        return

    body = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": username,
        "client_secret": password
    }

    global _url
    response = httpx.post(
        url=f"{_url}/login",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": _get_user_agent()
        }
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = Token.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return

    global _username
    global _token
    _username = username
    _token = response_obj.access_token
    if args.verbose:
        _console.print(f"[bold]token[/bold]: {response_obj.access_token}")
        _console.print(f"[bold]type[/bold]: {response_obj.token_type}")
    else:
        _console.print(f"successfully logged in as [green]{_username}[/green]")


def _cmd_logout(args: Namespace) -> None:
    """
    Attempt to log out of the remote server.
    """
    global _username
    global _token
    if (_username == "{unknown}") or (_token is None):
        _console.print("[bold red]error[/bold red] not logged in")
        return
    
    _username = "{unknown}"
    _token = None # type: ignore
    _console.print(f"successfully logged out of {_url}")


def _cmd_whoami(args: Namespace) -> None:
    """
    Attempt to fetch client info from the server.
    """ 
    global _token
    if _token is None:
        _console.print("[bold red]error[/bold red] not logged in")
        return

    global _url
    response = httpx.get(
        url=f"{_url}/users/me",
        headers={
            "Authorization": f"Bearer {_token}",
            "User-Agent": _get_user_agent()
        }
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = User.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]username[/bold]: {response_obj.username}")
        _console.print(f"[bold]email[/bold]: {response_obj.email}")
        _console.print(f"[bold]name[/bold]: {response_obj.name_last}, {response_obj.name_first}")
        _console.print(f"[bold]created[/bold]: {response_obj.created_at}")
    else:
        _console.print(f"username: [green]{response_obj.username}[/green]")


def _cmd_rfc_list(args: Namespace) -> None:
    """
    Attempt to list the RFCs currently on this server.
    """
    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfcs",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcsResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    rfcs = [doc for doc in response_obj.rfcs]
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
        for rfc in rfcs:
            _console.print(f"[bold]id[/bold]: {rfc.id}")
            _console.print(f"[bold]title[/bold]: {rfc.title}")
            _console.print(f"[bold]author[/bold]: {rfc.author_name_last}, {rfc.author_name_first}")
            _console.print(f"[bold]slug[/bold]: {rfc.slug}")
            _console.print(f"[bold]summary[/bold]: {rfc.summary}")
            _console.print(f"[bold]status[/bold]: {rfc.status}")
            _console.print(f"[bold]created at[/bold]: {rfc.created_at}")
            _console.print(f"[bold]updated at[/bold]: {rfc.updated_at}")
            _console.print("=" * 40)
    else:
        _console.print(f"found {len(rfcs)} documents")
        for rfc in rfcs:
            _console.print(f"RFC {rfc.id}: {rfc.author_name_last}, {rfc.author_name_first}. '{rfc.title}'. Last updated: {rfc.updated_at}.")


def _cmd_rfc_get(args: Namespace) -> None:
    """
    Attempt to get a specific RFC on this server.
    """
    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfc/{args.id}",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        if args.verbose:
            _console.print(f"{response.text}")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
    rfc = response_obj.rfc
    _console.print(f"[bold]title[/bold]: {rfc.title}")
    _console.print(f"[bold]author[/bold]: {rfc.author_name_first} {rfc.author_name_last}")
    _console.print(f"[bold]slug[/bold]: {rfc.slug}")
    _console.print(f"[bold]status[/bold]: {rfc.status}")
    _console.print(f"[bold]summary[/bold]: {rfc.summary}")
    _console.print(f"[bold]created at[/bold]: {rfc.created_at}")
    _console.print(f"[bold]updated at[/bold]: {rfc.updated_at}")
    _console.print(f"[bold]revisions[/bold]: {rfc.revisions}")
    _console.print(f"[bold]current[/bold]: {rfc.current_revision}")
    _console.print(f"[bold]agent contributions[/bold]: {rfc.agent_contributions}")
    _console.print()
    _console.print(Markdown(rfc.content))
    _console.print()


def _cmd_rfc_post(args: Namespace) -> None:
    """
    Attempt to post a new RFC to this server.
    """
    global _token
    if _token is None:
        _console.print("[bold red]error[/bold red] not logged in")
        return
    
    rfc_content = ""
    try:
        with open(args.docpath) as file:
            rfc_content = file.read()
    except Exception:
        _console.print(f"[bold red]error[/bold red] could not open file '{args.docpath}'")
        return

    body = {
        "title": args.title,
        "slug": args.slug,
        "status": args.status,
        "summary": args.summary,
        "content": rfc_content,
        "agent_contributors": args.agent_contributors or []
    }
    
    global _url
    response = httpx.post(
        url=f"{_url}/rfc",
        headers={
            "Authorization": f"Bearer {_token}",
            "User-Agent": _get_user_agent()
        },
        json=body
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.PostRfcResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]id[/bold]: {response_obj.rfc_id}")
        _console.print(f"[bold]created at[/bold]: {response_obj.created_at}")
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        _console.print(f"successfully posted new RFC with ID {response_obj.rfc_id}")


def _cmd_comment_list(args: Namespace) -> None:
    """
    Attempt to list the comments on a given RFC.
    """
    rfc_id = args.rfc_id
    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/comments",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcCommentsResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    comment_threads = [thread for thread in response_obj.comment_threads]
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
    _console.print(f"found {len(comment_threads)} comments")
    _print_comment_threads(comment_threads)


def _cmd_comment_get(args: Namespace) -> None:
    """
    Attempt to get a specific comment on a given RFC.
    """
    rfc_id = args.rfc_id
    comment_id = args.comment_id

    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/comment/{comment_id}",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcCommentResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    comment = response_obj.comment
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
    _print_comment(comment)


def _cmd_comment_post(args: Namespace) -> None:
    """
    Attempt to post a new comment on a given RFC.
    """
    global _token
    if _token is None:
        _console.print("[bold red]error[/bold red] not logged in")
        return
    
    rfc_id = args.rfc_id
    content = args.content
    try:
        reply_to = args.reply_to
    except AttributeError:
        reply_to = None

    body = {
        "content": content,
        "parent_comment_id": reply_to
    }

    global _url
    response = httpx.post(
        url=f"{_url}/rfc/{rfc_id}/comment",
        headers={
            "Authorization": f"Bearer {_token}",
            "User-Agent": _get_user_agent()
        },
        json=body
    )

    response_json = response.json()
    try:
        response_obj = res_types.PostRfcCommentResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]id[/bold]: {response_obj.comment_id}")
        _console.print(f"[bold]created at[/bold]: {response_obj.created_at}")
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        _console.print(f"successfully posted new comment with ID {response_obj.comment_id}")


def _cmd_revision_list(args: Namespace) -> None:
    """
    Attempt to list the revisions of a given RFC.
    """
    rfc_id = args.rfc_id
    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/revs",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcRevisionsResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
    for summary in response_obj.revisions:
        _console.print(f"[bold]id[/bold]: {summary.id}")
        _console.print(f"[bold]author[/bold]: {summary.author_name_first} {summary.author_name_last}")
        _console.print(f"[bold]created at[/bold]: {summary.created_at}")
        _console.print(f"[bold]message[/bold]: {summary.message}")
        _console.print("=" * 40)


def _cmd_revision_get(args: Namespace) -> None:
    """
    Attempt to get a specific revision of a given RFC.
    """
    rfc_id = args.rfc_id
    revision_id = args.revision_id

    global _url
    global _token

    headers = {
        "User-Agent": _get_user_agent()
    }

    if _token is not None:
        headers["Authorization"] = f"Bearer {_token}"

    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/rev/{revision_id}",
        headers=headers
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcRevisionResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    if args.verbose:
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
        _console.print("=" * 40)
    rev = response_obj.revision
    _console.print(f"[bold]title[/bold]: {rev.title}")
    _console.print(f"[bold]author[/bold]: {rev.author_name_first} {rev.author_name_last}")
    _console.print(f"[bold]slug[/bold]: {rev.slug}")
    _console.print(f"[bold]status[/bold]: {rev.status}")
    _console.print(f"[bold]summary[/bold]: {rev.summary}")
    _console.print(f"[bold]created at[/bold]: {rev.created_at}")
    _console.print(f"[bold]agent contributors[/bold]: {rev.agent_contributors}")
    _console.print()
    _console.print(Markdown(rev.content))
    _console.print()


def _cmd_revision_post(args: Namespace) -> None:
    """
    Attempt to post a new revision for an existing RFC.
    """
    global _token
    if _token is None:
        _console.print("[bold red]error[/bold red] not logged in")
        return
    
    rfc_id = args.rfc_id
    message = args.message
    try:
        title = args.title
    except AttributeError:
        title = None
    try:
        slug = args.slug
    except AttributeError:
        slug = None
    try:
        status = args.status
    except AttributeError:
        status = None
    try:
        summary = args.summary
    except AttributeError:
        summary = None
    try:
        agent_contributors = args.agent_contributors
    except AttributeError:
        agent_contributors = []
    try:
        content_file = args.content_file
        with open(content_file) as file:
            content = file.read()
    except AttributeError:
        content = None

    body = {
        "update": {
            "title": title,
            "slug": slug,
            "status": status,
            "summary": summary,
            "content": content,
            "agent_contributors": agent_contributors,
        },
        "message": message
    }

    global _url
    response = httpx.post(
        url=f"{_url}/rfc/{rfc_id}/rev",
        headers={
            "Authorization": f"Bearer {_token}",
            "User-Agent": _get_user_agent()
        },
        json=body
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.PostRfcRevisionResponse.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return
    
    rev = response_obj.revision
    if args.verbose:
        _console.print(f"[bold]id[/bold]: {rev.id}")
        _console.print(f"[bold]author[/bold]: {rev.author_name_first} {rev.author_name_last}")
        _console.print(f"[bold]created at[/bold]: {rev.created_at}")
        _console.print(f"[bold]message[/bold]: {rev.message}")
        _console.print(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        _console.print(f"successfully posted new RFC revision with ID {rev.id}")


def _print_comment(comment: CommentThread) -> None:
    """
    Pretty print a comment and its replies.
    """
    _console.print(comment.model_dump_json(indent=4))


def _print_comment_threads(threads: list[CommentThread]) -> None:
    """
    Recursively pretty-print comment threads.
    """
    for thread in threads:
        _print_comment(thread)


def _get_preamble() -> str:
    """
    The preamble that the rich console prints upon CLI launch.
    """
    preamble = ""

    global _token
    global _url
    global _username
    if _token is None:
        preamble += "[bold yellow]warning[/bold yellow] you are not currently logged in\n"
        preamble += "[bold yellow]warning[/bold yellow] run [cyan]login <username>[/cyan] to authenticate\n"
    preamble += ("=" * 60) + "\n"
    preamble += f"[bold]MDRFC CLI Client [cyan]v{get_mdrfc_version()}[/cyan][/bold]\n"
    preamble += f"[bold]Server[/bold]: {_url}\n"
    preamble += "[bold]Username[/bold]: "
    if _username == "{unknown}":
        preamble += "[italic yellow]{unknown}[/italic yellow]\n"
    else:
        preamble += f"[green]{_username}[/green]\n"
    preamble += "\n"
    preamble += "For help: [cyan]help[/cyan], [cyan]?[/cyan]\n"
    preamble += "To exit: [cyan]exit[/cyan], [cyan]quit[/cyan]\n"
    preamble += ("=" * 60)

    return preamble


def _get_prompt() -> str:
    """
    The prompt for the CLI client REPL.
    """
    global _url
    global _username

    prompt = ""
    prompt += "([cyan]mdrfc[/cyan]) "
    if _username == "{unknown}":
        prompt += "[italic yellow]{unknown}[/italic yellow]"
    else:
        prompt += f"[bold green]{_username}[/bold green]"
    prompt += f"@[bold green]{_url}[/bold green]"
    prompt += "[no_underline white]>[/no_underline white] "

    return prompt 


def _run_repl() -> None:
    """
    Enter the client REPL.
    """
    global _console
    _console.print(_get_preamble())

    commands = {
        "ping": _cmd_ping,
        "p": _cmd_ping,
        "login": _cmd_login,
        "l": _cmd_login,
        "logout": _cmd_logout,
        "lo": _cmd_logout,
        "whoami": _cmd_whoami,
        "me": _cmd_whoami,
        "rfc-list": _cmd_rfc_list,
        "rfc-l": _cmd_rfc_list,
        "rfc-get": _cmd_rfc_get,
        "rfc-g": _cmd_rfc_get,
        "rfc-post": _cmd_rfc_post,
        "rfc-p": _cmd_rfc_post,
        "comment-list": _cmd_comment_list,
        "com-l": _cmd_comment_list,
        "comment-get": _cmd_comment_get,
        "com-g": _cmd_comment_get,
        "comment-post": _cmd_comment_post,
        "com-p": _cmd_comment_post,
        "revision-list": _cmd_revision_list,
        "rev-l": _cmd_revision_list,
        "revision-get": _cmd_revision_get,
        "rev-g": _cmd_revision_get,
        "revision-post": _cmd_revision_post,
        "rev-p": _cmd_revision_post,
    }

    running = True
    while running:
        user_input = _console.input(
            prompt=_get_prompt()
        )

        if user_input == "":
            continue
        elif (user_input == "quit") or (user_input == "exit"):
            running = False
        elif (user_input == "help") or (user_input == "?"):
            parser.print_help()
        else:
            try:
                args = parser.parse_args(shlex.split(user_input))
                handler = commands.get(args.command)
                if handler:
                    handler(args)
                else:
                    parser.print_usage()
                    print("for help, run `help`, `?`")
            except SystemExit:
                continue
            except Exception as e:
                _console.print(f"[bold red]error[/bold red] command failed: {e}")


def _validate_url(url: str) -> None:
    """
    Exit if the provided URL is not valid.
    """
    split = urlsplit(url)
    if split.netloc == "":
        print("error: invalid URL")
        exit(1)


def _login_on_startup() -> None:
    """
    Attempt to log in on client startup.
    """
    username = os.getenv("MDRFC_USERNAME")
    password = os.getenv("MDRFC_PASSWORD")

    if (username is None) or (password is None):
        _console.print("[bold red]error[/bold red] env vars `MDRFC_USERNAME` and `MDRFC_PASSWORD` are required to log in")
        return
    
    body = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": username,
        "client_secret": password
    }

    global _url
    response = httpx.post(
        url=f"{_url}/login",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": _get_user_agent()
        }
    )

    if response.status_code != 200:
        _console.print(f"[bold red]error[/bold red] login request failed with status code {response.status_code}")
        return
    
    response_json = response.json()
    try:
        response_obj = Token.model_validate(response_json)
    except ValidationError as e:
        _console.print("[bold red]error[/bold red] response validation failed")
        _console.print(e)
        return

    global _username
    global _token
    _username = username
    _token = response_obj.access_token


def run_client(
    args: Namespace
) -> None:
    """
    Run the MDRFC CLI client.
    """
    url = args.url

    _validate_url(url)

    global _url
    _url = url

    print(f"connecting to {url}...")

    if not args.no_login:
        _login_on_startup()
    _run_repl()

    print(f"disconnected from {url}")