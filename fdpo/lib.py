from dataclasses import dataclass
from typing import Callable
from pysmt.fnode import FNode
from pysmt.shortcuts import BVAdd, BVSub, Ite, Equals, BV


@dataclass(frozen=True)
class Signature:
    inputs: list[int]
    output: int


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    sig: Callable[[list[int]], Signature]
    smt: Callable[[list[FNode]], FNode]


def binary_sig(params: list[int]) -> Signature:
    return Signature([params[0], params[0]], params[0])


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 1, binary_sig, lambda a: BVAdd(*a)),
        Function("sub", 1, binary_sig, lambda a: BVSub(*a)),
        Function(
            "mux",
            1,
            lambda p: Signature([1, p[0], p[0]], p[0]),
            lambda a: Ite(Equals(a[0], BV(0, 1)), a[1], a[2]),
        ),
    ]
}
