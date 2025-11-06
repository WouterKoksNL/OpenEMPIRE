from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_industry_investment_variables(model: AbstractModel):
    """Define industry investment decision variables."""
    # Steel plant investment variables
    model.steelPlantBuiltCapacity = Var(model.SteelProducers, model.SteelPlants, model.Period, within=NonNegativeReals)
    model.steelPlantInstalledCapacity = Var(model.SteelProducers, model.SteelPlants, model.Period, within=NonNegativeReals)

    # Cement plant investment variables
    model.cementPlantBuiltCapacity = Var(model.CementProducers, model.CementPlants, model.Period, within=NonNegativeReals)
    model.cementPlantInstalledCapacity = Var(model.CementProducers, model.CementPlants, model.Period, within=NonNegativeReals)

    # Ammonia plant investment variables
    model.ammoniaPlantBuiltCapacity = Var(model.AmmoniaProducers, model.AmmoniaPlants, model.Period, within=NonNegativeReals)
    model.ammoniaPlantInstalledCapacity = Var(model.AmmoniaProducers, model.AmmoniaPlants, model.Period, within=NonNegativeReals)
