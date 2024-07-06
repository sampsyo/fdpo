from dataclasses import dataclass
from typing import Callable
from pysmt.fnode import FNode
from pysmt.shortcuts import (
    BVAdd,
    BVSub,
    BVMul,
    BVUDiv,
    BVURem,
    Ite,
    NotEquals,
    BV,
    BVUGT,
    BVULT,
    BVLShl,
    BVLShr,
    BVAShr,
    BVAnd,
    BVOr,
    BVXor,
    BVSExt,
    BVZExt,
    BVExtract,
)


@dataclass(frozen=True)
class Signature:
    inputs: list[int]
    output: int


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    sig: Callable[[list[int]], Signature]
    smt: Callable[[list[int], list[FNode]], FNode]


def binary_sig(params: list[int]) -> Signature:
    return Signature([params[0], params[0]], params[0])


def cmp_sig(params: list[int]) -> Signature:
    return Signature([params[0], params[0]], 1)


def ext_sig(params: list[int]) -> Signature:
    return Signature([params[0]], params[1])


def slice_sig(params: list[int]) -> Signature:
    """The signature for slicing/extracting a range of bits."""
    in_width, lo, hi = params
    return Signature([in_width], hi - lo + 1)


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 1, binary_sig, lambda _, a: BVAdd(*a)),
        Function("sub", 1, binary_sig, lambda _, a: BVSub(*a)),
        Function("mul", 1, binary_sig, lambda _, a: BVMul(*a)),
        Function("div", 1, binary_sig, lambda _, a: BVUDiv(*a)),
        Function("mod", 1, binary_sig, lambda _, a: BVURem(*a)),
        Function(
            "if",
            1,
            lambda p: Signature([1, p[0], p[0]], p[0]),
            lambda _, a: Ite(NotEquals(a[0], BV(0, 1)), a[1], a[2]),
        ),
        Function(
            "gt", 1, cmp_sig, lambda _, a: Ite(BVUGT(*a), BV(1, 1), BV(0, 1))
        ),
        Function(
            "lt", 1, cmp_sig, lambda _, a: Ite(BVULT(*a), BV(1, 1), BV(0, 1))
        ),
        Function("shl", 1, binary_sig, lambda _, a: BVLShl(*a)),
        Function("shr", 1, binary_sig, lambda _, a: BVLShr(*a)),
        Function("ashr", 1, binary_sig, lambda _, a: BVAShr(*a)),
        Function("and", 1, binary_sig, lambda _, a: BVAnd(*a)),
        Function("or", 1, binary_sig, lambda _, a: BVOr(*a)),
        Function("xor", 1, binary_sig, lambda _, a: BVXor(*a)),
        Function("sext", 2, ext_sig, lambda p, a: BVSExt(a[0], p[1] - p[0])),
        Function("zext", 2, ext_sig, lambda p, a: BVZExt(a[0], p[1] - p[0])),
        Function(
            "slice", 3, slice_sig, lambda p, a: BVExtract(a[0], p[1], p[2])
        ),
    ]
}
