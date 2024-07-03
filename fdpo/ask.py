import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang
import re


def parse_env(s: str) -> dict[str, int]:
    return {
        name: int(val) for name, val in re.findall(r"^(\w+) = (\d+)$", s, re.M)
    }


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
        print(prompt)
        print("---")
        resp = await self.client.generate(
            model=self.model, prompt=prompt, stream=True
        )
        out = []
        async for part in resp:  # type: ignore
            text = part["response"]
            print(text, end="", flush=True)
            out.append(text)
        return "".join(out)

    def run(
        self, prog: lang.Program, inputs: dict[str, int]
    ) -> dict[str, int]:
        input_str = "\n".join(f"{k} = {v}" for k, v in inputs.items())
        prompt = self.prompt("run.md", prog=prog.pretty(), invals=input_str)
        res = asyncio.run(self.interact(prompt))
        return parse_env(res)
