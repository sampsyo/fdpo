from .lang import parse, Program, ParseError
from .check import check, CheckError
from .smt import prog_formula, equiv_formula, run, equiv
from .ask import AskError, Asker, AskConfig
from .util import parse_env, env_str
from .bench import bench_run, bench_opt
from .cost import score
from . import lib
from pysmt.shortcuts import to_smtlib
import sys
import tomllib
import os
import logging
from typing import Optional
import asyncio

LOG = logging.getLogger("fdpo")


def load_config() -> dict:
    config_path = os.path.expanduser("~/.config/fdpo.toml")
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except OSError:
        return {}


def read_progs() -> tuple[Program, Optional[Program]]:
    src = sys.stdin.read()
    try:
        prog1, prog2 = parse(src)
    except ParseError as exc:
        print(f"syntax error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        check(prog1)
        if prog2:
            check(prog2)
    except CheckError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(1)

    return prog1, prog2


def asker(config: dict) -> Asker:
    return Asker(
        AskConfig(
            host=config["host"],
            model=config["model"],
            transcript_dir=config.get("transcripts"),
        )
    )


def main():
    config = load_config()
    LOG.addHandler(logging.StreamHandler())
    LOG.setLevel(config.get("verbosity", logging.INFO))

    mode = sys.argv[1] if len(sys.argv) > 1 else "print"
    match mode:
        case "print":
            prog, _ = read_progs()
            print(prog.pretty())
        case "smt":
            prog, _ = read_progs()
            _, phi = prog_formula(prog)
            print(to_smtlib(phi))
        case "equiv-smt":
            prog1, prog2 = read_progs()
            assert prog2
            phi = equiv_formula(prog1, prog2)
            print(to_smtlib(phi))
        case "run":
            prog, _ = read_progs()
            inputs = parse_env(sys.argv[2:])
            print(env_str(run(prog, inputs)))
        case "equiv":
            prog1, prog2 = read_progs()
            assert prog2
            ce = equiv(prog1, prog2)
            if ce:
                print("not equivalent")
                print(ce)
            else:
                print("equivalent")
        case "ask-run":
            prog, _ = read_progs()
            inputs = parse_env(sys.argv[2:])
            print(env_str(asyncio.run(asker(config).run(prog, inputs))))
        case "ask-opt":
            prog, _ = read_progs()
            try:
                new_prog, _ = asyncio.run(asker(config).opt(prog))
            except AskError as e:
                print(e, file=sys.stderr)
                sys.exit(1)
            print(new_prog.pretty())
        case "bench-run":
            filenames = sys.argv[2:]
            count = config["bench"]["count"]
            asyncio.run(bench_run(filenames, asker(config), count))
        case "bench-opt":
            filenames = sys.argv[2:]
            count = config["bench"]["count"]
            asyncio.run(bench_opt(filenames, asker(config), count))
        case "lib-help":
            print("\n".join(f.help for f in lib.FUNCTIONS.values()))
        case "cost":
            prog, _ = read_progs()
            print(score(prog))
        case _:
            print(f"error: unknown mode {mode}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
