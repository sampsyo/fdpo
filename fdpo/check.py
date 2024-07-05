from . import lang, lib


class CheckError(Exception):
    def __init__(self, message):
        self.message = message


def short_call(call: lang.Call) -> str:
    """Get a short string representing a call.

    Include the function name and the parameters but not the inputs. For
    example, `foo[1, 2]`.
    """
    params_s = ", ".join(str(p) for p in call.params)
    return f"{call.func}[{params_s}]"


def check_expr(prog: lang.Program, expr: lang.Expression) -> int:
    if isinstance(expr, lang.Call):
        func = lib.FUNCTIONS.get(expr.func)
        if not func:
            raise CheckError(f"unknown function {expr.func}")

        # Apply the parameters to get the signature.
        if len(expr.params) != func.params:
            raise CheckError(
                f"{expr.func} expects {func.params} parameters "
                f"but call has {len(expr.params)} parameters"
            )
        sig = func.sig(expr.params)

        # Check the inputs.
        if len(expr.inputs) != len(sig.inputs):
            raise CheckError(
                f"{short_call(expr)} expects {len(sig.inputs)} inputs "
                f"but call has {len(expr.inputs)} inputs"
            )
        for i, (in_width, in_expr) in enumerate(zip(sig.inputs, expr.inputs)):
            expr_width = check_expr(prog, in_expr)
            if expr_width != in_width:
                raise CheckError(
                    f"width mismatch: input {i+1} to {short_call(expr)} "
                    f"has width {in_width}, but expression has width {expr_width}"
                )

        return sig.output

    elif isinstance(expr, lang.Lookup):
        port = prog.inputs.get(expr.var)
        if not port:
            raise CheckError(f"unknown variable {expr.var}")
        return port.width

    elif isinstance(expr, lang.Literal):
        return expr.width

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
