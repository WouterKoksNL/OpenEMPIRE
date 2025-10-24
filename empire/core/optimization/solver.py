from pyomo.environ import SolverFactory, Suffix, ConcreteModel
from pyomo.opt import TerminationCondition
import sys
import logging
from enum import Enum

from empire.core.config import EmpireRunConfiguration



class SolvingMethods(Enum):
    """Lists gurobi solver options"""
    PRIMAL_SIMPLEX = 0
    DUAL_SIMPLEX = 1
    BARRIER = 2
    CONCURRENT = 3


def set_solver(solver_name, logger, solver_method: SolvingMethods = SolvingMethods.DUAL_SIMPLEX):
    """Set the solver for the optimization problem and set the parameters (solver dependent). 
    Solver parameters are currently hardcoded!
    Solver options:
    - CPLEX
    - Xpress
    - Gurobi
    - GLPK

    Args:
        solver_name (str): The name of the solver to use.

    Returns:
        SolverFactoryClass: The solver instance.
    """
    
    if solver_name == "CPLEX":
        opt = SolverFactory("cplex", Verbose=True)
        opt.options["lpmethod"] = 4
        opt.options["solutiontype"] = 2
        #instance.display('outputs_cplex.txt')
    elif solver_name == "Xpress":
        opt = SolverFactory("xpress") #Verbose=True
        opt.options["defaultAlg"] = 4
        opt.options["crossover"] = 0
        opt.options["lpLog"] = 1
        opt.options["Trace"] = 1
        #instance.display('outputs_xpress.txt')
    elif solver_name == "Gurobi":
        opt = SolverFactory('gurobi', Verbose=True)
        opt.options["Method"] = solver_method.value   # dual-simplex obtains the most accurate duals
        opt.options["FeasibilityTol"] = 1e-9
        opt.options["OptimalityTol"] = 1e-9
        # Increase numerical focus (0 = default, 3 = maximum)
        opt.options["NumericFocus"] = 3
    elif solver_name == "GLPK":
        opt = SolverFactory("glpk", Verbose=True)
    else:
        sys.exit(f"ERROR! Invalid solver_name: {solver_name} Options: CPLEX, Xpress, Gurobi, GLPK")
    if logger is not None:
        logger.info("Using solver: %s", solver_name)
    return opt




def solve(
        instance: ConcreteModel, 
        opt: SolverFactory, 
        run_config: EmpireRunConfiguration, 
        logger: logging.Logger
        ):
    logger.info("Solving...")
    results = opt.solve(instance, tee=True, logfile=run_config.results_path / f"logfile_{run_config.run_name}.log")#, keepfiles=True, symbolic_solver_labels=True)
    if results.solver.termination_condition == TerminationCondition.optimal:
        return results
    else:
        raise ValueError(f"Optimization was not successful. Termination condition: {results.solver.termination_condition}.")