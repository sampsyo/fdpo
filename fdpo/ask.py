import asyncio
from ollama import AsyncClient
import tomllib
import jinja2


async def interact(host, model, prompt):
    client = AsyncClient(host=host)
    resp = await client.generate(model=model, prompt=prompt, stream=True)
    async for part in resp:  # type: ignore
        print(part["response"], end="", flush=True)


def do_something():
    jinja = jinja2.Environment(
        loader=jinja2.PackageLoader("fdpo", "prompts"),
    )
    template = jinja.get_template("smoke.md")
    prompt = template.render()

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    asyncio.run(interact(config["host"], config["model"], prompt))


if __name__ == "__main__":
    do_something()
