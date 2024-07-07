from . import lang, smt, ask
from .util import Env
import random
import csv
import sys
import os


def gen_inputs(ports: list[lang.Port]) -> Env:
    return {port.name: random.getrandbits(port.width) for port in ports}


async def bench_run_one(filename: str, asker: ask.Asker) -> bool:
    # Parse the program.
    with open(filename) as f:
        src = f.read()
    prog, _ = lang.parse(src)

    # Generate a test vector, and get the golden output.
    inputs = gen_inputs(list(prog.inputs.values()))
    outputs = smt.run(prog, inputs)

    # "Ask" to run the same program.
    test_outputs = await asker.run(prog, inputs)

    return outputs == test_outputs


async def bench_run(filenames: list[str], asker: ask.Asker):
    writer = csv.writer(sys.stdout)
    writer.writerow(["prog", "success"])
    for filename in filenames:
        name, _ = os.path.splitext(os.path.basename(filename))
        success = await bench_run_one(filename, asker)
        writer.writerow([name, "1" if success else "0"])
