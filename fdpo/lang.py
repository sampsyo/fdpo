import lark
import enum
from dataclasses import dataclass

GRAMMAR = """
?start: prog

prog: decl* asgt*

asgt: ident "=" expr ";"
?expr: ident | call
call: ident "(" list{expr} ")"

decl: dir WS ident ":" width ";"
dir: "in" -> in | "out" -> out

?ident: CNAME
?width: INT

?list{item}: [item ("," item)* ","?]

%import common.WS
%import common.CNAME
%import common.INT

%ignore WS
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


@dataclass(frozen=True)
class Call:
    func: str
    args: list["Expression"]

    @classmethod
    def parse(cls, tree) -> "Call":
        assert tree.data == "call"
        func, args_tree = tree.children

        # We either have a list of arguments or a single argument. Maybe
        # this is fixable with a better grammar?
        if isinstance(args_tree, lark.Tree) and args_tree.data == "list":
            arg_trees = args_tree.children
        elif isinstance(args_tree, lark.Token):
            arg_trees = [args_tree]
        else:
            assert False

        return cls(
            str(func),
            [parse_expr(t) for t in arg_trees],
        )

    def pretty(self) -> str:
        args = ", ".join(a.pretty() for a in self.args)
        return f"{self.func}({args})"


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

    @classmethod
    def parse(cls, tree) -> "Program":
        assert tree.data == "prog"

        ports = []
        asgts = []
        for line in tree.children:
            match line.data:
                case "decl":
                    ports.append(Port.parse_decl(line))
                case "asgt":
                    asgts.append(Assignment.parse(line))
                case _:
                    assert False, f"unknown line {line.data}"

        return cls(
            {p.name: p for p in ports if p.direction == Direction.IN},
            {p.name: p for p in ports if p.direction == Direction.OUT},
            asgts,
        )

    def pretty(self) -> str:
        return "\n".join(
            [p.pretty() for p in self.inputs.values()]
            + [p.pretty() for p in self.outputs.values()]
            + [a.pretty() for a in self.assignments]
        )


def parse(program: str) -> Program:
    parser = lark.Lark(GRAMMAR, parser="earley")
    tree = parser.parse(program)
    return Program.parse(tree)
