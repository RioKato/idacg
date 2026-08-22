from argparse import ArgumentParser
from dataclasses import asdict
from glob import iglob
from importlib.resources import files
import json
from pathlib import Path
import sys

try:
    from . import bridge
except ImportError:
    bridge = None

from . import jsonl, renderer, searcher


def init():
    dst = Path("justfile")

    if dst.exists():
        raise FileExistsError(dst)

    src = files("idacg").joinpath("resources/justfile")
    dst.write_text(src.read_text())


def dump(database: str, output: str):
    database = Path(database).resolve()
    database = str(database)

    with bridge.use_database(database):
        funcs, calls = bridge.dump()

    with open(f"{output}.func.jsonl", "w") as fd:
        for func in funcs:
            jsonl.write(fd, asdict(func))

    with open(f"{output}.call.jsonl", "w") as fd:
        for src, dst in calls:
            jsonl.write(fd, dict(src=src, dst=dst))


def type_(database: str, til: str):
    database = Path(database).resolve()
    database = str(database)
    til = Path(til).resolve()
    til = str(til)

    with bridge.use_database(database):
        bridge.apply_til(til)


def search(query: str, paths: str):
    query = searcher.compile(query)

    for path in iglob(paths, recursive=True):
        with open(path) as fd:
            for obj in jsonl.reader(fd):
                if "code" not in obj:
                    raise ValueError("missing code")

                if obj["code"] is None:
                    continue

                for result in searcher.search(query, obj["code"]):
                    for k, v in result.items():
                        obj[k] = v

                    jsonl.write(sys.stdout, obj)


def render(template: str, vars: list[str]):
    args = {}

    for var in vars:
        name, sep, value = var.partition("=")

        if not sep:
            raise ValueError(f"expected name=value")

        if value.startswith("@"):
            obj = []

            for path in iglob(value[1:], recursive=True):
                with open(path) as fd:
                    for e in jsonl.reader(fd):
                        obj.append(e)
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

    subparsers.add_parser("init")

    if bridge:
        dump_parser = subparsers.add_parser("dump")
        dump_parser.add_argument("database")
        dump_parser.add_argument("output")

        type_parser = subparsers.add_parser("type")
        type_parser.add_argument("database")
        type_parser.add_argument("til")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("paths")
    search_parser.add_argument("query")

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("template")
    render_parser.add_argument("vars", nargs="*")

    subparsers.add_parser("show")

    args = parser.parse_args()

    match args.command:
        case "init":
            init()

        case "dump":
            dump(args.database, args.output)

        case "type":
            type_(args.database, args.til)

        case "search":
            search(args.query, args.paths)

        case "render":
            render(args.template, args.vars)

        case "show":
            show()

        case _:
            parser.print_help()
