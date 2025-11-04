from pyomo.environ import Var, NonNegativeReals, AbstractModel

def define_heat_investment_variables(model: AbstractModel):
    model.ConverterInvCap = Var(model.ConverterOfNode, model.Period, domain=NonNegativeReals)
    model.ConverterInstalledCap = Var(model.ConverterOfNode, model.Period, domain=NonNegativeReals)
