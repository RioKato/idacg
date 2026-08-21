from jinja2 import Environment, FileSystemLoader

import json
from pathlib import Path
import re
from typing import Any


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def cypher(value: Any) -> str:
    COMPAT = (bool, str, int, float)

    if value is None or isinstance(value, COMPAT):
        return json.dumps(value)

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
    environment = Environment(loader=FileSystemLoader(path.parent))

    for filter in FILTERS:
        environment.filters[filter.__name__] = filter

    template = environment.get_template(path.name)
    return template.render(**args)
