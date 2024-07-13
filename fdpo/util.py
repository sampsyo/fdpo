Env = dict[str, int]


def parse_env(args: list[str]) -> Env:
    """Parse a list of integer values like a=5 b=42."""
    return {key: int(value) for key, value in (arg.split("=") for arg in args)}


def env_str(env: Env) -> str:
    out = [f"{key} = {value}" for key, value in env.items()]
    return "\n".join(out)
