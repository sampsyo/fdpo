from . import lang, smt, ask, cost
from .util import Env
import random
import csv
import sys
import os
import asyncio
from typing import Optional
from collections.abc import Generator
from dataclasses import dataclass


@dataclass(frozen=True)
class BenchConfig:
    host: str
    models: list[str]
    transcript_dir: Optional[str]
    count: int
    methods: list[str]

    def ask_configs(self) -> Generator[ask.AskConfig, None, None]:
        for model in self.models:
            yield ask.AskConfig(
                host=self.host,
                model=model,
                transcript_dir=self.transcript_dir,
            )


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


async def bench_run(filenames: list[str], config: BenchConfig):
    writer = csv.writer(sys.stdout)
    writer.writerow(["prog", "model", "successes"])
    sys.stdout.flush()
    for ask_config in config.ask_configs():
        asker = ask.Asker(ask_config)
        tasks = {
            filename: bench_run_one(filename, asker, config.count)
            for filename in filenames
        }
        for filename, task in tasks.items():
            successes = await task
            name, _ = os.path.splitext(os.path.basename(filename))
            writer.writerow([name, ask_config.model, successes])
            sys.stdout.flush()


def bench_opt_tasks(
    filenames: list[str], config: BenchConfig, asker: ask.Asker
):
    for filename in filenames:
        with open(filename) as f:
            src = f.read()
        prog, _ = lang.parse(src)

        # One-shot queries.
        if "oneshot" in config.methods:
            for _ in range(config.count):
                yield filename, "oneshot", asker.opt_oneshot(prog)

        # Agent queries.
        if "agent" in config.methods:
            for _ in range(config.count):
                yield filename, "agent", asker.opt(prog)


async def bench_opt(filenames: list[str], config: BenchConfig):
    writer = csv.writer(sys.stdout)
    writer.writerow(["prog", "method", "model", "best_cost", "rounds"])
    sys.stdout.flush()
    for ask_config in config.ask_configs():
        asker = ask.Asker(ask_config)
        for filename, method, task in bench_opt_tasks(
            filenames, config, asker
        ):
            try:
                # TODO: Super hacky; make this type safe.
                if method == "oneshot":
                    new_prog = await task
                    rounds = 1
                else:
                    new_prog, rounds = await task  # type: ignore
            except ask.AskError as e:
                score = -1
                rounds = -1
            else:
                score = cost.score(new_prog)  # type: ignore
            name, _ = os.path.splitext(os.path.basename(filename))
            writer.writerow([name, method, ask_config.model, score, rounds])
            sys.stdout.flush()
