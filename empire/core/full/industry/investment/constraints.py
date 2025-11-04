"""Industry investment constraints."""
from pyomo.environ import Constraint, value


def define_industry_investment_constraints(model, LeapYearsInvestment):
    """Define constraints for industry plant investment.
    
    Args:
        model: Pyomo abstract model
        LeapYearsInvestment: Number of years per investment period
    """
    
    # Cement plant lifetime constraint
    def cement_plant_lifetime_rule(model, n, p, i):
        """Link cement plant investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - (model.cementPlantLifetime[p] / LeapYearsInvestment)) > startPeriod:
            startPeriod = value(1 + i - model.cementPlantLifetime[p] / LeapYearsInvestment)
        return sum(model.cementPlantBuiltCapacity[n, p, j] for j in model.Period if j >= startPeriod and j <= i) + \
               model.cement_initialCapacity[n, p] * (1 - model.cement_scaleFactorInitialCap[p, i]) == \
               model.cementPlantInstalledCapacity[n, p, i]
    model.cement_plant_lifetime = Constraint(model.CementProducers, model.CementPlants, model.Period, 
                                            rule=cement_plant_lifetime_rule)
    
    # Ammonia plant lifetime constraint
    def ammonia_plant_lifetime_rule(model, n, p, i):
        """Link ammonia plant investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - (model.ammoniaPlantLifetime[p] / LeapYearsInvestment)) > startPeriod:
            startPeriod = value(1 + i - model.ammoniaPlantLifetime[p] / LeapYearsInvestment)
        return sum(model.ammoniaPlantBuiltCapacity[n, p, j] for j in model.Period if j >= startPeriod and j <= i) + \
               model.ammonia_initialCapacity[n, p] * (1 - model.ammonia_scaleFactorInitialCap[p, i]) == \
               model.ammoniaPlantInstalledCapacity[n, p, i]
    model.ammonia_plant_lifetime = Constraint(model.AmmoniaProducers, model.AmmoniaPlants, model.Period, 
                                             rule=ammonia_plant_lifetime_rule)
    
    # Steel plant lifetime constraint
    def steel_plant_lifetime_rule(model, n, p, i):
        """Link steel plant investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - (model.steelPlantLifetime[p] / LeapYearsInvestment)) > startPeriod:
            startPeriod = value(1 + i - model.steelPlantLifetime[p] / LeapYearsInvestment)
        return sum(model.steelPlantBuiltCapacity[n, p, j] for j in model.Period if j >= startPeriod and j <= i) + \
               model.steel_initialCapacity[n, p] * (1 - model.steel_scaleFactorInitialCap[p, i]) == \
               model.steelPlantInstalledCapacity[n, p, i]
    model.steel_plant_lifetime = Constraint(model.SteelProducers, model.SteelPlants, model.Period, 
                                           rule=steel_plant_lifetime_rule)
    
    # Steel scrap capacity constraint
    def max_scrap_capacity_rule(model, p, i):
        """Limit steel scrap capacity to fraction of total production."""
        if 'scrap' in p.lower():
            return sum(model.steelPlantInstalledCapacity[n, p, i] for n in model.SteelProducers) <= \
                   0.45 * sum(model.steel_yearlyProduction[n, i] for n in model.SteelProducers) / 8760
        else:
            return Constraint.Skip
    model.max_scrap_capacity = Constraint(model.SteelPlants, model.Period, rule=max_scrap_capacity_rule)

