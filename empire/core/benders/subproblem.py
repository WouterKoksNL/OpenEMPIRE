

from __future__ import division

import logging
import time
from pathlib import Path
import pandas as pd
from pyomo.environ import (
    DataPortal,
    AbstractModel,
    ConcreteModel,
    Set,
    Suffix
)

from empire.core.optimization.loading_utils import load_dict_into_dataportal, load_parameters
from empire.core.optimization.objective import define_objective
from empire.core.optimization.operational import OperationalInputParams, derive_stochastic_parameters, define_operational_sets, define_operational_constraints, prep_operational_parameters, define_operational_variables, define_operational_parameters, load_operational_parameters, define_stochastic_input, load_stochastic_input, define_period_and_scenario_dependent_parameters
from empire.core.optimization.shared_data import define_shared_sets, load_shared_sets, define_shared_parameters, load_shared_parameters
from empire.core.optimization.out_of_sample_functions import set_investments_as_parameters
from empire.core.optimization.solver import set_solver, solve, SolvingMethods
from empire.core.optimization.helpers import pickle_instance, log_problem_statistics, prepare_results_dir, prepare_temp_dir
from empire.core.config import EmpireConfiguration
from empire.core.paths import PathsConfig
from empire.core.optimization.loading_utils import load_set_directly, filter_dict, get_df, filter_df, load_parameter_from_df


logger = logging.getLogger(__name__)


def create_subproblem_model(
        paths: PathsConfig,
        empire_config: EmpireConfiguration,
        operational_input_params: OperationalInputParams,
        ) -> None | float:

    prepare_temp_dir(empire_config.use_temporary_directory, temp_dir=empire_config.temporary_directory)
    prepare_results_dir(paths)
    
    model = AbstractModel()

    
    ########
    ##SETS##
    ########

    define_shared_sets(model, empire_config.north_sea_flag)
    define_operational_sets(model, operational_input_params)


    ##############
    ##PARAMETERS##
    ##############

    #Define the parameters

    logger.info("Declaring parameters...")

    define_shared_parameters(model, empire_config.discount_rate, empire_config.leap_years_investment)
    # define_investment_parameters(model, wacc)
    define_operational_parameters(model, operational_input_params)
    define_period_and_scenario_dependent_parameters(model, empire_config.emission_cap_flag)  # should not be needed preferably.
    define_stochastic_input(model)
    #Load the data

    

    logger.info("Sets and parameters declared and read...")

    #############
    ##VARIABLES##
    #############

    logger.info("Declaring variables...")

    set_investments_as_parameters(model, set_only_capacities=True)

    define_operational_variables(model)


    # model parameter preparations
    prep_operational_parameters(model, num_scenarios=len(operational_input_params.scenarios))

    # constraint defintions
    define_operational_constraints(model, logger, empire_config.emission_cap_flag, include_hydro_node_limit_constraint_flag=False)


    define_objective(model, include_investment=False)


    #################################################################

    #######
    ##RUN##
    #######

    logger.info("Model created")

    return model


def load_data(
    model: AbstractModel, 
    paths: PathsConfig, 
    empire_config: EmpireConfiguration, 
    period: int, 
    scenario: str, 
    out_of_sample_flag: bool, 
    sample_file_path: Path | None = None
    ) -> DataPortal:

    data = DataPortal()
    load_shared_sets(model, data, paths.dataset_path, empire_config.north_sea_flag, load_period=False)
    load_set_directly(data, model.Period, period)
    load_set_directly(data, model.PeriodActive, period)
    load_set_directly(data, model.Scenario, scenario)

    load_shared_parameters(model, data, paths.dataset_path)
    
    load_operational_parameters(
        model,
        data,
        dataset_dir=paths.dataset_path,
        emission_cap_flag=empire_config.emission_cap_flag,
        filtering_flag=True,
        period=period,
        scenario=scenario
    )

    load_stochastic_input(
        model,
        data,
        dataset_dir=paths.dataset_path,
        filtering_flag=True,
        period=period,
        scenario=scenario,
    )

    return data


def create_subproblem_instance(model: AbstractModel, data: DataPortal) -> ConcreteModel:
    start = time.time()
    instance: ConcreteModel = model.create_instance(data) 
    end = time.time()
    logger.info("Building instance took [sec]: %d", end - start)
    instance.dual = Suffix(direction=Suffix.IMPORT) #Make sure the dual value is collected into solver results (if solver supplies dual information)
    return instance 


def solve_subproblem(instance, solver_name, paths):

    opt = set_solver(solver_name, logger, solver_method=SolvingMethods.DUAL_SIMPLEX)
    _ = solve(instance, opt, paths, logger)
 
    return opt


def load_capacity_values(
    sp_model,
    data, 
    capacity_params: dict[str, dict[tuple, float]],
    period_active: int,
    ) -> None:
    """Load capacity values from the MP into the DataPortal for the subproblem."""

    for param_name, capacities in capacity_params.items():
        filtered_capacities = filter_dict(
            capacities,
            periods_to_load=[period_active],
            period_indnr=-1,  # period index is always last in the tuple
        )
        load_dict_into_dataportal(data, getattr(sp_model, param_name), filtered_capacities)
    return

def update_capacity_values(
    sp_instance,
    capacity_params: dict[str, dict[tuple, float]],
    period_active: int,  # period index is always last in the tuple
    ) -> None:
    """Update capacity values in the subproblem instance from the MP capacities."""
    for param_name, capacities in capacity_params.items():
        filtered_capacities = filter_dict(
            capacities,
            periods_to_load=[period_active],
            period_indnr=-1,
        )
        for index, value in filtered_capacities.items():
            getattr(sp_instance, param_name)[index].value = value
    return

def init_subproblem(
    capacity_params: dict[str, dict[tuple, float]],
    period_active: int,
    scenario: str,
    empire_config: EmpireConfiguration,
    paths: PathsConfig,
    operational_input_params: OperationalInputParams,
    ):
    if not isinstance(scenario, str):
        raise ValueError("Subproblem routine only supports single scenarios.")
    sp_model = create_subproblem_model(paths, empire_config, operational_input_params)
    data = load_data(sp_model, paths, empire_config, period_active, scenario, out_of_sample_flag=False) # load all data except capacities
    load_capacity_values(sp_model, data, capacity_params, period_active) # load capacities into DataPortal
    sp_instance = create_subproblem_instance(sp_model, data)
    node_unscaled_yearly_demand_ser = calc_total_raw_nodal_load(sp_instance.Node, period_active, operational_input_params, paths)
    derive_stochastic_parameters(sp_instance, node_unscaled_yearly_demand_ser)
    return sp_instance


def calc_total_raw_nodal_load(
        nodes: Set, 
        period_active: int, 
        operational_params: OperationalInputParams, 
        paths: PathsConfig,
        ) -> pd.Series:
    demand_df = get_df(paths.dataset_path / 'Stochastic', 'sloadRaw')
    demand_df = filter_df(demand_df, period=period_active)

    seasScale = get_df(paths.dataset_path / 'General', 'seasScale')
    season_scale_mapping = seasScale.set_index('Season')["seasonScale"]
    hour_season_mapping = pd.Series(
        {hour: season for season, hour in operational_params.HoursOfSeason}
    )

    demand_df['Season'] = demand_df['Operationalhour'].map(hour_season_mapping)
    demand_df['Scale'] = demand_df['Season'].map(season_scale_mapping)

    # Scenario probability
    sceProbab = 1 / len(operational_params.scenarios)

    demand_df["weighted_load"] = sceProbab * demand_df["ElectricLoadRaw_in_MW"] * demand_df["Scale"]


    # Compute weighted yearly demand per node

    node_unscaled_yearly_demand_ser = (
        demand_df.groupby("Node")["weighted_load"].sum()
    .reindex(nodes, fill_value=0.0)
    )

    return node_unscaled_yearly_demand_ser

