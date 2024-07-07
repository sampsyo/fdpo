from . import lang, smt, ask
from .util import Env
import random
import csv
import sys
import os
import asyncio


def gen_inputs(ports: list[lang.Port]) -> Env:
    return {port.name: random.getrandbits(port.width) for port in ports}


async def bench_run_one(filename: str, asker: ask.Asker, count: int) -> int:
    # Parse the program.
    with open(filename) as f:
        src = f.read()
    prog, _ = lang.parse(src)

    score = 0
    for _ in range(count):
        # Generate a test vector, and get the golden output.
        inputs = gen_inputs(list(prog.inputs.values()))
        outputs = smt.run(prog, inputs)

        # "Ask" to run the same program.
        test_outputs = await asker.run(prog, inputs)

        # Score one when we match.
        score += outputs == test_outputs

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
