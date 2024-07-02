from dataclasses import dataclass


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    inputs: int


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 1, 2),
        Function("sub", 1, 2),
    ]
}
