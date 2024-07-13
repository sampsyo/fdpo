Env = dict[str, int]

BASES = {"b": 2, "o": 8, "d": 10, "h": 16, "x": 16}


def parse_int(s: str) -> int:
    """Parse either a plain integer or a width/base-tagged
    integer, like 16d42.
    """
    try:
        return int(s)
    except ValueError as exc:
        for base, radix in BASES.items():
            if base in s:
                _, value = s.split(base, 1)
                return int(value, radix)
        raise ValueError(f"invalid integer: {s}")


def parse_env(args: list[str]) -> Env:
    """Parse a list of integer values like a=5 b=42."""
    return {
        key: parse_int(value)
        for key, value in (arg.split("=") for arg in args if "=" in arg)
    }


def env_str(env: Env) -> str:
    out = [f"{key} = {value}" for key, value in env.items()]
    return "\n".join(out)
