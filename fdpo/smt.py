from . import lang
from pysmt.shortcuts import Symbol, Equals, And, to_smtlib
from pysmt.typing import BVType
from pysmt.fnode import FNode
from itertools import chain


def expr_to_smt(ports: dict[str, FNode], expr: lang.Expression):
    if isinstance(expr, lang.Lookup):
        return ports[expr.var]
    else:
        assert False, "working on it"


def to_formula(prog: lang.Program) -> FNode:
    ports = {
        port.name: Symbol(port.name, BVType(port.width))
        for port in chain(prog.inputs.values(), prog.outputs.values())
    }

    constraints = [
        Equals(ports[asgt.dest], expr_to_smt(ports, asgt.expr))
        for asgt in prog.assignments
    ]
    return And(*constraints)


def to_smt(prog: lang.Program) -> str:
    return to_smtlib(to_formula(prog))
