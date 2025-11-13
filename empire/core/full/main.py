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
from empire.core.full.operational.operational_input_params import OperationalInputParams
from .out_of_sample_functions import set_out_of_sample_path, run_operational_model
from .results import write_operational_results, write_pre_solve
from empire.results.main import write_results
from .solver import set_solver, solve
from .helpers import pickle_instance, log_problem_statistics, prepare_temp_dir, prepare_results_dir
from empire.core.config import EmpireConfiguration
from empire.core.paths import PathsConfig



from empire.core.full.shared import (
    define_shared_sets,
    load_shared_set_data,
    define_shared_parameters,
    define_shared_derived_sets,
    load_shared_parameter_data,
    define_shared_expressions,
)
from empire.core.full.investment import (
    define_investment_variables,
    define_investments_as_param,
    define_investment_expressions,
    define_investment_constraints,
    load_oos_investments,

    define_investment_parameters,
    load_investment_parameter_data,
)
from empire.core.full.operational import (
    define_operational_sets,
    define_operational_parameters,
    define_operational_variables,
    load_operational_parameter_data,
    define_operational_expressions,
    define_operational_constraints,
    derive_instance_stochastic_parameters,
    load_operational_set_data,
    define_operational_derived_sets,
)


logger = logging.getLogger(__name__)



def run_empire(
        paths: PathsConfig,
        empire_config: EmpireConfiguration,
        periods_active: list[int], 
        operational_input_params: OperationalInputParams,
        out_of_sample_flag: bool = False,
        sample_file_path: Path | None = None,
        ) -> tuple[float, ConcreteModel] | None:
    
    dataset_dir = paths.dataset_path
    filtering_dict = {"Period": periods_active}
    stochastic_input_dir = (dataset_dir / "Stochastic" if not out_of_sample_flag else sample_file_path)
    
    windfarmNodes = None
    offshoreNodesList = []

    prepare_temp_dir(empire_config.use_temporary_directory, temp_dir=empire_config.temporary_directory)
    prepare_results_dir(paths)

    model = AbstractModel()
    
    define_shared_sets(model, windfarmNodes, empire_config)
    define_operational_sets(model, operational_input_params, empire_config)
    

    data = DataPortal()
    load_shared_set_data(data, paths.dataset_path, model, empire_config, load_period=True, periods_active=periods_active)
    load_operational_set_data(data, paths.dataset_path, model, empire_config)
    define_shared_derived_sets(model, offshoreNodesList, empire_config)  # must be before operational parameter loading 
    define_operational_derived_sets(model, empire_config)
    define_investment_parameters(model, empire_config)
    define_operational_parameters(model, empire_config)
    define_shared_parameters(model, empire_config)

    filtering_dict = {"Period": periods_active}
    load_shared_parameter_data(data, paths.dataset_path, model, empire_config, filtering_dict=filtering_dict)
    
    load_operational_parameter_data(data, paths.dataset_path, stochastic_input_dir, model, empire_config, filtering_dict=filtering_dict)
    load_investment_parameter_data(data, paths.dataset_path, model, empire_config, filtering_dict=filtering_dict)
  
    
    # Variable definitions
    if out_of_sample_flag:
        define_investments_as_param(model, empire_config)
        load_oos_investments(model, data, paths.results_path, empire_config)
        results_path = set_out_of_sample_path(paths.results_path, sample_file_path)
        logger.info("Out-of-sample results will be saved to: %s", results_path)
    else:
        define_investment_variables(model, empire_config)

    define_operational_variables(model, empire_config)
    
    define_operational_expressions(model, empire_config, paths.results_path)
    define_investment_expressions(model, empire_config)
    define_shared_expressions(model, empire_config)

    define_objective(model, empire_config)

    define_operational_constraints(model, empire_config)

    if not out_of_sample_flag:
        # All constraints exclusively for investment decisions inactive when out_of_sample
        define_investment_constraints(model, empire_config, windfarmNodes)


    #################################################################


    #######
    ##RUN##
    #######

    logger.info("Objective and constraints read...")

    logger.info("Building instance...")

    start = time.time()
    instance: ConcreteModel = model.create_instance(data) #, report_timing=True)
    derive_instance_stochastic_parameters(instance)
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

    write_results(        
        instance, 
        paths.results_path, 
        paths.run_name,
        empire_config,)

    if empire_config.compute_operational_duals_flag and not out_of_sample_flag:
        run_operational_model(instance, opt, paths.results_path, paths.run_name, logger)
        write_operational_results(instance, paths.results_path, empire_config.emission_cap_flag, logger)
    return


