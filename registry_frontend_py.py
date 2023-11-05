#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
import os
from typing import Optional
import requests
from dotenv import load_dotenv


def get_password(input_password: Optional[str]) -> str:
    env_password = os.environ.get("ADMIN_PASSWORD")
    password = input_password if input_password is not None else env_password
    if password is None:
        raise RuntimeError(
            "Password is not defined anywhere. Either pass as argument, or set the ADMIN_PASSWORD environment variable"
        )
    return password


def get_token(url: str, password: str) -> bytes:
    r = requests.get(url + "/api/v1/authorize/admin", auth=("py_frontend", password))
    if not r.ok:
        raise RuntimeError("Received error when asking for token")
    return r.content  # This is bytes, text is str


def view_items(url: str, password: str):
    token = get_token(url, password)


def add_item(url: str, password: str):
    token = get_token(url, password)


def assign_item(url: str, password: str):
    token = get_token(url, password)


def delete_item(url: str, password: str):
    token = get_token(url, password)


def view(args: argparse.Namespace):
    password = get_password(args.password)
    url = args.url
    view_items(url, password)


def add(args: argparse.Namespace):
    password = get_password(args.password)
    url = args.url
    add_item(url, password)


def assign(args: argparse.Namespace):
    password = get_password(args.password)
    url = args.url
    assign_item(url, password)


def delete(args: argparse.Namespace):
    password = get_password(args.password)
    url = args.url
    delete_item(url, password)


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
        default="https://api.arietguillaume.ca",
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

    load_dotenv()

    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
