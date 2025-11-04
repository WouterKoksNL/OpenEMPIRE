"""Operational sets for the EMPIRE model (excluding module-specific sets)."""
from pyomo.environ import Set

def define_base_operational_sets(model, Operationalhour, Season, HoursOfSeason,
                                 FirstHoursOfRegSeason, FirstHoursOfPeakSeason,
                                 Scenario, GasScenario):
    """Define sets specific to operational constraints.
    
    These are general operational sets. Module-specific sets (hydrogen, industry, 
    heat, natural gas) are defined in their respective modules.
    
    Args:
        model: Pyomo abstract model
    """
    # Note: Most operational sets are already defined in shared.sets
    # This module is here for consistency and future operational-specific sets
    
    model.Operationalhour = Set(ordered=True, initialize=Operationalhour)  # h
    model.Season = Set(ordered=True, initialize=Season)  # s


    model.HoursOfSeason = Set(dimen=2, ordered=True, initialize=HoursOfSeason)  # (s,h) for all s in S, h in H_s
    model.FirstHoursOfRegSeason = Set(within=model.Operationalhour, ordered=True, initialize=FirstHoursOfRegSeason)
    model.FirstHoursOfPeakSeason = Set(within=model.Operationalhour, ordered=True, initialize=FirstHoursOfPeakSeason)
    # Stochastic sets
    model.Scenario = Set(ordered=True, initialize=Scenario)  # w
    model.GasScenario = Set(ordered=True, initialize=GasScenario)  # gp
