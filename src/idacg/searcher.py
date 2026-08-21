from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_c

import json

from .query import Lark_StandAlone, Transformer

CLANG = Language(tree_sitter_c.language())


class ToTreeSitterQuery(Transformer):
    def start(self, items):
        return items[0]

    def capture(self, items):
        name = str(items[0])[1:]
        return f"(_) @{name}"

    def wildcard(self, _):
        return "(_)"

    def string_literal(self, items):
        value = json.dumps(str(items[0]))
        return f"(string_literal) @__str (#eq? @__str {value})"

    def number_literal(self, items):
        value = str(items[0])
        return f'(number_literal) @__num (#eq? @__num "{value}")'

    def args(self, items):
        return list(items)

    def call(self, items):
        name = str(items[0])
        args = items[1] if len(items) > 1 else []
        args_query = " ".join(args)
        return f'(call_expression function: (identifier) @__func arguments: (argument_list {args_query}) (#eq? @__func "{name}"))'


def compile(dsl: str) -> Query:
    parser = Lark_StandAlone(transformer=ToTreeSitterQuery())
    tql = parser.parse(dsl)
    return Query(CLANG, tql)


def search(query: Query, source: str) -> Iterator[dict[str, str | int | None]]:
    parser = Parser(CLANG)
    tree = parser.parse(source.encode())
    cursor = QueryCursor(query)
    keys = [query.capture_name(i) for i in range(query.capture_count)]
    keys = [key for key in keys if not key.startswith("__")]

    for _, captures in cursor.matches(tree.root_node):
        result = {key: None for key in keys}

        for name, nodes in captures.items():
            for node in nodes:
                if name in keys:
                    match node.type:
                        case "string_literal":
                            text = source[node.start_byte : node.end_byte]
                            result[name] = json.loads(text)
                        case "number_literal":
                            text = source[node.start_byte : node.end_byte]
                            result[name] = int(text, 0)

        yield result
