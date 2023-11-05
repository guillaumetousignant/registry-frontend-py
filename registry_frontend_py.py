#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
import os
from typing import Optional


def get_password(input_password: Optional[str]) -> str:
    env_password = os.environ.get("ADMIN_PASSWORD")
    password = input_password if input_password is not None else env_password
    if password is None:
        raise RuntimeError(
            "Password is not defined anywhere. Either pass as argument, or set the ADMIN_PASSWORD environment variable"
        )
    return password


def view_items(password: str):
    pass


def view(args: argparse.Namespace):
    password = get_password(args.password)
    url = args.url
    print("view")
    print(args)


def add(args: argparse.Namespace):
    print("add")
    print(args)


def assign(args: argparse.Namespace):
    print("assign")
    print(args)


def delete(args: argparse.Namespace):
    print("delete")
    print(args)


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog="Registry Frontend Python",
        description="Terminal frontend for the registry, written in python.",
    )
    parser.add_argument(
        "-p", "--password", type=Path, help="password to use to get token from server"
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default="api.arietguillaume.ca",
        help="server url to use",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="choose one of these commands to send to the server",
        required=True,
    )
    view_subparser = subparsers.add_parser("view")
    view_subparser.set_defaults(func=view)
    add_subparser = subparsers.add_parser("add")
    add_subparser.set_defaults(func=add)
    assign_subparser = subparsers.add_parser("assign")
    assign_subparser.set_defaults(func=assign)
    delete_subparser = subparsers.add_parser("delete")
    delete_subparser.set_defaults(func=delete)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
