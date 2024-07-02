from . import lang, lib


def check_expr(prog: lang.Program, expr: lang.Expression):
    if isinstance(expr, lang.Call):
        if expr.func not in lib.FUNCTIONS:
            assert False, "unknown function"
        for arg in expr.args:
            check_expr(prog, arg)
    elif isinstance(expr, lang.Lookup):
        # TODO check that it's an input port
        pass
    else:
        assert False


def check(prog: lang.Program):
    for asgt in prog.assignments:
        check_expr(prog, asgt.expr)
