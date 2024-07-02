from . import lang, lib


class CheckError(Exception):
    def __init__(self, message):
        self.message = message


def check_expr(prog: lang.Program, expr: lang.Expression) -> int:
    if isinstance(expr, lang.Call):
        func = lib.FUNCTIONS.get(expr.func)
        if not func:
            raise CheckError(f"unknown function {expr.func}")
        if len(expr.params) != func.params:
            raise CheckError(
                f"{expr.func} expects {func.inputs} parameters "
                f"but call has {len(expr.inputs)} parameters"
            )
        if len(expr.inputs) != func.inputs:
            raise CheckError(
                f"{expr.func} expects {func.inputs} inputs "
                f"but call has {len(expr.inputs)} inputs"
            )
        for arg in expr.inputs:
            arg_width = check_expr(prog, arg)
            # TODO
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
