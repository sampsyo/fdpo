from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Signature:
    inputs: list[int]
    output: int


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    sig: Callable[[list[int]], Signature]


def binary_sig(params: list[int]) -> Signature:
    return Signature([params[0], params[0]], params[0])


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 1, binary_sig),
        Function("sub", 1, binary_sig),
    ]
}
