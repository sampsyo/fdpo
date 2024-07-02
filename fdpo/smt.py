from typing import Optional
from . import lang, lib
from pysmt.shortcuts import (
    Solver,
    Symbol,
    Equals,
    NotEquals,
    And,
    Or,
    ForAll,
    to_smtlib,
    BV,
    get_env,
)
from pysmt.typing import BVType
from pysmt.fnode import FNode
from pysmt import logics
from itertools import chain
import shutil
from dataclasses import dataclass

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


def symbol_env(prog: lang.Program, prefix: str = "") -> SymbolEnv:
    return {
        port.name: Symbol(f"{prefix}{port.name}", BVType(port.width))
        for port in chain(prog.inputs.values(), prog.outputs.values())
    }


def prog_env_formula(prog: lang.Program, env: SymbolEnv) -> FNode:
    constraints = [
        Equals(env[asgt.dest], expr_to_smt(env, asgt.expr))
        for asgt in prog.assignments
    ]
    return And(*constraints)


def prog_formula(prog: lang.Program) -> tuple[SymbolEnv, FNode]:
    env = symbol_env(prog)
    return env, prog_env_formula(prog, env)


def equiv_formula(prog1: lang.Program, prog2: lang.Program) -> FNode:
    env1 = symbol_env(prog1, "prog1_")
    phi1 = prog_env_formula(prog1, env1)
    env2 = symbol_env(prog2, "prog2_")
    phi2 = prog_env_formula(prog2, env2)
    inputs = And(Equals(env1[port], env2[port]) for port in prog1.inputs)
    outputs = Or(NotEquals(env1[port], env2[port]) for port in prog1.outputs)
    return And(phi1, phi2, inputs, outputs)


def to_smt(prog: lang.Program) -> str:
    return to_smtlib(prog_formula(prog)[1])


def model_vals(model) -> Env:
    """Get the bit-vector values from a pysmt `Model`."""
    return {key.symbol_name(): value.bv2nat() for key, value in model}


def get_solver(name: str, debug: bool = False):
    # Do a mysterious global-state dance for pysmt to register solvers for later use.
    smt_env = get_env()

    match name:
        case "z3":
            smt_env.factory.add_generic_solver(
                "z3", [shutil.which("z3"), "-smt2", "-in"], [logics.BV]
            )
        case "boolector":
            smt_env.factory.add_generic_solver(
                "boolector", [shutil.which("boolector"), "--smt2"], [logics.BV]
            )

    options = {}
    if debug:
        options["debug_interaction"] = True
    return Solver(name=name, solver_options=options)


def solve(phi: FNode) -> Optional[Env]:
    with get_solver("z3", False) as solver:
        solver.add_assertion(phi)
        if solver.solve():
            return model_vals(solver.get_model())
        else:
            return None


def run(prog: lang.Program, env: Env) -> Env:
    symb_env, prog_f = prog_formula(prog)
    env_constraints = [
        Equals(symb_env[var], BV(value, prog.inputs[var].width))
        for var, value in env.items()
    ]
    phi = And(prog_f, *env_constraints)

    model = solve(phi)
    assert model, "unsat"
    return {k: v for k, v in model.items() if k in prog.outputs}


@dataclass(frozen=True)
class Counterexample:
    inputs: Env
    differing_outputs: dict[str, tuple[int, int]]


def equiv(
    prog1: lang.Program, prog2: lang.Program
) -> Optional[Counterexample]:
    """Check whether programs are equivalent, returning an example if not."""
    phi = equiv_formula(prog1, prog2)
    model = solve(phi)
    if not model:
        return None

    # Found a counter-example. Let's belt-and-suspenders check that it's a
    # real counter-example, and also extract the inputs & differing outputs.
    inputs = {}
    for port in prog1.inputs.values():
        prog1_val = model[f"prog1_{port.name}"]
        prog2_val = model[f"prog2_{port.name}"]
        assert prog1_val == prog2_val, "differing input"
        inputs[port.name] = prog1_val
    differing_outputs = {}
    for port in prog1.outputs.values():
        prog1_val = model[f"prog1_{port.name}"]
        prog2_val = model[f"prog2_{port.name}"]
        if prog1_val != prog2_val:
            differing_outputs[port.name] = (prog1_val, prog2_val)
    assert differing_outputs, "no differing outputs"

    return Counterexample(inputs, differing_outputs)
