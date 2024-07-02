from .lang import parse
from .check import check, CheckError
from .smt import prog_formula, equiv_formula, run, equiv
from pysmt.shortcuts import to_smtlib
import sys


def parse_inputs(args: list[str]) -> dict[str, int]:
    """Parse a list of arguments like a=5 b=42."""
    return {key: int(value) for key, value in (arg.split("=") for arg in args)}


def main():
    src = sys.stdin.read()
    prog1, prog2 = parse(src)

    try:
        check(prog1)
        if prog2:
            check(prog2)
    except CheckError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "print"
    match mode:
        case "print":
            print(prog1.pretty())
        case "smt":
            _, phi = prog_formula(prog1)
            print(to_smtlib(phi))
        case "equiv-smt":
            assert prog2
            phi = equiv_formula(prog1, prog2)
            print(to_smtlib(phi))
        case "run":
            inputs = parse_inputs(sys.argv[2:])
            for key, value in run(prog1, inputs).items():
                print(key, "=", value)
        case "equiv":
            assert prog2
            equiv(prog1, prog2)
        case _:
            print(f"error: unknown mode {mode}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
