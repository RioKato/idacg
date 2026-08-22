from argparse import ArgumentParser
from dataclasses import asdict
import json
from pathlib import Path

from . import bridge, renderer


def dump(database: str, output: str):
    database = Path(database).resolve()
    database = str(database)

    with bridge.use_database(database):
        funcs, calls = bridge.dump()

    with open(f"{output}.func.jsonl", "w") as fd:
        for func in funcs:
            line = json.dumps(asdict(func))
            fd.write(f"{line}\n")

    with open(f"{output}.call.jsonl", "w") as fd:
        for src, dst in calls:
            line = json.dumps(dict(src=src, dst=dst))
            fd.write(f"{line}\n")


def search(database: str, query: str):
    database = Path(database).resolve()
    database = str(database)

    with bridge.use_database(database):
        for result in bridge.search(query):
            line = json.dumps(result)
            print(line)


def render(template: str, vars: list[str]):
    args = {}

    for var in vars:
        name, sep, value = var.partition("=")

        if not sep:
            raise ValueError(f"expected name=value")

        if value.startswith("@"):
            obj = []

            with open(value[1:]) as fd:
                for line in fd:
                    line = line.strip()

                    if not line:
                        continue

                    obj.append(json.loads(line))
        else:
            obj = json.loads(value)

        args[name] = obj

    cypher = renderer.render(template, **args)
    print(cypher)


def show():
    print(renderer.show())


def main() -> None:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    dump_parser = subparsers.add_parser("dump")
    dump_parser.add_argument("database")
    dump_parser.add_argument("output")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("database")
    search_parser.add_argument("query")

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("template")
    render_parser.add_argument("vars", nargs="*")

    subparsers.add_parser("show")

    args = parser.parse_args()

    match args.command:
        case "dump":
            dump(args.database, args.output)

        case "search":
            search(args.database, args.query)

        case "render":
            render(args.template, args.vars)

        case "show":
            show()

        case _:
            parser.print_help()
