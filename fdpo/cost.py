from . import lang, lib


def score_expr(expr: lang.Expression) -> int:
    match expr:
        case lang.Call(fname, params, inputs):
            func = lib.FUNCTIONS[fname]
            return func.cost(params)
        case _:
            return 0


def score(prog: lang.Program) -> int:
    return sum(score_expr(a.expr) for a in prog.assignments)
