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
    help: str


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
        Function(
            "add",
            1,
            binary_sig,
            lambda _, a: BVAdd(*a),
            "add[N](x: N, y: N) -> N: Integer addition.",
        ),
        Function(
            "sub",
            1,
            binary_sig,
            lambda _, a: BVSub(*a),
            "sub[N](x: N, y: N) -> N: Integer subtraction.",
        ),
        Function(
            "mul",
            1,
            binary_sig,
            lambda _, a: BVMul(*a),
            "mul[N](x: N, y: N) -> N: Unsigned integer multiplication.",
        ),
        Function(
            "div",
            1,
            binary_sig,
            lambda _, a: BVUDiv(*a),
            "div[N](x: N, y: N) -> N: Unsigned integer (rounded) division.",
        ),
        Function(
            "mod",
            1,
            binary_sig,
            lambda _, a: BVURem(*a),
            "mod[N](x: N, y: N) -> N: Unsigned integer modulus (remainder).",
        ),
        Function(
            "if",
            1,
            lambda p: Signature([1, p[0], p[0]], p[0]),
            lambda _, a: Ite(NotEquals(a[0], BV(0, 1)), a[1], a[2]),
            "if[N](c: 1, a: N, b: N) -> N: If `c` is 1, then `a`. Otherwise, `b`.",
        ),
        Function(
            "gt",
            1,
            cmp_sig,
            lambda _, a: Ite(BVUGT(*a), BV(1, 1), BV(0, 1)),
            "gt[N](x: N, y: N) -> 1: Unsigned integer greater-than comparison.",
        ),
        Function(
            "lt",
            1,
            cmp_sig,
            lambda _, a: Ite(BVULT(*a), BV(1, 1), BV(0, 1)),
            "lt[N](x: N, y: N) -> 1: Unsigned integer less-than comparison.",
        ),
        Function(
            "shl",
            1,
            binary_sig,
            lambda _, a: BVLShl(*a),
            "shl[N](x: N, d: N) -> N: Shift `x` left by `d` bits.",
        ),
        Function(
            "shr",
            1,
            binary_sig,
            lambda _, a: BVLShr(*a),
            "shr[N](x: N, d: N) -> N: Shift `x` right by `d` bits (logical, zero padded).",
        ),
        Function(
            "ashr",
            1,
            binary_sig,
            lambda _, a: BVAShr(*a),
            "ashr[N](x: N, d: N) -> N: Shift `x` right by `d` bits (arithmetic, sign extended).",
        ),
        Function(
            "and",
            1,
            binary_sig,
            lambda _, a: BVAnd(*a),
            "and[N](x: N, y: N) -> N: Bitwise and.",
        ),
        Function(
            "or",
            1,
            binary_sig,
            lambda _, a: BVOr(*a),
            "or[N](x: N, y: N) -> N: Bitwise or.",
        ),
        Function(
            "xor",
            1,
            binary_sig,
            lambda _, a: BVXor(*a),
            "xor[N](x: N, y: N) -> N: Bitwise exclusive or.",
        ),
        Function(
            "sext",
            2,
            ext_sig,
            lambda p, a: BVSExt(a[0], p[1] - p[0]),
            "sext[N, M](x: N) -> M: Sign-extend `x` from `N` bits to `M` bits.",
        ),
        Function(
            "zext",
            2,
            ext_sig,
            lambda p, a: BVZExt(a[0], p[1] - p[0]),
            "zext[N, M](x: N) -> M: Zero-extend `x` from `N` bits to `M` bits.",
        ),
        Function(
            "slice",
            3,
            slice_sig,
            lambda p, a: BVExtract(a[0], p[1], p[2]),
            "slice[N, L, H](x: N) -> (L-H+1): Extract the bits from `L` to `H` (inclusive) from `x`.",
        ),
    ]
}
