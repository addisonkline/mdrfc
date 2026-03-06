from argparse import ArgumentParser, Namespace
import json
import os
from urllib.parse import urlsplit

import httpx
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from rich import print as rprint
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


_url: str = None # type: ignore
_username: str = "{unknown}"
_token: str = None # type: ignore


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
    add_help=False,
    exit_on_error=False
)
subparsers = parser.add_subparsers(title="commands", dest="command")

# ping the server
ping_desc = "Ping the remote server"
ping_p = subparsers.add_parser(
    "ping",
    usage="ping [option]...",
    help=ping_desc,
    description=ping_desc,
    add_help=False, # the default help option exits the REPL
    exit_on_error=False,
)
ping_p.add_argument( # so replace it with one that doesn't
    "-h",
    "--help",
    action="store_true",
    help="show this help message and exit",
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
    usage="login <username> [option]...",
    help=login_desc,
    description=login_desc,
    add_help=False,
    exit_on_error=False
)
login_p.add_argument(
    "username",
    help="username for this MDRFC server"
)
login_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this help message and exit"
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
    usage="logout [option]...",
    help=logout_desc,
    description=logout_desc,
    add_help=False,
    exit_on_error=False
)
logout_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
)

# ask the server who this client is
whoami_desc = "(login required) Get client info from this server"
whoami_p = subparsers.add_parser(
    "whoami",
    usage="whoami [option]...",
    help=whoami_desc,
    description=whoami_desc,
    add_help=False,
    exit_on_error=False
)
whoami_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this help message and exit"
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
    usage="rfc-list [option]...",
    help=rfc_list_desc,
    description=rfc_list_desc,
    add_help=False,
    exit_on_error=False
)
rfc_list_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
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
    usage="rfc-get <id> [option]...",
    help=rfc_get_desc,
    description=rfc_get_desc,
    add_help=False,
    exit_on_error=False
)
rfc_get_p.add_argument(
    "id",
    type=int,
    help="the RFC ID to fetch"
)
rfc_get_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
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
    usage="rfc-post <docpath> <title> <slug> <summary> <status> [option]...",
    help=rfc_post_desc,
    description=rfc_post_desc,
    add_help=False,
    exit_on_error=False
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
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
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
    usage="comment-list <rfc_id> [option]...",
    help=comment_list_desc,
    description=comment_list_desc,
    add_help=False,
    exit_on_error=False
)
comment_list_p.add_argument(
    "rfc_id",
    type=int,
    help="the RFC ID to fetch comments on"
)
comment_list_p.add_argument(
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
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
    usage="comment-get <rfc_id> <comment_id> [option]...",
    help=comment_get_desc,
    description=comment_get_desc,
    add_help=False,
    exit_on_error=False
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
    "-h",
    "--help",
    action="store_true",
    help="show this message and exit"
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
    usage="comment-post <> [option]...",
    help=comment_post_desc,
    description=comment_post_desc,
    add_help=False,
    exit_on_error=False
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
    "-h",
    "--help",
    action="store_true",
    help="show this messages and exit"
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

# command handlers
def _cmd_ping(args: Namespace) -> None:
    """
    Ping the remote MDRFC server.
    """
    if args.help:
        ping_p.print_help()
        return

    global _url
    response = httpx.get(
        _url,
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRootResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] remote not recognized as an MDRFC server")
        return
    
    if args.verbose:
        rprint(f"[bold]name[/bold]: {response_obj.name}")
        rprint(f"[bold]version[/bold]: {response_obj.version}")
        rprint(f"[bold]status[/bold]: {response_obj.status}")
        rprint(f"[bold]uptime[/bold]: {response_obj.uptime}")
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        print("pong")


def _cmd_login(args: Namespace) -> None:
    """
    Attempt to log into the server.
    """
    if args.help:
        login_p.print_help()
        return
    
    username = args.username
    _console = Console()
    password = Prompt.get_input(
        _console,
        prompt=f"password for {username}: ",
        password=True
    )

    if not password.strip():
        rprint("[bold red]error[/bold red] password required")
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
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = Token.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return

    global _username
    global _token
    _username = username
    _token = response_obj.access_token
    if args.verbose:
        rprint(f"[bold]token[/bold]: {response_obj.access_token}")
        rprint(f"[bold]type[/bold]: {response_obj.token_type}")
    else:
        rprint(f"successfully logged in as [green]{_username}[/green]")


def _cmd_logout(args: Namespace) -> None:
    """
    Attempt to log out of the remote server.
    """
    if args.help:
        logout_p.print_help()
        return
    
    global _username
    global _token
    if (_username == "{unknown}") or (_token is None):
        rprint("[bold red]error[/bold red] not logged in")
        return
    
    _username = "{unknown}"
    _token = None # type: ignore
    rprint(f"successfully logged out of {_url}")


def _cmd_whoami(args: Namespace) -> None:
    """
    Attempt to fetch client info from the server.
    """
    if args.help:
        whoami_p.print_help()
        return
    
    global _token
    if _token is None:
        rprint("[bold red]error[/bold red] not logged in")
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
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = User.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    if args.verbose:
        rprint(f"[bold]username[/bold]: {response_obj.username}")
        rprint(f"[bold]email[/bold]: {response_obj.email}")
        rprint(f"[bold]name[/bold]: {response_obj.name_last}, {response_obj.name_first}")
        rprint(f"[bold]created[/bold]: {response_obj.created_at}")
    else:
        rprint(f"username: [green]{response_obj.username}[/green]")


def _cmd_rfc_list(args: Namespace) -> None:
    """
    Attempt to list the RFCs currently on this server.
    """
    if args.help:
        rfc_list_p.print_help()
        return
    
    global _url
    response = httpx.get(
        url=f"{_url}/rfcs",
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcsResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    rfcs = [doc for doc in response_obj.rfcs]
    if args.verbose:
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
        rprint("=" * 40)
        for rfc in rfcs:
            rprint(f"[bold]id[/bold]: {rfc.id}")
            rprint(f"[bold]title[/bold]: {rfc.title}")
            rprint(f"[bold]author[/bold]: {rfc.author_name_last}, {rfc.author_name_first}")
            rprint(f"[bold]slug[/bold]: {rfc.slug}")
            rprint(f"[bold]summary[/bold]: {rfc.summary}")
            rprint(f"[bold]status[/bold]: {rfc.status}")
            rprint(f"[bold]created at[/bold]: {rfc.created_at}")
            rprint(f"[bold]updated at[/bold]: {rfc.updated_at}")
            rprint("=" * 40)
    else:
        rprint(f"found {len(rfcs)} documents")
        for rfc in rfcs:
            rprint(f"RFC {rfc.id}: {rfc.author_name_last}, {rfc.author_name_first}. '{rfc.title}'. Last updated: {rfc.updated_at}.")


def _cmd_rfc_get(args: Namespace) -> None:
    """
    Attempt to get a specific RFC on this server.
    """
    if args.help:
        rfc_get_p.print_help()
        return
    
    global _url
    response = httpx.get(
        url=f"{_url}/rfc/{args.id}",
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    if args.verbose:
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
        rprint("=" * 40)
    rfc = response_obj.rfc
    rprint(f"[bold]title[/bold]: {rfc.title}")
    rprint(f"[bold]author[/bold]: {rfc.author_name_first} {rfc.author_name_last}")
    rprint(f"[bold]slug[/bold]: {rfc.slug}")
    rprint(f"[bold]status[/bold]: {rfc.status}")
    rprint(f"[bold]summary[/bold]: {rfc.summary}")
    rprint()
    rprint(Markdown(rfc.content))
    rprint()


def _cmd_rfc_post(args: Namespace) -> None:
    """
    Attempt to post a new RFC to this server.
    """
    if args.help:
        rfc_post_p.print_help()
        return
    
    global _token
    if _token is None:
        rprint("[bold red]error[/bold red] not logged in")
        return
    
    rfc_content = ""
    try:
        with open(args.docpath) as file:
            rfc_content = file.read()
    except Exception:
        rprint(f"[bold red]error[/bold red] could not open file '{args.docpath}'")
        return

    body = {
        "title": args.title,
        "slug": args.slug,
        "status": args.status,
        "summary": args.summary,
        "content": rfc_content
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
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.PostRfcResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    if args.verbose:
        rprint(f"[bold]id[/bold]: {response_obj.rfc_id}")
        rprint(f"[bold]created at[/bold]: {response_obj.created_at}")
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        rprint(f"successfully posted new RFC with ID {response_obj.rfc_id}")


def _cmd_comment_list(args: Namespace) -> None:
    """
    Attempt to list the comments on a given RFC.
    """
    if args.help:
        comment_list_p.print_help()
        return
    
    rfc_id = args.rfc_id
    global _url
    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/comments",
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcCommentsResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    comment_threads = [thread for thread in response_obj.comment_threads]
    if args.verbose:
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
        rprint("=" * 40)
    _print_comment_threads(comment_threads)


def _cmd_comment_get(args: Namespace) -> None:
    """
    Attempt to get a specific comment on a given RFC.
    """
    if args.help:
        comment_get_p.print_help()
        return
    
    rfc_id = args.rfc_id
    comment_id = args.comment_id
    global _url
    response = httpx.get(
        url=f"{_url}/rfc/{rfc_id}/comment/{comment_id}",
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    try:
        response_obj = res_types.GetRfcCommentResponse.model_validate(response_json)
    except ValidationError as e:
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    comment = response_obj.comment
    if args.verbose:
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
        rprint("=" * 40)
    _print_comment(comment)


def _cmd_comment_post(args: Namespace) -> None:
    """
    Attempt to post a new comment on a given RFC.
    """
    if args.help:
        comment_post_p.print_help()
        return
    
    global _token
    if _token is None:
        rprint("[bold red]error[/bold red] not logged in")
        return
    
    rfc_id = args.rfc_id
    content = args.content
    try:
        reply_to = args.reply_to
    except AttributeError:
        reply_to = None

    body = {
        "rfc_id": rfc_id,
        "content": content,
        "parent_comment_id": reply_to
    }

    global _url
    response = httpx.post(
        url=f"{_url}/rfc/comment",
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
        rprint("[bold red]error[/bold red] response validation failed")
        rprint(e)
        return
    
    if args.verbose:
        rprint(f"[bold]id[/bold]: {response_obj.comment_id}")
        rprint(f"[bold]created at[/bold]: {response_obj.created_at}")
        rprint(f"[bold]metadata[/bold]: {response_obj.metadata}")
    else:
        rprint(f"successfully posted new comment with ID {response_obj.comment_id}")


def _print_comment(comment: CommentThread) -> None:
    """
    Pretty print a comment and its replies.
    """
    rprint(comment.model_dump_json(indent=4))


def _print_comment_threads(threads: list[CommentThread]) -> None:
    """
    Recursively pretty-print comment threads.
    """
    for thread in threads:
        _print_comment(thread)


def _get_preamble() -> Text:
    """
    The preamble that the rich console prints upon CLI launch.
    """
    preamble = Text("warning", style=Style(color="yellow", bold=True))
    preamble.append(" You are not currently logged in. Run ", style=Style(color="white", bold=False))
    preamble.append("login", style=Style(color="cyan", bold=False))
    preamble.append(" with valid credentials\n", style=Style(color="white", bold=False))
    preamble.append("info", style=Style(color="cyan", bold=True))
    preamble.append(" For help: ", style=Style(color="white", bold=False))
    preamble.append("help", style=Style(color="cyan", bold=False))
    preamble.append(", ", style=Style(color="white", bold=False))
    preamble.append("?", style=Style(color="cyan", bold=False))
    preamble.append("\n")
    preamble.append("info", style=Style(color="cyan", bold=True))
    preamble.append(" To exit: ", style=Style(color="white", bold=False))
    preamble.append("exit", style=Style(color="cyan", bold=False))
    preamble.append(", ", style=Style(color="white", bold=False))
    preamble.append("quit", style=Style(color="cyan", bold=False))

    return preamble


def _get_prompt() -> Text:
    """
    The prompt for the CLI client REPL.
    """
    global _url
    global _username

    prompt = Text("mdrfc", style=Style(color="cyan"))
    prompt = prompt.append("::", style=Style(color="white"))
    prompt = prompt.append(_username, style=Style(color="green", bold=True))
    prompt = prompt.append("@", style=Style(color="white", bold=True))
    prompt = prompt.append(_url, style=Style(color="green", bold=True))
    prompt = prompt.append("$ ", style=Style(color="white"))

    return prompt 


def _run_repl() -> None:
    """
    Enter the client REPL.
    """
    console = Console()
    console.print(_get_preamble())

    commands = {
        "ping": _cmd_ping,
        "login": _cmd_login,
        "logout": _cmd_logout,
        "whoami": _cmd_whoami,
        "rfc-list": _cmd_rfc_list,
        "rfc-get": _cmd_rfc_get,
        "rfc-post": _cmd_rfc_post,
        "comment-list": _cmd_comment_list,
        "comment-get": _cmd_comment_get,
        "comment-post": _cmd_comment_post,
    }

    running = True
    while running:
        user_input = Prompt.get_input(
            console=console,
            prompt=_get_prompt(),
            password=False
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
            except Exception as e:
                rprint(f"[bold red]error[/bold red] command failed: {e}")


def _validate_url(url: str) -> None:
    """
    Exit if the provided URL is not valid.
    """
    split = urlsplit(url)
    if split.netloc == "":
        print("error: invalid URL")
        exit(1)


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

    _run_repl()

    print(f"disconnected from {url}")