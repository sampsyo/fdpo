from dataclasses import dataclass


@dataclass(frozen=True)
class Function:
    name: str
    inputs: int


FUNCTIONS = {
    func.name: func
    for func in [
        Function("add", 2),
        Function("sub", 2),
    ]
}
