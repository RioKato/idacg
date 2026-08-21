from jinja2 import Environment, FileSystemLoader, PackageLoader

import json
from pathlib import Path
import re
from typing import Any


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def cypher(value: Any) -> str:
    COMPAT = (bool, str, int, float)

    if value is None or isinstance(value, COMPAT):
        return json.dumps(value, allow_nan=False)

    if isinstance(value, list):
        inner = (cypher(e) for e in value)
        return f"[{', '.join(inner)}]"

    if isinstance(value, dict):
        for k in value:
            if not (isinstance(k, str) and IDENTIFIER.fullmatch(k)):
                raise ValueError("invalid Cypher identifier")

        inner = (f"{k}: {cypher(v)}" for k, v in value.items())
        return f"{{{', '.join(inner)}}}"

    raise ValueError(f"unsupported Cypher value")


FILTERS = [cypher]


def render(path: str, **args) -> str:
    path = Path(path)

    if path.is_file():
        loader = FileSystemLoader(path.parent)
        name = path.name
    else:
        loader = PackageLoader(__package__, "templates")
        name = str(path)

        if not name.endswith(".j2"):
            name = f"{name}.j2"

    environment = Environment(loader=loader)

    for filter in FILTERS:
        environment.filters[filter.__name__] = filter

    template = environment.get_template(name)
    return template.render(**args)


def show() -> str:
    environment = Environment(loader=PackageLoader(__package__, "templates"))
    text = ""

    for name in environment.list_templates():
        source, _, _ = environment.loader.get_source(environment, name)
        text += f"# {name}\n\n```cypher\n{source.rstrip()}\n```\n\n"

    return text
