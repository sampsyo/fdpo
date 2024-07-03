Set up:

    uv venv
    uv pip install -e .
    . ./.venv/bin/activate

Create the config at `~/.config/fdpo.toml`:

    host = "http://localhost:11434"
    model = "codegemma:instruct"

Test:

    turnt -j test/*/*.nl
