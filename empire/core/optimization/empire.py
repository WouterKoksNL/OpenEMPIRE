import logging
import os
import time
from pathlib import Path



from pyomo.environ import (
    DataPortal,
    AbstractModel,
    ConcreteModel,
    value,
    Suffix
)
from .objective import define_objective
from .operational import OperationalInputParams, define_operational_sets, define_operational_constraints, prep_operational_parameters, derive_stochastic_parameters, define_operational_variables, define_operational_parameters, load_operational_parameters, define_stochastic_input, load_stochastic_input, define_period_and_scenario_dependent_parameters, load_operational_sets
from .investment import define_investment_constraints, prep_investment_parameters, define_investment_variables, load_investment_parameters, define_investment_parameters
from .shared_data import define_shared_sets, load_shared_sets, define_shared_parameters, load_shared_parameters
from .out_of_sample_functions import set_investments_as_parameters, load_optimized_investments, set_out_of_sample_path
from .results import write_results, run_operational_model, write_operational_results, write_pre_solve
from .solver import set_solver, solve
from .helpers import pickle_instance, log_problem_statistics, prepare_temp_dir, prepare_results_dir
from empire.core.config import EmpireConfiguration
from empire.core.paths import PathsConfig

logger = logging.getLogger(__name__)



def run_empire(
        paths: PathsConfig,
        empire_config: EmpireConfiguration,
        periods_active: list[int], 
        operational_input_params: OperationalInputParams,
        out_of_sample_flag: bool = False,
        sample_file_path: Path | None = None,
        ) -> tuple[float, ConcreteModel] | None:

    prepare_temp_dir(empire_config.use_temporary_directory, temp_dir=empire_config.temporary_directory)
    prepare_results_dir(paths)

    model = AbstractModel()
    
    # Set definitions
    define_shared_sets(model, empire_config.north_sea_flag)
    define_operational_sets(model, operational_input_params)


    # Parameter definitions
    define_shared_parameters(model, empire_config.discount_rate, empire_config.leap_years_investment)
    define_investment_parameters(model, empire_config.wacc)
    define_operational_parameters(model, operational_input_params)
    define_period_and_scenario_dependent_parameters(model, empire_config.emission_cap_flag)
    define_stochastic_input(model)

    # # Data loading
    data = DataPortal()
    load_shared_sets(model, data, paths.dataset_path, empire_config.north_sea_flag, load_period=True, periods_active=periods_active)
    load_operational_sets(model, data, operational_input_params.scenarios)
    load_shared_parameters(model, data, paths.dataset_path)
    load_operational_parameters(model, data, paths.dataset_path, empire_config.emission_cap_flag)
    load_stochastic_input(model, data, paths.dataset_path, out_of_sample_flag, sample_file_path=sample_file_path)
    load_investment_parameters(model, data, paths.dataset_path)

    # Variable definitions
    if out_of_sample_flag:
        set_investments_as_parameters(model)
        
        load_optimized_investments(model, data, paths.results_path, set_only_capacities=True)
        results_path = set_out_of_sample_path(paths.results_path, sample_file_path)
        logger.info("Out-of-sample results will be saved to: %s", results_path)

    else:
        define_investment_variables(model)

    define_operational_variables(model)


    if not out_of_sample_flag:
        # All constraints exclusively for investment decisions inactive when out_of_sample_flag
        prep_investment_parameters(model)


    # Constraint defintions
    if not out_of_sample_flag:
        define_investment_constraints(model, empire_config.north_sea_flag)
    define_operational_constraints(model, logger, empire_config.emission_cap_flag, include_hydro_node_limit_constraint_flag=empire_config.include_hydro_node_limit_constraint_flag)


    # Model parameter preparations
    prep_operational_parameters(model)

    # Objective definition
    define_objective(model)


    #################################################################


    #######
    ##RUN##
    #######

    logger.info("Objective and constraints read...")

    logger.info("Building instance...")

    start = time.time()
    instance: ConcreteModel = model.create_instance(data) #, report_timing=True)
    derive_stochastic_parameters(instance)
    instance.dual = Suffix(direction=Suffix.IMPORT) #Make sure the dual value is collected into solver results (if solver supplies dual information)

    end = time.time()
    logger.info("Building instance took [sec]: %d", end - start)

    #import pdb; pdb.set_trace()
    #instance.CO2price.pprint()
    if not out_of_sample_flag:	
        log_problem_statistics(instance, logger)
        write_pre_solve(
            instance,
            paths.results_path,
            paths.run_name,
            empire_config.write_in_lp_format,
            empire_config.use_temporary_directory,
            empire_config.temporary_directory,
            logger
        )


    opt = set_solver(empire_config.optimization_solver, logger)
    _ = solve(instance, opt, paths, logger)
    post_process(instance, paths, empire_config, opt, logger, out_of_sample_flag)  
    return value(instance.Obj), instance


def post_process(instance, paths, empire_config, opt, logger, out_of_sample_flag):
    if empire_config.pickle_instance_flag:
        pickle_instance(instance, paths.run_name, empire_config.use_temporary_directory, logger, empire_config.temporary_directory)

    #instance.display('outputs_gurobi.txt')

    #import pdb; pdb.set_trace()

    write_results(instance, paths.results_path, paths.run_name, out_of_sample_flag, empire_config.emission_cap_flag, empire_config.print_iamc_flag, logger)

    if empire_config.compute_operational_duals_flag and not out_of_sample_flag:
        run_operational_model(instance, opt, paths.results_path, paths.run_name, logger)
        write_operational_results(instance, paths.results_path, empire_config.emission_cap_flag, logger)
    return


