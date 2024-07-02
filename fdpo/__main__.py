from .lang import parse
from .check import check, CheckError
from .smt import to_smt
import sys


def main():
    src = sys.stdin.read()
    prog = parse(src)

    try:
        check(prog)
    except CheckError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "print"
    match mode:
        case "print":
            print(prog.pretty())
        case "smt":
            print(to_smt(prog))
        case _:
            print(f"error: unknown mode {mode}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
