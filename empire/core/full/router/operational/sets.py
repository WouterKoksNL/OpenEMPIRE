from base.operational.sets import define_base_operational_sets


def define_operational_sets(model, Operationalhour, Season, HoursOfSeason,
                            FirstHoursOfRegSeason, FirstHoursOfPeakSeason, Scenario, GasScenario):
    """Define operational sets for the model."""
    # Define operational sets (general)
    define_base_operational_sets(model, Operationalhour, Season, HoursOfSeason,
                                 FirstHoursOfRegSeason, FirstHoursOfPeakSeason, Scenario, GasScenario)