from argparse import Namespace

from mdrfc.utils.version import get_mdrfc_version


def print_version(args: Namespace) -> None:
    """
    Print the software version and exit.
    If verbose, include more detailed software info.
    """
    print(f"version: {get_mdrfc_version()}")

    if args.verbose:
        print()
        print("Basic Info:")
        print("  Name: mdrfc")
        print("  Description: A server for hosting Markdown-formatted RFC documents")
        print("  Repository: https://github.com/addisonkline/mdrfc")
        print("  License: MIT")
        print("  License file: `LICENSE` in the project root")
        print("Credits:")
        print("  Copyright (c) 2026 Addison Kline")
        print("  GitHub: @addisonkline")
        print("  Website: https://www.addisonkline.net")
        print("  Email: addison at addisonkline dot net")
