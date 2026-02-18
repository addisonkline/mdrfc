import argparse

from mdrfc.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mdrfc",
        description="A server implementation for hosting Markdown-formatted RFCs",
        epilog="Copyright (c) 2026 Addison Kline (GitHub: @addisonkline)"
    )
    subparsers = parser.add_subparsers(description="subcommands")

    serve_parser = subparsers.add_parser(
        "serve",
        help="run an mdcli server"
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
    serve_parser.set_defaults(func=run_server)
    
    args = parser.parse_args()

    args.func(args)

