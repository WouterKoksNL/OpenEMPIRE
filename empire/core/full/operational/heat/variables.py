from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_heat_operational_variables(model: AbstractModel):
    """Define heat module operational decision variables."""
    # Converter operational variables
    model.ConverterOperational = Var(model.ConverterOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Thermal load shedding variables
    model.loadShedTR = Var(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
