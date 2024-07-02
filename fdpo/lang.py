from typing import Optional
import lark
import enum
from dataclasses import dataclass

GRAMMAR = r"""
?start: prog

prog: decls asgts ["---" asgts]
decls: decl*
asgts: asgt*

asgt: ident "=" expr ";"
?expr: ident | call
call: ident "[" list{INT} "]" "(" list{expr} ")"

decl: dir WS ident ":" width ";"
dir: "in" -> in | "out" -> out

?ident: CNAME
?width: INT

?list{item}: [item ("," item)* ","?]

COMMENT: "#" /[^\n]*/ "\n"

%import common.WS
%import common.CNAME
%import common.INT

%ignore WS
%ignore COMMENT
"""


class Direction(enum.Enum):
    IN = 0
    OUT = 1

    @classmethod
    def parse(cls, tree) -> "Direction":
        match tree.data:
            case "in":
                return cls.IN
            case "out":
                return cls.OUT
            case _:
                assert False

    def __str__(self) -> str:
        match self:
            case self.IN:
                return "in"
            case self.OUT:
                return "out"
            case _:
                assert False


@dataclass(frozen=True)
class Port:
    name: str
    direction: Direction
    width: int

    @classmethod
    def parse_decl(cls, tree) -> "Port":
        dir_t, _, name, width = tree.children
        return cls(
            str(name),
            Direction.parse(dir_t),
            int(width),
        )

    def pretty(self) -> str:
        return f"{self.direction} {self.name}: {self.width};"


def _tree_list(tree) -> list:
    """Get the list of subtrees from a parse tree."""
    # We either have a list of subtrees, a single thing, or None if the
    # list is empty. Maybe this is fixable with a better grammar?
    if isinstance(tree, lark.Tree) and tree.data == "list":
        return tree.children
    elif isinstance(tree, lark.Token):
        return [tree]
    elif tree is None:
        return []
    else:
        assert False


@dataclass(frozen=True)
class Call:
    func: str
    params: list[int]
    inputs: list["Expression"]

    @classmethod
    def parse(cls, tree) -> "Call":
        assert tree.data == "call"
        func, params, inputs = tree.children
        return cls(
            str(func),
            [int(t) for t in _tree_list(params)],
            [parse_expr(t) for t in _tree_list(inputs)],
        )

    def pretty(self) -> str:
        params = ", ".join(str(p) for p in self.params)
        inputs = ", ".join(a.pretty() for a in self.inputs)
        return f"{self.func}[{params}]({inputs})"


@dataclass(frozen=True)
class Lookup:
    var: str

    def pretty(self) -> str:
        return self.var


Expression = Call | Lookup


def parse_expr(tree) -> Expression:
    if isinstance(tree, lark.Token):
        return Lookup(str(tree))
    elif tree.data == "call":
        return Call.parse(tree)
    else:
        assert False, "unknown expr type"


@dataclass(frozen=True)
class Assignment:
    dest: str
    expr: Expression

    @classmethod
    def parse(cls, tree) -> "Assignment":
        lhs, rhs = tree.children
        return cls(
            str(lhs),
            parse_expr(rhs),
        )

    def pretty(self) -> str:
        return f"{self.dest} = {self.expr.pretty()};"


@dataclass(frozen=True)
class Program:
    inputs: dict[str, Port]
    outputs: dict[str, Port]
    assignments: list[Assignment]

    @staticmethod
    def parse_decls(tree) -> tuple[dict[str, Port], dict[str, Port]]:
        ports = [Port.parse_decl(l) for l in tree.children]
        return (
            {p.name: p for p in ports if p.direction == Direction.IN},
            {p.name: p for p in ports if p.direction == Direction.OUT},
        )

    @staticmethod
    def parse_asgts(tree) -> list[Assignment]:
        return [Assignment.parse(l) for l in tree.children]

    @classmethod
    def parse(cls, tree) -> tuple["Program", Optional["Program"]]:
        assert tree.data == "prog"

        decls, asgts1, asgts2 = tree.children
        inputs, outputs = cls.parse_decls(decls)
        return (
            cls(inputs, outputs, cls.parse_asgts(asgts1)),
            cls(inputs, outputs, cls.parse_asgts(asgts2)) if asgts2 else None,
        )

    def pretty(self) -> str:
        return "\n".join(
            [p.pretty() for p in self.inputs.values()]
            + [p.pretty() for p in self.outputs.values()]
            + [a.pretty() for a in self.assignments]
        )


def parse(program: str) -> tuple[Program, Optional[Program]]:
    parser = lark.Lark(GRAMMAR, parser="earley")
    tree = parser.parse(program)
    return Program.parse(tree)
