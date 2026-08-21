from pathlib import Path
from shlex import quote


def setup(path: str) -> str:
    path = Path(path)
    copies = ""

    for csv in path.rglob("functions.csv"):
        copies += f"COPY Function FROM '{quote(str(csv))}' (header=True);\n"

    for csv in path.rglob("calls.csv"):
        copies += f"COPY Call FROM '{quote(str(csv))}' (header=True);\n"

    return f"""
CREATE NODE TABLE IF NOT EXISTS Function (
    id STRING PRIMARY KEY,
    name STRING,
    file STRING,
    address UINT64,
    is_export BOOLEAN
);

CREATE REL TABLE IF NOT EXISTS Call (
    FROM Function TO Function
);

CREATE REL TABLE IF NOT EXISTS Resolve (
    FROM Function TO Function
);

{copies}

MATCH (import:Function), (export:Function)
WHERE export.is_export = true
AND import.name STARTS WITH '.'
AND SUBSTRING(import.name, 2, SIZE(import.name) - 1) = export.name
CREATE (import) -[:Resolve]-> (export);
"""
