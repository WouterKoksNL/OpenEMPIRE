import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyomo.environ import AbstractModel, ConstraintList, value
from time import time

from empire.core.config import OperationalInputParams, EmpireConfiguration, EmpireRunConfiguration
from .master_problem import create_master_problem_instance, solve_master_problem, extract_capacity_params, define_initial_capacity_params
from .subproblem import init_subproblem, solve_subproblem, update_capacity_values
from empire.core.optimization.objective import SCALING_FACTOR
from empire.core.optimization.loading_utils import filter_data
from .cuts import create_scenario_cut

logger = logging.getLogger(__name__)

def run_benders(
    run_config: EmpireRunConfiguration,
    empire_config: EmpireConfiguration,
    operational_input_params: OperationalInputParams,
    periods_active: list[int],
    capacity_params_init: None | dict = None,
) -> tuple[AbstractModel | None, float | None]:
    """
    Function to create and solve and EMPIRE instance using Benders decomposition.

    Parameters
    ----------
    run_config : EmpireRunConfiguration
        Configuration for the current model run.
    empire_config : EmpireConfiguration
        General configuration for the EMPIRE model.
    operational_input_params : OperationalInputParams
        Operational input parameters. 
    periods : list[int]
        List of periods to consider in the model. (shorter than full planning horizon?)
    capacity_params_init : dict, optional
        Initial capacity parameters to start the Benders iterations, by default None.

    Returns
    -------
    tuple[ConcreteModel | None, float | None]
        Returns the final master problem instance and its objective value if converged, otherwise (None, None).
    
    """
    timer_start = time()
    mp_instance = create_master_problem_instance(run_config, empire_config, periods=periods_active, scenarios=operational_input_params.scenarios)
    # capacity_params = extract_capacity_params(mp_instance)
    if capacity_params_init is None:
        capacity_params = define_initial_capacity_params(mp_instance)
    else:
        capacity_params = capacity_params_init

    # solve_master_problem(mp_instance, empire_config.optimization_solver, flags, run_config, empire_config.temporary_directory, save_flag=False)
    logger.info("Creating Benders subproblem model...")
    
    last_mp_obj = -1.
    mp_instance.cut_constraints = ConstraintList()
    mp_objs = []
    subproblems = {(period_active, scenario): 
                   init_subproblem(
                    capacity_params,
                    period_active,
                    scenario,
                    empire_config,
                    run_config,
                    operational_input_params,
                )
                   for period_active in periods_active
                   for scenario in operational_input_params.scenarios
                   }
    for iteration in range(empire_config.max_benders_iterations):
        logger.info("Benders iteration %d", iteration + 1)
        cuts = []
        if empire_config.parallel_benders_flag:
            with ThreadPoolExecutor(max_workers=empire_config.n_cores) as executor:  # adjust number of workers
                futures = [
                    executor.submit(solve_and_create_cut, sp_instance, capacity_params, period_active, scenario, empire_config, run_config, mp_instance)
                    for (period_active, scenario), sp_instance in subproblems.items()
                ]

                for future in as_completed(futures):
                    cuts.append(future.result())
        else:
            for (period_active, scenario), sp_instance in subproblems.items():
                cut = solve_and_create_cut(sp_instance, capacity_params, period_active, scenario, empire_config, run_config, mp_instance)
                cuts.append(cut)
        for cut in cuts:
            mp_instance.cut_constraints.add(expr=cut)

        mp_objective = solve_master_problem(mp_instance, empire_config, run_config, save_flag=False)
        capacity_params = extract_capacity_params(mp_instance)
        mp_objs.append(mp_objective)
        if np.isclose(mp_objective, last_mp_obj, rtol=1-8):
            logger.info("Benders converged.")
            for i, mp_obj in enumerate(mp_objs):
                print(f"Iteration {i+1}: Master problem objective = {mp_obj:.6e}")
            timer_end = time()
            logger.info("Total Benders time [sec]: %d", timer_end - timer_start)
            print("Total Benders time [sec]:", timer_end - timer_start)
            return mp_objective, mp_instance
        last_mp_obj = mp_objective

    logger.info("Benders did not converge.")
    print("Benders did not converge.")
    return None, None



def solve_and_create_cut(sp_instance, capacity_params, period_active, scenario, empire_config, run_config, mp_instance):
    # sp_instance = subproblems[(period_active, scenario)]
    update_capacity_values(sp_instance, capacity_params, period_active)
    opt = solve_subproblem(sp_instance, empire_config.optimization_solver, run_config)
    cut = create_scenario_cut(
        mp_instance,
        sp_instance,
        capacity_params,
        period_active,
        scenario,
    )
    return cut