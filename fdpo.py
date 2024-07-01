import lark
import enum
from dataclasses import dataclass

GRAMMAR = """
?start: prog

prog: decl* asgt*

asgt: ident "=" expr ";"
?expr: ident

decl: dir WS ident ":" width ";"
dir: "in" -> in | "out" -> out

?ident: CNAME
?width: INT

%import common.WS
%import common.CNAME
%import common.INT

%ignore WS
"""

class Direction(enum.Enum):
    IN = 0
    OUT = 1

    @classmethod
    def parse(cls, tree):
        match tree.data:
            case "in":
                return cls.IN
            case "out":
                return cls.OUT
            case _:
                return False


@dataclass(frozen=True)
class Port:
    name: str
    direction: Direction
    width: int

    @classmethod
    def parse_decl(cls, tree):
        dir_t, _, name, width = tree.children
        return cls(
            str(name),
            Direction.parse(dir_t),
            int(width),
        )


@dataclass(frozen=True)
class Assignment:
    dest: str
    src: str

    @classmethod
    def parse(cls, tree):
        lhs, rhs = tree.children
        return cls(
            str(lhs),
            str(rhs),
        )


@dataclass(frozen=True)
class Program:
    inputs: list[Port]
    outputs: list[Port]
    assignments: list[Assignment]

    @classmethod
    def parse(cls, tree):
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



def fdpo():
    parser = lark.Lark(GRAMMAR, parser='earley')
    ast = parser.parse('in x: 32; in y: 32; out z: 10; x = y; z = j;')
    prog = Program.parse(ast)
    print(prog)


if __name__ == "__main__":
    fdpo()
