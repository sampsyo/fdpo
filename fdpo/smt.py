from . import lang, lib
from pysmt.shortcuts import (
    Solver,
    Symbol,
    Equals,
    And,
    ForAll,
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


def expr_to_smt(env: SymbolEnv, expr: lang.Expression):
    if isinstance(expr, lang.Lookup):
        return env[expr.var]
    elif isinstance(expr, lang.Call):
        args = [expr_to_smt(env, arg) for arg in expr.inputs]
        return lib.FUNCTIONS[expr.func].smt(args)
    else:
        assert False


def symbol_env(prog: lang.Program) -> SymbolEnv:
    return {
        port.name: Symbol(port.name, BVType(port.width))
        for port in chain(prog.inputs.values(), prog.outputs.values())
    }


def prog_formula(prog: lang.Program) -> tuple[SymbolEnv, FNode]:
    env = symbol_env(prog)
    constraints = [
        Equals(env[asgt.dest], expr_to_smt(env, asgt.expr))
        for asgt in prog.assignments
    ]
    return env, And(*constraints)


def equiv_formula(prog1: lang.Program, prog2: lang.Program) -> FNode:
    env1, phi1 = prog_formula(prog1)
    env2, phi2 = prog_formula(prog2)
    in_constraints = [Equals(env1[port], env2[port]) for port in prog1.inputs]
    out_constraints = [
        Equals(env1[port], env2[port]) for port in prog1.outputs
    ]
    return ForAll(
        env1.values(),
        And(phi1, phi2, *(in_constraints + out_constraints)),
    )


def to_smt(prog: lang.Program) -> str:
    return to_smtlib(prog_formula(prog)[1])


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
        symb_env, prog_f = prog_formula(prog)
        env_constraints = [
            Equals(symb_env[var], BV(value, prog.inputs[var].width))
            for var, value in env.items()
        ]
        phi = And(prog_f, *env_constraints)
        model = get_model(phi)
    return {k: v for k, v in model_vals(model).items() if k in prog.outputs}
