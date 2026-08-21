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
            jsonl = json.dumps(asdict(func))
            fd.write(jsonl + "\n")

    with open(f"{output}.call.jsonl", "w") as fd:
        for src, dst in calls:
            jsonl = json.dumps(dict(src=src, dst=dst))
            fd.write(jsonl + "\n")


def search(database: str, query: str):
    database = Path(database).resolve()
    database = str(database)

    with bridge.use_database(database):
        for result in bridge.search(query):
            jsonl = json.dumps(result)
            print(jsonl)


def render(template: str):
    cypher = renderer.render(template)
    print(cypher)


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

    args = parser.parse_args()

    match args.command:
        case "dump":
            dump(args.database, args.output)

        case "search":
            search(args.database, args.query)

        case "render":
            render(args.template)

        case _:
            parser.print_help()
