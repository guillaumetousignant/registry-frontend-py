#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
import os
from typing import Optional
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.traceback import install


class UnauthorizedException(Exception):
    "Raised when a request is rejected with an unauthorized code"
    pass


def get_password(input_password: Optional[str]) -> str:
    env_password = os.environ.get("ADMIN_PASSWORD")
    password = input_password if input_password is not None else env_password
    if password is None:
        raise RuntimeError(
            "Password is not defined anywhere. Either pass as argument, or set the ADMIN_PASSWORD environment variable"
        )
    return password


def get_token(url: str, password: str) -> str:
    request = requests.get(
        f"{url}/api/v1/authorize/admin", auth=("py_frontend", password)
    )
    if not request.ok:
        raise RuntimeError("Received error when asking for token")
    return request.text  # content is bytes, text is str


def view_items(url: str, token: str, console: Console):
    request = requests.get(
        f"{url}/api/v1/items", headers={"Authorization": f"Bearer {token}"}
    )

    if not request.ok:
        if request.status_code == 401:
            raise UnauthorizedException
        else:
            raise RuntimeError("Received error when asking for items")

    items = request.json()["data"]

    table = Table(title="Items")
    table.add_column("ID", style="bold yellow", no_wrap=True)
    table.add_column("Name", no_wrap=True)
    table.add_column("Colour", no_wrap=True)
    table.add_column("Link", style="cyan")
    table.add_column("Assigned", no_wrap=True)

    for item in items:
        table.add_row(
            str(item["id"]),
            item["name"],
            item["colour"],
            f'[link={item["link"]}]{item["link"]}[/link]',
            item["assigned"]
            if item["assigned"] is not None
            else "[bold reverse]unassigned[/bold reverse]",
        )

    console.print(table)


def add_item(
    url: str,
    token: str,
    console: Console,
    name: Optional[str],
    colour: Optional[str],
    link: Optional[str],
    assigned: Optional[str],
):
    if name is None:
        name = Prompt.ask("[yellow]Enter item name[/yellow]")
    if colour is None:
        colour = Prompt.ask("[yellow]Enter item colour[/yellow]")
    if link is None:
        link = Prompt.ask("[yellow]Enter item link[/yellow]")
    if assigned is None:
        assigned = Prompt.ask("[yellow]Enter item assigned[/yellow]", default=None)

    request = requests.post(
        f"{url}/api/v1/items/add",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "colour": colour,
            "link": link,
            "assigned": assigned,
        },
    )

    if not request.ok:
        if request.status_code == 401:
            raise UnauthorizedException
        else:
            raise RuntimeError("Received error when adding item")
    else:
        console.print("[green]Successfully added item[/green]")


def assign_item(
    url: str, token: str, console: Console, id: Optional[int], assigned: Optional[str]
):
    items_request = requests.get(
        f"{url}/api/v1/items", headers={"Authorization": f"Bearer {token}"}
    )
    ids = [str(item["id"]) for item in items_request.json()["data"]]

    if id is None:
        id = int(Prompt.ask("[yellow]Enter item id[/yellow]", choices=ids))
    if assigned is None:
        assigned = Prompt.ask(
            "[yellow]Enter item assigned, or leave empty for unassigned[/yellow]"
        )

    request = requests.post(
        f"{url}/api/v1/items/{id}/claim",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "assigned": assigned,
        },
    )

    if not request.ok:
        if request.status_code == 401:
            raise UnauthorizedException
        else:
            raise RuntimeError("Received error when claiming item")
    else:
        console.print("[green]Successfully claimed item[/green]")


def delete_item(url: str, token: str, console: Console, id: Optional[int]):
    items_request = requests.get(
        f"{url}/api/v1/items", headers={"Authorization": f"Bearer {token}"}
    )
    ids = [str(item["id"]) for item in items_request.json()["data"]]

    if id is None:
        id = int(Prompt.ask("[yellow]Enter item id[/yellow]", choices=ids))

    request = requests.post(
        f"{url}/api/v1/items/{id}/delete",
        headers={"Authorization": f"Bearer {token}"},
    )

    if not request.ok:
        if request.status_code == 401:
            raise UnauthorizedException
        else:
            raise RuntimeError("Received error when deleting item")
    else:
        console.print("[green]Successfully deleted item[/green]")


def unassign_item(url: str, token: str, console: Console, id: Optional[int]):
    items_request = requests.get(
        f"{url}/api/v1/items", headers={"Authorization": f"Bearer {token}"}
    )
    ids = [str(item["id"]) for item in items_request.json()["data"]]

    if id is None:
        id = int(Prompt.ask("[yellow]Enter item id[/yellow]", choices=ids))

    request = requests.post(
        f"{url}/api/v1/items/{id}/unclaim",
        headers={"Authorization": f"Bearer {token}"},
    )

    if not request.ok:
        if request.status_code == 401:
            raise UnauthorizedException
        else:
            raise RuntimeError("Received error when unassigning item")
    else:
        console.print("[green]Successfully unassigned item[/green]")


def view(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    view_items(url, token, console)


def add(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    add_item(url, token, console, args.name, args.colour, args.link, args.assigned)


def assign(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    assign_item(url, token, console, args.id, args.assigned)


def delete(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    delete_item(url, token, console, args.id)


def unassign(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    unassign_item(url, token, console, args.id)


def registry_frontend(url: str, token: str, console: Console, password: str):
    while True:
        try:
            console.print(
                "[bold]1. View\n2. Add\n3. Assign\n4. Delete\n5. Unassign\n6. Token\n7. Exit[/bold]"
            )
            action = Prompt.ask(
                "[yellow]Choose action[/yellow]",
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="1",
            )
            match action:
                case "1":
                    view_items(url, token, console)
                case "2":
                    add_item(url, token, console, None, None, None, None)
                case "3":
                    assign_item(url, token, console, None, None)
                case "4":
                    delete_item(url, token, console, None)
                case "5":
                    unassign_item(url, token, console, None)
                case "6":
                    token = get_token(url, password)
                    console.print("[green]Successfully refreshed token[/green]")
                case "7":
                    break
                case _:
                    pass
            console.print("")
        except UnauthorizedException:
            console.print("[red]Token expired, try again[/red]")
            token = get_token(url, password)


def registry_frontend_interactive(args: argparse.Namespace, console: Console):
    password = get_password(args.password)
    url = args.url
    token = get_token(url, password)
    registry_frontend(url, token, console, password)


def main(argv: list[str]):
    install(show_locals=True)

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
    parser.set_defaults(func=registry_frontend_interactive)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="choose one of these commands to send to the server",
    )
    view_subparser = subparsers.add_parser("view")
    view_subparser.set_defaults(func=view)
    add_subparser = subparsers.add_parser("add")
    add_subparser.add_argument(
        "-n",
        "--name",
        type=str,
        help="item name",
    )
    add_subparser.add_argument(
        "-c",
        "--colour",
        type=str,
        help="item colour",
    )
    add_subparser.add_argument(
        "-l",
        "--link",
        type=str,
        help="item link",
    )
    add_subparser.add_argument(
        "-a",
        "--assigned",
        type=str,
        help="item assigned",
    )
    add_subparser.set_defaults(func=add)
    assign_subparser = subparsers.add_parser("assign")
    assign_subparser.add_argument(
        "-i",
        "--id",
        type=int,
        help="item id",
    )
    assign_subparser.add_argument(
        "-a",
        "--assigned",
        type=str,
        help="item assigned",
    )
    assign_subparser.set_defaults(func=assign)
    delete_subparser = subparsers.add_parser("delete")
    delete_subparser.add_argument(
        "-i",
        "--id",
        type=int,
        help="item id",
    )
    delete_subparser.set_defaults(func=delete)
    unassign_subparser = subparsers.add_parser("unassign")
    unassign_subparser.add_argument(
        "-i",
        "--id",
        type=int,
        help="item id",
    )
    unassign_subparser.set_defaults(func=unassign)

    args = parser.parse_args(argv)

    load_dotenv()
    console = Console()

    try:
        args.func(args, console)
    except KeyboardInterrupt:
        console.print("[blue]Received keyboard interrupt[/blue]")
        return


if __name__ == "__main__":
    main(sys.argv[1:])
