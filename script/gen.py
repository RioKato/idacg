from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent.parent

grammar = root / "grammar" / "query.lark"
output = root / "src" / "idacg" / "query.py"

with output.open("w") as f:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "lark.tools.standalone",
            str(grammar),
        ],
        stdout=f,
        check=True,
    )
