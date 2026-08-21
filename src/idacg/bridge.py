import idapro

import idautils
import ida_auto
import ida_funcs
import ida_hexrays
import ida_nalt
import ida_xref

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from . import searcher


@contextmanager
def use_database(path: str):
    idapro.open_database(path, run_auto_analysis=True)

    try:
        ida_auto.auto_wait()
        yield
    finally:
        idapro.close_database()


class IDGenerator:
    def __init__(self):
        self.hash = ida_nalt.retrieve_input_file_sha256()
        self.base = ida_nalt.get_imagebase()

    def generate(self, ea: int):
        return (self.hash + (ea - self.base).to_bytes(length=8)).hex()


@dataclass
class Function:
    id: str
    name: str
    file: str
    address: int
    export: bool


def dump() -> Tuple[List[Function], Set[str]]:
    generator = IDGenerator()
    file = ida_nalt.get_root_filename()
    exports = {ea for _, _, ea, _ in idautils.Entries()}

    def create_func(ea):
        return Function(
            id=generator.generate(ea),
            name=ida_funcs.get_func_name(ea),
            file=file,
            address=ea,
            export=ea in exports,
        )

    funcs = {}
    calls = set()

    for callee in idautils.Functions():
        calleef = create_func(callee)
        funcs[calleef.id] = calleef

        for xref in idautils.XrefsTo(callee):
            if xref.type not in (ida_xref.fl_CF, ida_xref.fl_CN):
                continue

            caller = ida_funcs.get_func_start(xref.frm)

            if caller is None:
                continue

            callerf = create_func(caller)
            funcs[callerf.id] = callerf
            calls.add((callerf.id, calleef.id))

    return list(funcs.values()), calls


def search(dsl: str) -> Iterator[Dict[str, str | int | None]]:
    generator = IDGenerator()
    query = searcher.compile(dsl)

    for ea in idautils.Functions():
        try:
            source = ida_hexrays.decompile(ea)
        except ida_hexrays.DecompilationFailure:
            continue

        source = str(source)
        id = generator.generate(ea)

        for result in searcher.search(query, source):
            result["id"] = id
            yield result
