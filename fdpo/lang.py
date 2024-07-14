from typing import Optional, assert_never
import lark
import enum
import dataclasses
from dataclasses import dataclass

GRAMMAR = r"""
prog: decls asgts ["---" asgts]
decls: decl*
asgts: asgt*

asgt: ident [":" width] "=" expr ";"
?expr: ident | call | lit
call: ident "[" list{INT} "]" "(" list{expr} ")"

decl: dir WS ident ":" width ";"
dir: "in" -> in | "out" -> out

# Integer literals.
lit: dlit | xlit | blit | rawlit
dlit: /[0-9]+/ "d" /[0-9]+/
xlit: /[0-9]+/ "x" /[0-9A-Fa-f]+/
blit: /[0-9]+/ "b" /[01]+/
rawlit: INT

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
                assert_never(self)


@dataclass(frozen=True)
class Port:
    name: str
    width: int

    @classmethod
    def parse_decl(cls, tree) -> tuple["Port", Direction]:
        dir_t, _, name, width = tree.children
        return (
            cls(
                str(name),
                int(width),
            ),
            Direction.parse(dir_t),
        )

    def pretty(self, direction) -> str:
        return f"{direction} {self.name}: {self.width};"


def _tree_list(tree) -> list:
    """Get the list of subtrees from a parse tree."""
    # We either have a list of subtrees, a single thing, or None if the
    # list is empty. Maybe this is fixable with a better grammar?
    if isinstance(tree, lark.Tree) and tree.data == "list":
        return tree.children
    elif tree is None:
        return []
    else:
        return [tree]


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


@dataclass(frozen=True)
class Literal:
    width: int
    base: int  # 2, 10, or 16
    value: int

    def pretty(self) -> str:
        match self.base:
            case 2:
                base_str = "b"
                val_str = f"{self.value:b}"
            case 10:
                base_str = "d"
                val_str = f"{self.value:d}"
            case 16:
                base_str = "x"
                val_str = f"{self.value:x}"
            case _:
                assert False
        return f"{self.width}{base_str}{val_str}"

    @classmethod
    def parse(cls, tree) -> "Literal":
        if tree.data == "rawlit":
            raise RawLiteralError(tree)
        width_tree, value_tree = tree.children
        width = int(width_tree)
        base = {"blit": 2, "dlit": 10, "xlit": 16}[tree.data]
        value = int(value_tree, base)
        return cls(width, base, value)


Expression = Call | Lookup | Literal


def parse_expr(tree) -> Expression:
    if isinstance(tree, lark.Token):
        return Lookup(str(tree))
    elif tree.data == "call":
        return Call.parse(tree)
    elif tree.data == "lit":
        return Literal.parse(tree.children[0])
    else:
        assert False, "unknown expr type"


@dataclass(frozen=True)
class Assignment:
    dest: str
    width: Optional[int]  # For temporaries, not outputs.
    expr: Expression

    @classmethod
    def parse(cls, tree) -> "Assignment":
        lhs, width, rhs = tree.children
        return cls(
            str(lhs),
            int(width) if width is not None else None,
            parse_expr(rhs),
        )

    def pretty(self) -> str:
        wann = f": {self.width}" if self.width is not None else ""
        return f"{self.dest}{wann} = {self.expr.pretty()};"


@dataclass(frozen=True)
class Program:
    inputs: dict[str, Port]
    outputs: dict[str, Port]
    assignments: list[Assignment]
    temps: dict[str, Port] = dataclasses.field(init=False)

    def __post_init__(self):
        temps = {
            a.dest: Port(a.dest, a.width)
            for a in self.assignments
            if a.dest not in self.outputs and a.width is not None
        }
        object.__setattr__(self, "temps", temps)

    @staticmethod
    def parse_decls(tree) -> tuple[dict[str, Port], dict[str, Port]]:
        decls = [Port.parse_decl(d) for d in tree.children]
        return (
            {p.name: p for (p, d) in decls if d == Direction.IN},
            {p.name: p for (p, d) in decls if d == Direction.OUT},
        )

    @staticmethod
    def parse_asgts(tree) -> list[Assignment]:
        return [Assignment.parse(a) for a in tree.children]

    @classmethod
    def parse(cls, tree) -> tuple["Program", Optional["Program"]]:
        assert tree.data == "prog"

        decls, asgts1, asgts2 = tree.children
        inputs, outputs = cls.parse_decls(decls)
        return (
            cls(inputs, outputs, cls.parse_asgts(asgts1)),
            cls(inputs, outputs, cls.parse_asgts(asgts2)) if asgts2 else None,
        )

    def pretty_sig(self) -> str:
        return "\n".join(
            [p.pretty(Direction.IN) for p in self.inputs.values()]
            + [p.pretty(Direction.OUT) for p in self.outputs.values()]
        )

    def pretty(self) -> str:
        return "\n".join(
            [self.pretty_sig()] + [a.pretty() for a in self.assignments]
        )


class ParseError(Exception):
    pass


class TreeError(ParseError):
    def __init__(self, tree: lark.Tree, message: str):
        row = tree.meta.line
        col = tree.meta.column
        super().__init__(f"{row}:{col}: {message}")


class RawLiteralError(TreeError):
    def __init__(self, tree: lark.Tree):
        val = str(tree.children[0])
        msg = (
            f"The plain integer {val} is not allowed. All literals must be "
            f"written as <width><base><value>, where <width> is the bit width, "
            f"<base> is b, d, or x for binary, decimal, or hexadecimal, and "
            f"<value> is the integer written in that base. For example, try "
            f"32d{val} for a 32-bit decimal."
        )
        super().__init__(tree, msg)


def parse(program: str) -> tuple[Program, Optional[Program]]:
    parser = lark.Lark(
        GRAMMAR, parser="earley", start="prog", propagate_positions=True
    )
    try:
        tree = parser.parse(program)
    except lark.exceptions.UnexpectedInput as e:
        raise ParseError(str(e))
    return Program.parse(tree)
