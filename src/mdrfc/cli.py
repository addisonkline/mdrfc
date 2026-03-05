import argparse

from mdrfc.client import run_client
from mdrfc.server import run_server
from mdrfc.setup.run_setup import run_setup_sync


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mdrfc",
        usage="mdrfc [-h] <command>",
        description="A server implementation for hosting Markdown-formatted RFCs",
        epilog="Copyright (c) 2026 Addison Kline (GitHub: @addisonkline)"
    )
    subparsers = parser.add_subparsers(title="commands")

    # set up this environment
    setup_desc = "initialize this environment for MDRFC"
    setup_parser = subparsers.add_parser(
        "setup",
        usage="mdrfc setup [option]...",
        description=setup_desc,
        help=setup_desc
    )
    setup_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print more detailed process information to the console"
    )
    setup_parser.set_defaults(func=run_setup_sync)

    # spin up server
    serve_desc = "run an MDRFC server"
    serve_parser = subparsers.add_parser(
        "serve",
        usage="mdrfc serve [option]...",
        description=serve_desc,
        help=serve_desc
    )
    serve_parser.add_argument(
        "-H",
        "--host",
        default="127.0.0.1",
        help="the host to serve on (default: '127.0.0.1')"
    )
    serve_parser.add_argument(
        "-p",
        "--port",
        default=8026,
        type=int,
        help="the port to serve on (default: 8026)"
    )
    serve_parser.add_argument(
        "-r",
        "--reload",
        action="store_true",
        help="reload the server upon detected code changes"
    )
    serve_parser.add_argument(
        "-lf",
        "--log-file",
        default="mdrfc.log",
        help="the file path to write logs to (default: 'mdrfc.log')"
    )
    serve_parser.add_argument(
        "-llf",
        "--log-level-file",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="the minimum log level to write to the log file (default: 'INFO')"
    )
    serve_parser.add_argument(
        "-llc",
        "--log-level-console",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="the minimum log level to write to the console (default: 'INFO')"
    )
    serve_parser.set_defaults(func=run_server)

    # launch CLI client
    client_desc = "connect to a remote server with a CLI client"
    client_parser = subparsers.add_parser(
        "client",
        usage="mdrfc client <url> [option]...",
        description=client_desc,
        help=client_desc,
    )
    client_parser.add_argument(
        "url",
        help="the MDRFC server URL to connect to"
    )
    client_parser.set_defaults(func=run_client)
    
    args = parser.parse_args()

    try:
        args.func(args)
        exit(0)
    except AttributeError:
        parser.print_usage()
        print("try `mdrfc --help` for help")
        exit(1)
