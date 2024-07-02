from . import lang, lib
from pysmt.shortcuts import (
    Solver,
    Symbol,
    Equals,
    And,
    to_smtlib,
    BV,
    get_model,
    get_env,
)
from pysmt.typing import BVType
from pysmt.fnode import FNode
from pysmt.logics import QF_BV
from itertools import chain
import shutil

SymbolEnv = dict[str, FNode]
Env = dict[str, int]


def expr_to_smt(ports: SymbolEnv, expr: lang.Expression):
    if isinstance(expr, lang.Lookup):
        return ports[expr.var]
    elif isinstance(expr, lang.Call):
        args = [expr_to_smt(ports, arg) for arg in expr.inputs]
        return lib.FUNCTIONS[expr.func].smt(args)
    else:
        assert False


def to_formula(prog: lang.Program) -> tuple[SymbolEnv, FNode]:
    ports = {
        port.name: Symbol(port.name, BVType(port.width))
        for port in chain(prog.inputs.values(), prog.outputs.values())
    }
    constraints = [
        Equals(ports[asgt.dest], expr_to_smt(ports, asgt.expr))
        for asgt in prog.assignments
    ]
    return ports, And(*constraints)


def to_smt(prog: lang.Program) -> str:
    return to_smtlib(to_formula(prog))


def model_vals(model) -> Env:
    """Get the bit-vector values from a pysmt `Model`."""
    return {key.symbol_name(): value.bv2nat() for key, value in model}


def solver(name: str, debug: bool = False):
    # Do a mysterious global-state dance for pysmt to register solvers for later use.
    smt_env = get_env()

    match name:
        case "z3":
            smt_env.factory.add_generic_solver(
                "z3", [shutil.which("z3"), "-smt2", "-in"], [QF_BV]
            )
        case "boolector":
            smt_env.factory.add_generic_solver(
                "boolector", [shutil.which("boolector"), "--smt2"], [QF_BV]
            )

    options = {}
    if debug:
        options["debug_interaction"] = True
    return Solver(name=name, solver_options=options)


def run(prog: lang.Program, env: Env) -> Env:
    with solver("z3"):
        ports, prog_f = to_formula(prog)
        env_constraints = [
            Equals(ports[var], BV(value, prog.inputs[var].width))
            for var, value in env.items()
        ]
        phi = And(prog_f, *env_constraints)
        model = get_model(phi)
    return {k: v for k, v in model_vals(model).items() if k in prog.outputs}
