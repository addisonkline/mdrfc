from argparse import ArgumentParser, Namespace
import json
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.style import Style

import mdrfc.responses as res_types
from mdrfc.utils.version import get_mdrfc_version


_url: str = None # type: ignore
_username: str = "{unknown}"


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
    add_help=False
)
subparsers = parser.add_subparsers(title="commands", dest="command")

# ping the server
ping_desc = "Ping the remote server"
ping_p = subparsers.add_parser(
    "ping",
    help=ping_desc,
    description=ping_desc
)
ping_p.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="include more detailed server info"
)

# command handlers
def cmd_ping(args: Namespace) -> None:
    """
    Ping the remote MDRFC server.
    """
    global _url
    response = httpx.get(
        _url,
        headers={"User-Agent": _get_user_agent()}
    )

    if response.status_code != 200:
        rprint(f"[bold red]error[/bold red] request failed with status code [red]{response.status_code}[/red]")
        return
    
    response_json = response.json()
    response_json_str = json.dumps(response_json)
    try:
        response_obj = res_types.GetRootResponse.model_validate_json(response_json_str)
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
        "ping": cmd_ping
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
            args = parser.parse_args(user_input.split())
            handler = commands.get(args.command)
            if handler:
                handler(args)
            else:
                parser.print_usage()
                print("for help, run `help`, `?`")


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