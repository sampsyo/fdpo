import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang, smt, lib
from .util import Env, parse_env
import re
import logging
import sys
from typing import Optional
from dataclasses import dataclass

LOG = logging.getLogger("fdpo")
MAX_ERRORS = 5


def parse_env_lines(s: str) -> dict[str, int]:
    return {
        name: int(val) for name, val in re.findall(r"^(\w+) = (\d+)$", s, re.M)
    }


def extract_code(s: str) -> Optional[str]:
    """Extract a Markdown fenced code block from the string."""
    parts = re.split(r"^```$", s, 2, re.M)
    if len(parts) >= 3:
        return parts[1]
    else:
        return None


@dataclass
class CheckCommand:
    prog: lang.Program


@dataclass
class EvalCommand:
    env: Env
    prog: lang.Program


Command = CheckCommand | EvalCommand


class CommandError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def parse_command(s: str) -> Command:
    """Parse an agent command from a response."""
    code = extract_code(s)
    if not code:
        raise CommandError("no fenced command found")
    try:
        cmd, prog = code.strip().split("\n", 1)
    except ValueError:
        raise CommandError("missing program following the operation line")
    prog, _ = lang.parse(prog)
    opcode, *args = cmd.split()
    match opcode:
        case "check":
            return CheckCommand(prog)
        case "eval":
            return EvalCommand(parse_env(args), prog)
        case _:
            raise CommandError(f"unknown command: {opcode}")


class Chat:
    def __init__(self, asker: "Asker"):
        self.asker = asker
        self.history = []

    async def send(self, message: str) -> str:
        LOG.debug(
            "Sending message (hist. %i):\n%s", len(self.history), message
        )
        self.history.append({"role": "user", "content": message})
        resp = await self.asker.client.chat(
            model=self.asker.model, messages=self.history, stream=True
        )
        out = []
        LOG.debug("Receiving response.")
        async for part in resp:  # type: ignore
            text = part["message"]["content"]
            if LOG.level <= logging.DEBUG:
                print(text, end="", file=sys.stderr, flush=True)
            out.append(text)
        if LOG.level <= logging.DEBUG:
            print(file=sys.stderr, flush=True)
        LOG.debug("Response finished with %s parts.", len(out))
        out_s = "".join(out)
        self.history.append({"role": "assistant", "content": out_s})
        return out_s


class OptChat(Chat):
    def __init__(self, asker: "Asker", prog: lang.Program):
        super().__init__(asker)
        self.prog = prog
        self.errors = 0

    async def get_command(self, prompt: str) -> Command:
        resp = await self.send(prompt)
        try:
            return parse_command(resp)
        except CommandError as e:
            self.errors += 1
            assert self.errors < MAX_ERRORS  # TODO handle gracefully
            err_prompt = self.asker.prompt(
                "malformed_command.md", error=str(e)
            )
            return await self.get_command(err_prompt)

    async def run(self) -> lang.Program:
        prompt = self.asker.prompt("opt.md", prog=self.prog.pretty())
        cmd = await self.get_command(prompt)

        match cmd:
            case CheckCommand(new_prog):
                print("CHECK")
                # Check equivalence.
                ce = smt.equiv(self.prog, new_prog)
                if ce:
                    # TODO: Send counter-example as feedback.
                    ce.print()
                    assert False
                else:
                    print("EQUIV")
                    return new_prog
            case EvalCommand(env, new_prog):
                print("EVAL")

        return new_prog


class Asker:
    def __init__(self, config: dict):
        self.client = AsyncClient(host=config["host"])
        self.model = config["model"]
        self.jinja = jinja2.Environment(
            loader=jinja2.PackageLoader("fdpo", "prompts"),
        )

    def prompt(self, filename: str, **kwargs) -> str:
        template = self.jinja.get_template(filename)
        kwargs["lib_help"] = "\n".join(
            f"* {f.help}" for f in lib.FUNCTIONS.values()
        )
        return template.render(**kwargs)

    async def interact(self, prompt: str):
        LOG.debug("Sending prompt:\n%s", prompt)
        resp = await self.client.generate(
            model=self.model, prompt=prompt, stream=True
        )
        out = []
        LOG.debug("Receiving response.")
        async for part in resp:  # type: ignore
            text = part["response"]
            if LOG.level <= logging.DEBUG:
                print(text, end="", file=sys.stderr, flush=True)
            out.append(text)
        if LOG.level <= logging.DEBUG:
            print(file=sys.stderr, flush=True)
        LOG.debug("Response finished with %s parts.", len(out))
        return "".join(out)

    async def run(self, prog: lang.Program, inputs: Env) -> Env:
        input_str = "\n".join(f"{k} = {v}" for k, v in inputs.items())
        prompt = self.prompt("run.md", prog=prog.pretty(), invals=input_str)
        res = await self.interact(prompt)
        return parse_env_lines(res)

    async def opt(self, prog: lang.Program) -> lang.Program:
        return await OptChat(self, prog).run()
