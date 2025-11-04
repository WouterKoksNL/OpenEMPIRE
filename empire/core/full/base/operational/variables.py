from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_base_operational_variables(model: AbstractModel, use_cvar):
    """Define base operational decision variables."""
    # Generator operational variables
    model.genOperational = Var(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Storage operational variables
    model.storOperational = Var(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.storCharge = Var(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.storDischarge = Var(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Transmission operational variables
    model.transmissionOperational = Var(model.DirectionalLink, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)  # flow
    
    # Load shedding variables
    model.loadShed = Var(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)

    ## CVaR module variables
    if use_cvar:
        model.aux_vars_cvar = Var(model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
        model.value_at_risk = Var(model.Period)