import asyncio
from ollama import AsyncClient
import tomllib

PROMPT = """
Please write a Python program to compute the sum of two numbers. Just print the
code; no text is necessary.
""".strip()


async def interact(host, model):
    client = AsyncClient(host=host)
    resp = await client.generate(model=model, prompt=PROMPT, stream=True)
    async for part in resp:  # type: ignore
        print(part["response"], end="", flush=True)


def do_something():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    asyncio.run(interact(config["host"], config["model"]))


if __name__ == "__main__":
    do_something()
