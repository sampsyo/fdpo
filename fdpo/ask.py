import asyncio
from ollama import AsyncClient
import tomllib
import jinja2
from . import lang


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
        resp = await self.client.generate(
            model=self.model, prompt=prompt, stream=True
        )
        async for part in resp:  # type: ignore
            print(part["response"], end="", flush=True)

    def run(self, prog: lang.Program, inputs: dict[str, int]):
        input_str = "\n".join(f"{k} = {v}" for k, v in inputs.items())
        prompt = self.prompt("run.md", prog=prog.pretty(), inputs=input_str)
        asyncio.run(self.interact(prompt))
