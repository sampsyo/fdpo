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
    def parse(cls, tree) -> 'Direction':
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
    def parse_decl(cls, tree) -> 'Port':
        dir_t, _, name, width = tree.children
        return cls(
            str(name),
            Direction.parse(dir_t),
            int(width),
        )

    def pretty(self) -> str:
        return f"{self.direction} {self.name} = {self.width};"


@dataclass(frozen=True)
class Call:
    func: str
    args: list['Expression']

    @classmethod
    def parse(cls, tree) -> 'Call':
        assert tree.data == "call"
        func, args_tree = tree.children
        assert args_tree.data == "list"
        return cls(
            str(func),
            [parse_expr(t) for t in args_tree.children],
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
    def parse(cls, tree) -> 'Assignment':
        lhs, rhs = tree.children
        return cls(
            str(lhs),
            parse_expr(rhs),
        )

    def pretty(self) -> str:
        return f"{self.dest} = {self.expr.pretty()};"


@dataclass(frozen=True)
class Program:
    inputs: list[Port]
    outputs: list[Port]
    assignments: list[Assignment]

    @classmethod
    def parse(cls, tree) -> 'Program':
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
            [p for p in ports if p.direction == Direction.IN],
            [p for p in ports if p.direction == Direction.OUT],
            asgts,
        )

    def pretty(self) -> str:
        return "\n".join(
            [p.pretty() for p in self.inputs] +
            [p.pretty() for p in self.outputs] +
            [a.pretty() for a in self.assignments]
        )



def fdpo():
    import sys
    parser = lark.Lark(GRAMMAR, parser='earley')
    src = sys.stdin.read()
    ast = parser.parse(src)
    prog = Program.parse(ast)
    print(prog.pretty())


if __name__ == "__main__":
    fdpo()
