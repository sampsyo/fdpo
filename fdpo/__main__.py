from .ir import parse
import sys


def main():
    src = sys.stdin.read()
    prog = parse(src)
    print(prog.pretty())


if __name__ == "__main__":
    main()
