from .lang import parse
from .check import check, CheckError
import sys


def main():
    src = sys.stdin.read()
    prog = parse(src)

    try:
        check(prog)
    except CheckError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(1)

    print(prog.pretty())


if __name__ == "__main__":
    main()
