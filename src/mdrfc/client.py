from argparse import ArgumentParser, Namespace
import json
import os
from urllib.parse import urlsplit

import httpx
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.style import Style

import mdrfc.responses as res_types
from mdrfc.backend.auth import Token, User
from mdrfc.utils.version import get_mdrfc_version


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
    usage="login <username> <password> [option]...",
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
    "password",
    help="associated password"
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
    
    global _url
    username = args.username
    password = args.password

    body = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": username,
        "client_secret": password
    }

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
        "whoami": _cmd_whoami,
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
                args = parser.parse_args(user_input.split())
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