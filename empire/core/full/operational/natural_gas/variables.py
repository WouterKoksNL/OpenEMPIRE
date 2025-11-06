from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_natural_gas_operational_variables(model: AbstractModel):
    """Define natural gas operational decision variables."""
    # Natural gas import variables
    model.ng_terminalImport = Var(model.NaturalGasTerminalsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals, initialize=0)
    
    # Natural gas transmission variables
    model.ng_transmission = Var(model.NaturalGasDirectionalLink, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals, initialize=0)
    
    # Natural gas for power generation
    model.ng_forPower = Var(model.Node, model.NaturalGasGenerators, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Natural gas storage variables
    model.ng_storageOperational = Var(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.ng_chargeStorage = Var(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.ng_dischargeStorage = Var(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
