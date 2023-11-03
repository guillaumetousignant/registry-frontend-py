#!/usr/bin/env python3

import sys
import argparse


def registry_frontend_py(input: float, output: int, optional: bool):
    print("Hello World!")
    print(f"Input: {input}, output: {output}, optional: {optional}")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog="Registry Frontend Python",
        description="Terminal frontend for the registry, written in python.",
    )
    parser.add_argument("-i", "--input", type=float, default=0.0, help="input float")
    parser.add_argument("-o", "--output", type=int, default=0, help="output int")
    parser.add_argument(
        "-p",
        "--optional",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="optional",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    registry_frontend_py(args.input, args.output, args.optional)


if __name__ == "__main__":
    main(sys.argv[1:])
