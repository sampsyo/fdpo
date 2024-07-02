from . import lang, lib


def check_expr(prog: lang.Program, expr: lang.Expression) -> int:
    if isinstance(expr, lang.Call):
        if expr.func not in lib.FUNCTIONS:
            assert False, "unknown function"
        for arg in expr.args:
            return check_expr(prog, arg)
        return 32  # TODO
    elif isinstance(expr, lang.Lookup):
        assert expr.var in prog.inputs, f"unknown input {expr.var}"
        return 32  # TODO
    else:
        assert False


def check_asgt(prog: lang.Program, asgt: lang.Assignment):
    expr_width = check_expr(prog, asgt.expr)
    dest_width = prog.outputs[asgt.dest].width
    assert expr_width == dest_width, "width mismatch"


def check(prog: lang.Program):
    for asgt in prog.assignments:
        check_asgt(prog, asgt)
