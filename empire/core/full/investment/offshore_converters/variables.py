
from pyomo.environ import Var, NonNegativeReals, AbstractModel

def define_offshore_converter_investment_variables(model: AbstractModel):

    # GD Offshore converter capacity built in period i and total capacity installed
    model.offshoreConvInvCap = Var(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
    model.offshoreConvInstalledCap = Var(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
