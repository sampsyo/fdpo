from .lang import parse
from .check import check
import sys


def main():
    src = sys.stdin.read()
    prog = parse(src)
    check(prog)
    print(prog.pretty())


if __name__ == "__main__":
    main()
