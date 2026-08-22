import json
from typing import Any, Iterator, TextIO


def reader(fd: TextIO) -> Iterator[Any]:
    for line in fd:
        line = line.strip()

        if not line:
            continue

        yield json.loads(line)


def write(fd: TextIO, obj: Any):
    line = f"{json.dumps(obj)}\n"
    fd.write(line)
