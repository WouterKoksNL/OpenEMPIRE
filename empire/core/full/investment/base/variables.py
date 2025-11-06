from pyomo.environ import Var, NonNegativeReals, AbstractModel

def define_base_investment_variables(model: AbstractModel, offshore_wind=True):
    model.genInvCap = Var(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
    model.transmissionInvCap = Var(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
    model.storPWInvCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.storENInvCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.genInstalledCap = Var(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
    model.transmissionInstalledCap = Var(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
    model.storPWInstalledCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.storENInstalledCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)

    if offshore_wind:
        # GD Offshore converter capacity built in period i and total capacity installed
        model.offshoreConvInvCap = Var(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
        model.offshoreConvInstalledCap = Var(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
    