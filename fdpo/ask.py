import asyncio
from ollama import AsyncClient
import tomllib
import jinja2


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

    def do_something(self):
        prompt = self.prompt("smoke.md")
        asyncio.run(self.interact(prompt))
