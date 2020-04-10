"""Define a command-line interface for the isup module.

Call parse_args() to return an argument parser namespace
"""
import argparse


def parse_args() -> argparse.Namespace:
    """Define an argument parser and return the parsed arguments."""
    parser = argparse.ArgumentParser(
        prog="cmslogin",
        description="log in to cms vpn using 1password credentials",
    )
    parser.add_argument(
        "path",
        type=str,
        metavar="PATH",
        default="./",
        help="path to the run-cms script in the filesystem"
    )

    return parser.parse_args()
