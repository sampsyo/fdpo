import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang, smt
import re
import logging
import sys
from typing import Optional

LOG = logging.getLogger("fdpo")


def parse_env(s: str) -> dict[str, int]:
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


class Asker:
    def __init__(self, config: dict):
        self.client = AsyncClient(host=config["host"])
        self.model = config["model"]
        self.jinja = jinja2.Environment(
            loader=jinja2.PackageLoader("fdpo", "prompts"),
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

    def run(
        self, prog: lang.Program, inputs: dict[str, int]
    ) -> dict[str, int]:
        input_str = "\n".join(f"{k} = {v}" for k, v in inputs.items())
        prompt = self.prompt("run.md", prog=prog.pretty(), invals=input_str)
        res = asyncio.run(self.interact(prompt))
        return parse_env(res)

    def opt(self, prog: lang.Program) -> lang.Program:
        # Ask for an optimized program.
        prompt = self.prompt("opt.md", prog=prog.pretty())
        code = extract_code(asyncio.run(self.interact(prompt)))
        assert code  # TODO: Send feedback and ask again.
        new_prog = lang.parse_body(code, prog)  # TODO: Catch syntax errors.

        # Check equivalence.
        ce = smt.equiv(prog, new_prog)
        if ce:
            # TODO: Send counter-example as feedback.
            ce.print()
            assert False

        return new_prog
