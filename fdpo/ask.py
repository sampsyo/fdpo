import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang, smt, lib, check, cost
from .util import Env, parse_env, env_str
import re
import logging
import sys
from typing import Optional, assert_never
from dataclasses import dataclass
import datetime
import os

LOG = logging.getLogger("fdpo")
MAX_ERRORS = 5
MAX_ROUNDS = 20
OPS = ["check", "eval", "cost", "commit"]


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

    def log(self) -> str:
        return "check"


@dataclass
class EvalCommand:
    env: Env
    prog: lang.Program

    def log(self) -> str:
        return f"eval({env_str(self.env)})"


@dataclass
class CostCommand:
    prog: lang.Program

    def log(self) -> str:
        return f"cost -> {cost.score(self.prog)}"


@dataclass
class CommitCommand:
    prog: lang.Program

    def log(self) -> str:
        return "commit"


Command = CheckCommand | EvalCommand | CostCommand | CommitCommand


class CommandError(Exception):
    pass


def parse_command(s: str) -> Command:
    """Parse an agent command from a response."""
    try:
        cmd, prog = s.strip().split("\n", 1)
    except ValueError:
        raise CommandError("missing program following the operation line")

    # Tolerate a trailing semicolon on the command.
    if cmd.endswith(";"):
        cmd = cmd[:-1]

    try:
        prog, _ = lang.parse(prog)
    except lang.ParseError as exc:
        raise CommandError(f"syntax error: {exc}")

    opcode, *args = cmd.split()
    match opcode:
        case "check":
            return CheckCommand(prog)
        case "eval":
            try:
                env = parse_env(args)
            except ValueError as exc:
                raise CommandError(f"invalid evaluation value: {exc}")
            return EvalCommand(env, prog)
        case "cost":
            return CostCommand(prog)
        case "commit":
            return CommitCommand(prog)
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
    def __init__(self, asker: "Asker", transcript_dir: Optional[str] = None):
        self.asker = asker
        self.history = []

        if transcript_dir:
            os.makedirs(transcript_dir, exist_ok=True)
            tstamp = datetime.datetime.now().isoformat()
            filename = os.path.join(transcript_dir, f"{tstamp}.md")
            self.transcript_file = open(filename, "w")
        else:
            self.transcript_file = None

    def transcribe(self, s: str, end="\n") -> None:
        if self.transcript_file:
            print(s, end=end, file=self.transcript_file, flush=True)

    async def send(self, message: str) -> str:
        LOG.debug(
            "Sending message (hist. %i):\n%s", len(self.history), message
        )
        self.transcribe(f"# round {len(self.history) // 2}\n")
        self.transcribe(message)
        self.transcribe("\n---\n")

        self.history.append({"role": "user", "content": message})
        resp = await self.asker.client.chat(
            model=self.asker.model, messages=self.history, stream=True
        )

        out = []
        LOG.debug("Receiving response.")
        self.transcribe("```")
        async for part in resp:  # type: ignore
            text = part["message"]["content"]
            if LOG.level <= logging.DEBUG:
                print(text, end="", file=sys.stderr, flush=True)
            self.transcribe(text, end="")
            out.append(text)
        if LOG.level <= logging.DEBUG:
            print(file=sys.stderr, flush=True)
        self.transcribe("\n```\n")

        LOG.debug("Response finished with %s parts.", len(out))
        out_s = "".join(out)
        self.history.append({"role": "assistant", "content": out_s})
        return out_s


class OptChat(Chat):
    def __init__(
        self,
        asker: "Asker",
        prog: lang.Program,
        transcript_dir: Optional[str] = None,
    ):
        super().__init__(asker, transcript_dir)
        self.prog = prog
        self.best_prog: Optional[lang.Program] = None

    def prompt(self, name: str, **kwargs) -> str:
        return self.asker.prompt(
            name, prog=self.prog, best_prog=self.best_prog, ops=OPS, **kwargs
        )

    async def get_command(self, prompt: str) -> Command:
        resp = await self.send(prompt)
        for _ in range(MAX_ERRORS):
            try:
                return parse_resp_command(resp)
            except CommandError as e:
                LOG.info("   malformed command: %s", e)
                resp = await self.send(
                    self.prompt("malformed_command.md", error=str(e))
                )
        raise AskError(f"exceeded {MAX_ERRORS} interaction errors")

    def well_formed(self, prog: lang.Program) -> Optional[str]:
        try:
            check.check(prog)
        except check.CheckError as e:
            LOG.info("   ill-formed: %s", e)
            return self.prompt("illformed.md", error=str(e))
        return None

    def _check_equiv(self, prog: lang.Program) -> Optional[str]:
        """Check program equivalence.

        Return a message if the programs are not equivalent, or None if they are.
        """
        # Check that the two programs have the same input/output ports.
        if not same_sig(self.prog, prog):
            return self.prompt("signature_mismatch.md")

        # Check that the program is well-formed.
        if err := self.well_formed(prog):
            return err

        # Check for an identical program.
        if self.prog == prog:
            LOG.info("   identical")
            return self.prompt("identical.md")

        # Check equivalence.
        ce = smt.equiv(self.prog, prog)
        if ce:
            LOG.info("   not equivalent")
            return self.prompt("counterexample.md", ce=ce)
        else:
            LOG.info("   equivalent")
            # Save the new best equivalent program.
            score = cost.score(prog)
            if self.best_prog is None or score < cost.score(self.best_prog):
                LOG.info(f"   new best cost: {score}")
                self.best_prog = prog
            return None

    def check(self, cmd: CheckCommand) -> str:
        resp = self._check_equiv(cmd.prog)
        if resp:
            return resp
        return self.prompt("equivalent.md")

    def commit(self, cmd: CommitCommand) -> Optional[str]:
        """Perform a `commit` command for the agent.

        Return None if the interaction is done.
        """
        resp = self._check_equiv(cmd.prog)
        if resp:
            return resp
        if cost.score(cmd.prog) >= cost.score(self.prog):
            return self.prompt("cost.md", new_prog=cmd.prog)
        return None

    def eval(self, cmd: EvalCommand) -> str:
        """Perform an `eval` command for the agent."""
        # Check that the provided inputs match the input ports.
        if not all(name in cmd.env for name in self.prog.inputs):
            LOG.info(f"   missing inputs")
            return self.prompt(
                "missing_input.md", inputs=", ".join(cmd.prog.inputs)
            )

        # Check that the program is well-formed.
        if err := self.well_formed(cmd.prog):
            return err

        # Silently ignore extra inputs.
        env = {k: v for k, v in cmd.env.items() if k in self.prog.inputs}

        # Run the program.
        res = smt.run(cmd.prog, env)
        return self.prompt("eval.md", env=res)

    def cost(self, cmd: CostCommand) -> str:
        if err := self.well_formed(cmd.prog):
            return err
        return self.prompt("cost.md", new_prog=cmd.prog)

    async def run(self) -> tuple[lang.Program, int]:
        prompt = self.prompt("opt.md")
        cmd = await self.get_command(prompt)

        round = -1
        for round in range(MAX_ROUNDS):
            LOG.info("%i. %s", round + 1, cmd.log())
            match cmd:
                case CheckCommand(_):
                    resp = self.check(cmd)
                case EvalCommand(_, _):
                    resp = self.eval(cmd)
                case CostCommand(_):
                    resp = self.cost(cmd)
                case CommitCommand(_):
                    resp = self.commit(cmd)
                    break
                case _:
                    assert_never(cmd)

            prompt = self.prompt("next_command.md")
            try:
                cmd = await self.get_command(f"{resp}\n\n{prompt}")
            except AskError:
                if self.best_prog:
                    return self.best_prog, round + 1
                raise

        LOG.debug("Ended after %d interaction rounds.", round + 1)
        if self.best_prog:
            return self.best_prog, round + 1
        raise AskError(f"no equivalent found after {MAX_ROUNDS} rounds")


class Asker:
    def __init__(self, config: dict):
        self.client = AsyncClient(host=config["host"])
        self.model = config["model"]
        self.transcript_dir = config.get("transcripts")

        self.jinja = jinja2.Environment(
            loader=jinja2.PackageLoader("fdpo", "prompts"),
            autoescape=False,
        )
        self.jinja.globals.update(
            {
                "lib_help": "\n".join(
                    f"* {f.help}" for f in lib.FUNCTIONS.values()
                ),
            }
        )
        self.jinja.filters.update(
            {
                "score": cost.score,
                "env_str": env_str,
            }
        )

    def prompt(self, filename: str, **kwargs) -> str:
        template = self.jinja.get_template(filename)
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

    async def opt(self, prog: lang.Program) -> tuple[lang.Program, int]:
        return await OptChat(self, prog, self.transcript_dir).run()
