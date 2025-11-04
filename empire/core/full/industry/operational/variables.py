from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_industry_operational_variables(model: AbstractModel):
    """Define industry operational decision variables."""
    # Steel production variables
    model.steelProduced = Var(model.SteelProducers, model.SteelPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.steelLoadShed = Var(model.SteelProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Cement production variables
    model.cementProduced = Var(model.CementProducers, model.CementPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.cementLoadShed = Var(model.CementProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Ammonia production variables
    model.ammoniaProduced = Var(model.AmmoniaProducers, model.AmmoniaPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.ammoniaLoadShed = Var(model.AmmoniaProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Oil refining variables
    model.oilRefined = Var(model.OilProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.oilLoadShed = Var(model.OilProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
