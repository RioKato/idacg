from argparse import ArgumentParser
import csv
from pathlib import Path
import sys

from . import bridge
from . import lbug as _lbug


def dump(database: str, output: str):
    database = Path(database).resolve()
    database = str(database)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    with bridge.use_database(database):
        funcs, calls = bridge.dump()

    with open(output / "functions.csv", "w") as fd:
        writer = csv.writer(fd)
        writer.writerow(["id", "name", "file", "address", "export"])

        for func in funcs:
            writer.writerow([func.id, func.name, func.file, func.address, func.export])

    with open(output / "calls.csv", "w") as fd:
        writer = csv.writer(fd)
        writer.writerow(["caller", "callee"])

        for caller, callee in calls:
            writer.writerow([caller, callee])


def search(database: str, query: str):
    database = Path(database).resolve()
    database = str(database)

    writer = csv.writer(sys.stdout)
    init = True
    keys = []

    with bridge.use_database(database):
        for result in bridge.search(query):
            if init:
                init = False
                keys = result.keys()
                keys = list(keys)
                keys.remove("id")
                keys.insert(0, "id")
                writer.writerow(keys)

            values = [result[key] for key in keys]
            writer.writerow(values)


def lbug(input: str):
    print(_lbug.setup(input))


def main() -> None:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    dump_parser = subparsers.add_parser("dump")
    dump_parser.add_argument("database")
    dump_parser.add_argument("output")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("database")
    search_parser.add_argument("query")

    lbug_parser = subparsers.add_parser("lbug")
    lbug_parser.add_argument("input")

    args = parser.parse_args()

    match args.command:
        case "dump":
            dump(args.database, args.output)

        case "search":
            search(args.database, args.query)

        case "lbug":
            lbug(args.input)

        case _:
            parser.print_help()
