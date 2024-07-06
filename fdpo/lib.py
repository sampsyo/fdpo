from dataclasses import dataclass
from typing import Callable
from pysmt.fnode import FNode
from pysmt.shortcuts import BVAdd, BVSub, Ite, NotEquals, BV, BVUGT, BVULT


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


def cmp_sig(params: list[int]) -> Signature:
    return Signature([params[0], params[0]], 1)


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 1, binary_sig, lambda a: BVAdd(*a)),
        Function("sub", 1, binary_sig, lambda a: BVSub(*a)),
        Function(
            "if",
            1,
            lambda p: Signature([1, p[0], p[0]], p[0]),
            lambda a: Ite(NotEquals(a[0], BV(0, 1)), a[1], a[2]),
        ),
        Function(
            "gt", 1, cmp_sig, lambda a: Ite(BVUGT(*a), BV(1, 1), BV(0, 1))
        ),
        Function(
            "lt", 1, cmp_sig, lambda a: Ite(BVULT(*a), BV(1, 1), BV(0, 1))
        ),
    ]
}
