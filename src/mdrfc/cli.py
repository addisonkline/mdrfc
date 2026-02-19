import argparse

from mdrfc.server import run_server
from mdrfc.setup.run_setup import run_setup_sync


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mdrfc",
        description="A server implementation for hosting Markdown-formatted RFCs",
        epilog="Copyright (c) 2026 Addison Kline (GitHub: @addisonkline)"
    )
    subparsers = parser.add_subparsers(description="subcommands")

    serve_parser = subparsers.add_parser(
        "serve",
        help="run an MDRFC server"
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

    setup_parser = subparsers.add_parser(
        "setup",
        help="initialize this environment for MDRFC"
    )
    setup_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print more detailed process information to the console"
    )
    setup_parser.set_defaults(func=run_setup_sync)
    
    args = parser.parse_args()

    args.func(args)

