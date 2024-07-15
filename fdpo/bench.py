from . import lang, smt, ask, cost
from .util import Env
import random
import csv
import sys
import os
import asyncio


def gen_inputs(ports: list[lang.Port]) -> Env:
    return {port.name: random.getrandbits(port.width) for port in ports}


async def bench_run_exp(prog: lang.Program, asker: ask.Asker) -> bool:
    # Generate a test vector, and get the golden output.
    inputs = gen_inputs(list(prog.inputs.values()))
    outputs = smt.run(prog, inputs)

    # "Ask" to run the same program.
    test_outputs = await asker.run(prog, inputs)

    return outputs == test_outputs


async def bench_run_one(filename: str, asker: ask.Asker, count: int) -> int:
    with open(filename) as f:
        src = f.read()
    prog, _ = lang.parse(src)

    score = 0
    tasks = [bench_run_exp(prog, asker) for _ in range(count)]
    for task in asyncio.as_completed(tasks):
        # Score one when we match.
        score += await task

    return score


async def bench_run(filenames: list[str], asker: ask.Asker, count: int):
    writer = csv.writer(sys.stdout)
    writer.writerow(["prog", "successes"])
    tasks = {
        filename: bench_run_one(filename, asker, count)
        for filename in filenames
    }
    for filename, task in tasks.items():
        successes = await task
        name, _ = os.path.splitext(os.path.basename(filename))
        writer.writerow([name, successes])


def bench_opt_tasks(filenames: list[str], asker: ask.Asker, count: int):
    for filename in filenames:
        with open(filename) as f:
            src = f.read()
        prog, _ = lang.parse(src)

        for _ in range(count):
            yield filename, asker.opt(prog)


async def bench_opt(filenames: list[str], asker: ask.Asker, count: int):
    writer = csv.writer(sys.stdout)
    writer.writerow(["prog", "best_cost", "rounds"])
    for filename, task in bench_opt_tasks(filenames, asker, count):
        try:
            new_prog, rounds = await task
        except ask.AskError as e:
            score = -1
            rounds = -1
        else:
            score = cost.score(new_prog)
        name, _ = os.path.splitext(os.path.basename(filename))
        writer.writerow([name, score, rounds])
