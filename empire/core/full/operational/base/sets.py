"""Operational sets for the EMPIRE model (excluding module-specific sets)."""
from pyomo.environ import Set

from ..operational_input_params import OperationalInputParams


def define_base_operational_sets(model, operational_input_params: OperationalInputParams):
    """Define sets specific to operational constraints.
    
    These are general operational sets. Module-specific sets (hydrogen, industry, 
    heat, natural gas) are defined in their respective modules.
    
    Args:
        model: Pyomo abstract model
    """
    # Note: Most operational sets are already defined in shared.sets
    # This module is here for consistency and future operational-specific sets
    
    model.Operationalhour = Set(ordered=True, initialize=operational_input_params.Operationalhour)  # h
    model.Season = Set(ordered=True, initialize=operational_input_params.Season)  # s

    model.HoursOfSeason = Set(dimen=2, ordered=True, initialize=operational_input_params.HoursOfSeason)  # (s,h) for all s in S, h in H_s
    model.FirstHoursOfRegSeason = Set(within=model.Operationalhour, ordered=True, initialize=operational_input_params.FirstHoursOfRegSeason)
    model.FirstHoursOfPeakSeason = Set(within=model.Operationalhour, ordered=True, initialize=operational_input_params.FirstHoursOfPeakSeason)
    # Stochastic sets
    model.Scenario = Set(ordered=True, initialize=operational_input_params.scenarios)  # w
    model.GasScenario = Set(ordered=True, initialize=operational_input_params.gas_scenarios)  # gp
