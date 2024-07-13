import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang, smt, lib, check
from .util import Env, parse_env, env_str
import re
import logging
import sys
from typing import Optional, assert_never
from dataclasses import dataclass
import lark

LOG = logging.getLogger("fdpo")
MAX_ERRORS = 5
MAX_ROUNDS = 20
OPS = ["check", "eval"]


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


def same_sig(prog1: lang.Program, prog2: lang.Program) -> bool:
    return prog1.inputs == prog2.inputs and prog1.outputs == prog2.outputs


class AskError(Exception):
    pass


@dataclass
class CheckCommand:
    prog: lang.Program


@dataclass
class EvalCommand:
    env: Env
    prog: lang.Program


Command = CheckCommand | EvalCommand


class CommandError(Exception):
    pass


def parse_command(s: str) -> Command:
    """Parse an agent command from a response."""
    try:
        cmd, prog = s.strip().split("\n", 1)
    except ValueError:
        raise CommandError("missing program following the operation line")
    try:
        prog, _ = lang.parse(prog)
    except lark.UnexpectedInput as exc:
        raise CommandError(f"syntax error: {exc}")
    opcode, *args = cmd.split()
    match opcode:
        case "check":
            return CheckCommand(prog)
        case "eval":
            return EvalCommand(parse_env(args), prog)
        case _:
            raise CommandError(f"unknown command: {opcode}")


def parse_resp_command(s: str) -> Command:
    """Parse an agent command appearing anywhere in a response."""
    code = extract_code(s)
    if code:
        return parse_command(code)
    s = s.replace("```", "")
    return parse_command(s)


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

    async def get_command(self, prompt: str) -> Command:
        resp = await self.send(prompt)
        for _ in range(MAX_ERRORS):
            try:
                return parse_resp_command(resp)
            except CommandError as e:
                resp = await self.send(
                    self.asker.prompt("malformed_command.md", error=str(e))
                )
        raise AskError(f"exceeded {MAX_ERRORS} interaction errors")

    def well_formed(self, prog: lang.Program) -> Optional[str]:
        try:
            check.check(prog)
        except check.CheckError as e:
            return self.asker.prompt("illformed.md", error=str(e))
        return None

    def check(self, cmd: CheckCommand) -> Optional[str]:
        """Perform a `check` command for the agent.

        Return a message if the programs are not equivalent, or None (indicating the
        interaction is done) if they are.
        """
        # Check that the two programs have the same input/output ports.
        if not same_sig(self.prog, cmd.prog):
            return self.asker.prompt(
                "signature_mismatch.md", sig=self.prog.pretty_sig()
            )

        # Check that the program is well-formed.
        if err := self.well_formed(cmd.prog):
            return err

        # Check for an identical program.
        if self.prog == cmd.prog:
            return self.asker.prompt("identical.md")

        # Check equivalence.
        ce = smt.equiv(self.prog, cmd.prog)
        if ce:
            return self.asker.prompt("counterexample.md", ce=str(ce))
        else:
            return None

    def eval(self, cmd: EvalCommand) -> str:
        """Perform an `eval` command for the agent."""
        # Check that the provided inputs match the input ports.
        if not all(name in cmd.env for name in self.prog.inputs):
            return self.asker.prompt(
                "missing_input.md", inputs=", ".join(cmd.prog.inputs)
            )

        # Silently ignore extra inputs.
        env = {k: v for k, v in cmd.env.items() if k in self.prog.inputs}

        # Check that the program is well-formed.
        if err := self.well_formed(cmd.prog):
            return err

        # Run the program.
        res = smt.run(cmd.prog, cmd.env)
        return self.asker.prompt("eval.md", env=env_str(res))

    async def run(self) -> lang.Program:
        prompt = self.asker.prompt("opt.md", prog=self.prog.pretty())
        cmd = await self.get_command(prompt)

        for _ in range(MAX_ROUNDS):
            match cmd:
                case CheckCommand(_):
                    resp = self.check(cmd)
                    if resp is None:
                        return cmd.prog
                case EvalCommand(_, _):
                    resp = self.eval(cmd)
                case _:
                    assert_never(cmd)

            prompt = self.asker.prompt("next_command.md", ops=OPS)
            cmd = await self.get_command(f"{resp}\n\n{prompt}")

        raise AskError(f"exceeded {MAX_ROUNDS} interaction rounds")


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
