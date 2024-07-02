from . import lang, lib


class CheckError(Exception):
    def __init__(self, message):
        self.message = message


def check_expr(prog: lang.Program, expr: lang.Expression) -> int:
    if isinstance(expr, lang.Call):
        if expr.func not in lib.FUNCTIONS:
            raise CheckError(f"unknown function {expr.func}")
        for arg in expr.args:
            return check_expr(prog, arg)
        return 32  # TODO
    elif isinstance(expr, lang.Lookup):
        port = prog.inputs.get(expr.var)
        if not port:
            raise CheckError(f"unknown variable {expr.var}")
        return port.width
    else:
        assert False


def check_asgt(prog: lang.Program, asgt: lang.Assignment):
    expr_width = check_expr(prog, asgt.expr)
    dest_width = prog.outputs[asgt.dest].width
    if expr_width != dest_width:
        raise CheckError(
            f"width mismatch: {asgt.dest} has width {dest_width}, "
            f"but expression has width {expr_width}"
        )
    assert expr_width == dest_width, "width mismatch"


def check(prog: lang.Program):
    assigned = set()
    for asgt in prog.assignments:
        if asgt.dest in assigned:
            raise CheckError(f"{asgt.dest} assigned multiple times")
        assigned.add(asgt.dest)
        check_asgt(prog, asgt)

    for out in prog.outputs:
        if out not in assigned:
            raise CheckError(f"{out} not assigned")
