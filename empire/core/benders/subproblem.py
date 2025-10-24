

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

from empire.core.optimization.loading_utils import load_dict_into_dataportal, load_parameter, read_tab_file
from empire.core.optimization.objective import define_objective
from empire.core.optimization.operational import derive_stochastic_parameters, define_operational_sets, define_operational_constraints, prep_operational_parameters, define_operational_variables, define_operational_parameters, load_operational_parameters, define_stochastic_input, load_stochastic_input, define_period_and_scenario_dependent_parameters
from empire.core.optimization.shared_data import define_shared_sets, load_shared_sets, define_shared_parameters, load_shared_parameters
from empire.core.optimization.out_of_sample_functions import set_investments_as_parameters
from empire.core.optimization.solver import set_solver, solve, SolvingMethods
from empire.core.optimization.helpers import pickle_instance, log_problem_statistics, prepare_results_dir, prepare_temp_dir
from empire.core.config import EmpireRunConfiguration, OperationalInputParams, EmpireConfiguration
from empire.core.optimization.loading_utils import load_set_directly, filter_data


logger = logging.getLogger(__name__)


def create_subproblem_model(
        run_config: EmpireRunConfiguration,
        empire_config: EmpireConfiguration,
        operational_input_params: OperationalInputParams,
        ) -> None | float:

    prepare_temp_dir(empire_config.use_temporary_directory, temp_dir=empire_config.temporary_directory)
    prepare_results_dir(run_config)
    
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

    if empire_config.lopf_flag:
        logger.info("LOPF constraints activated using method: %s", empire_config.lopf_method)
        from .lopf_module import add_lopf_constraints
        kw = {} if empire_config.lopf_kwargs is None else dict(empire_config.lopf_kwargs)
        add_lopf_constraints(model, method=empire_config.lopf_method, **kw)



    define_objective(model, include_investment=False)


    #################################################################

    #######
    ##RUN##
    #######

    logger.info("Model created")

    return model


def load_data(
    model: AbstractModel, 
    run_config: EmpireRunConfiguration, 
    empire_config: EmpireConfiguration, 
    period: int, 
    scenario: str, 
    out_of_sample_flag: bool, 
    sample_file_path: Path | None = None
    ) -> DataPortal:

    data = DataPortal()
    load_shared_sets(model, data, run_config.tab_file_path, empire_config.north_sea_flag, load_period=False)
    load_set_directly(data, model.Period, period)
    load_set_directly(data, model.PeriodActive, period)
    load_set_directly(data, model.Scenario, scenario)

    load_shared_parameters(model, data, run_config.tab_file_path)
    load_selected_operational_parameters(model, data, run_config.tab_file_path, empire_config.emission_cap_flag, out_of_sample_flag, period, scenario, sample_file_path=sample_file_path, scenario_data_path=run_config.scenario_data_path)

    return data


def load_selected_operational_parameters(model, data, tab_file_path, emission_cap_flag, out_of_sample_flag, period: int, scenario: str, sample_file_path=None, scenario_data_path=None) -> None:
    # Load operational generator parameters
    data.load(filename=str(tab_file_path / 'Generator_VariableOMCosts.tab'), param=model.genVariableOMCost, format="table")

    data.load(filename=str(tab_file_path / 'Generator_CO2Content.tab'), param=model.genCO2TypeFactor, format="table")
    data.load(filename=str(tab_file_path / 'Generator_GeneratorTypeAvailability.tab'), param=model.genCapAvailTypeRaw, format="table")
    data.load(filename=str(tab_file_path / 'Generator_RampRate.tab'), param=model.genRampUpCap, format="table")

    # Load operational transmission line parameters
    data.load(filename=str(tab_file_path / 'Transmission_lineEfficiency.tab'), param=model.lineEfficiency, format="table")

    # Storage parameters
    data.load(filename=str(tab_file_path / 'Storage_StorageBleedEfficiency.tab'), param=model.storageBleedEff, format="table")
    data.load(filename=str(tab_file_path / 'Storage_StorageChargeEff.tab'), param=model.storageChargeEff, format="table")
    data.load(filename=str(tab_file_path / 'Storage_StorageDischargeEff.tab'), param=model.storageDischargeEff, format="table")
    data.load(filename=str(tab_file_path / 'Storage_StorageInitialEnergyLevel.tab'), param=model.storOperationalInit, format="table")
    data.load(filename=str(tab_file_path / 'Node_HydroGenMaxAnnualProduction.tab'), param=model.maxHydroNode, format="table")
    data.load(filename=str(tab_file_path / 'General_seasonScale.tab'), param=model.seasScale, format="table")


    load_parameter(data, tab_file_path / 'Generator_Efficiency.tab', model.genEfficiency, periods_to_load=[period], period_indnr=1)
    load_parameter(data, tab_file_path / 'Node_ElectricAnnualDemand.tab', model.sloadAnnualDemand, periods_to_load=[period], period_indnr=1)
    load_parameter(data, tab_file_path / 'Node_NodeLostLoadCost.tab', model.nodeLostLoadCost, periods_to_load=[period], period_indnr=1)
    load_parameter(data, tab_file_path / 'Generator_FuelCosts.tab', model.genFuelCost, periods_to_load=[period], period_indnr=1)
    load_parameter(data, tab_file_path / 'Generator_CCSCostTSVariable.tab', model.CCSCostTSVariable, periods_to_load=[period], period_indnr=0)
    if emission_cap_flag:
        load_parameter(data, tab_file_path / 'General_CO2Cap.tab', model.CO2cap, periods_to_load=[period], period_indnr=0)
    else:
        load_parameter(data, tab_file_path / 'General_CO2Price.tab', model.CO2price, periods_to_load=[period], period_indnr=0)

    load_parameter(data, tab_file_path / 'Stochastic_HydroGenMaxSeasonalProduction.tab', model.maxRegHydroGenRaw, periods_to_load=[period], period_indnr=0, scenarios_to_load=[scenario], scenario_indnr=1)
    load_parameter(data, tab_file_path / 'Stochastic_StochasticAvailability.tab', model.genCapAvailStochRaw, periods_to_load=[period], period_indnr=3, scenarios_to_load=[scenario], scenario_indnr=4)

    load_parameter(data, tab_file_path / 'Stochastic_ElectricLoadRaw.tab', model.sloadRaw, periods_to_load=[period], period_indnr=0, scenarios_to_load=[scenario], scenario_indnr=1)

    return 



def create_subproblem_instance(model: AbstractModel, data: DataPortal) -> ConcreteModel:
    start = time.time()
    instance: ConcreteModel = model.create_instance(data) 
    end = time.time()
    logger.info("Building instance took [sec]: %d", end - start)
    instance.dual = Suffix(direction=Suffix.IMPORT) #Make sure the dual value is collected into solver results (if solver supplies dual information)
    return instance 


def solve_subproblem(instance, solver_name, run_config):

    opt = set_solver(solver_name, logger, solver_method=SolvingMethods.DUAL_SIMPLEX)
    _ = solve(instance, opt, run_config, logger)
 
    return opt


def load_capacity_values(
    sp_model,
    data, 
    capacity_params: dict[str, dict[tuple, float]],
    period_active: int,
    ) -> None:
    """Load capacity values from the MP into the DataPortal for the subproblem."""

    for param_name, capacities in capacity_params.items():
        filtered_capacities = filter_data(
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
        filtered_capacities = filter_data(
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
    run_config: EmpireRunConfiguration,
    operational_input_params: OperationalInputParams,
    ):
    if not isinstance(scenario, str):
        raise ValueError("Subproblem routine only supports single scenarios.")
    sp_model = create_subproblem_model(run_config, empire_config, operational_input_params)
    data = load_data(sp_model, run_config, empire_config, period_active, scenario, out_of_sample_flag=False) # load all data except capacities
    load_capacity_values(sp_model, data, capacity_params, period_active) # load capacities into DataPortal
    sp_instance = create_subproblem_instance(sp_model, data)
    node_unscaled_yearly_demand_ser = calc_total_raw_nodal_load(sp_instance.Node, period_active, operational_input_params, empire_config, run_config)
    derive_stochastic_parameters(sp_instance, node_unscaled_yearly_demand_ser)
    return sp_instance


def calc_total_raw_nodal_load(nodes: Set, period_active: int, operational_params: OperationalInputParams, empire_config: EmpireConfiguration, run_config: EmpireRunConfiguration) -> pd.Series:
    demand_data = read_tab_file(run_config.tab_file_path / 'Stochastic_ElectricLoadRaw.tab')
    demand_data_ser = pd.Series(demand_data)
    all_indices = [(period_active, w, n, h) for w in operational_params.scenarios for n in nodes for (s, h) in operational_params.HoursOfSeason]
    demand_data_ser = demand_data_ser.reindex(pd.MultiIndex.from_tuples(all_indices, names=['PeriodActive', 'Scenario', 'Node', 'Hour']), fill_value=0.0)
    # demand_data_ser_total = demand_data_ser.groupby(['Period', 'Node']).sum()
    sceProbab = 1 / len(operational_params.scenarios)  # Needs to be updated if non-uniform probabilities are used.
    seasScale = read_tab_file(run_config.tab_file_path / 'General_seasonScale.tab')
    node_unscaled_yearly_demand_ser = pd.Series(0.0, index=nodes)

    for n in nodes:
        # Compute probability-weighted raw demand
            node_unscaled_yearly_demand_ser.loc[n] = sum(
                sceProbab * seasScale[(s,)] * demand_data_ser[period_active, w, n, h]
                for (s, h) in operational_params.HoursOfSeason
                # if h < cutoff  # adjust if you want peak hours included
                for w in operational_params.scenarios
            )
    return node_unscaled_yearly_demand_ser