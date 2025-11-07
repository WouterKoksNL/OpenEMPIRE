"""Heat module operational constraints."""
from pyomo.environ import Constraint


def define_operational_heat_constraints(model):

    # capacity-dependent: to be included in the benders cut
    def ConverterConv_rule(model, n, r, h, i, w, gp):
        return model.ConverterOperational[n,r,h,i,w,gp] - model.ConverterInstalledCap[n,r,i] <= 0
    model.ConverterConv = Constraint(model.ConverterOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=ConverterConv_rule)

    def FlowBalanceTR_rule(model, n, h, i, w, gp):
        return sum(model.genOperational[n,g,h,i,w,gp] for g in model.GeneratorTR if (n,g) in model.GeneratorsOfNode) \
            + sum((model.storageDischargeEff[b]*model.storDischarge[n,b,h,i,w,gp]-model.storCharge[n,b,h,i,w,gp]) for b in model.StorageTR if (n,b) in model.StoragesOfNode) \
            + sum(model.ConverterEff[r]*model.convAvail[n,r,h,w,i]*model.ConverterOperational[n,r,h,i,w,gp] for r in model.Converter if (n,r) in model.ConverterOfNode) \
            - model.sloadTR[n,h,i,w] + model.loadShedTR[n,h,i,w,gp] \
            == 0
    model.FlowBalanceTR = Constraint(model.ThermalDemandNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=FlowBalanceTR_rule)

    def FlowBalanceTRIndustrial_rule(model, n, h, i, w, gp):
        return sum(model.genOperational[n,g,h,i,w,gp] for g in model.GeneratorTR_Industrial if (n,g) in model.GeneratorsOfNode) \
            - model.refinery_heatConsumption * model.oilRefined[n,h,i,w,gp] \
            == 0
    model.FlowBalanceTRIndustrial = Constraint(model.OilProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=FlowBalanceTRIndustrial_rule)


    def shedTR_limit_rule(model,n,h,i,w,gp):
        return model.loadShedTR[n,h,i,w,gp] <= model.sloadTR[n,h,i,w]
    # model.shed_limitTR = Constraint(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=shedTR_limit_rule)

def add_heat_electric_demand(model, flow, n, h, i, w, gp):
    flow += (
                sum(model.genCHPEfficiency[g,i]*model.genOperational[n,g,h,i,w,gp] for g in model.GeneratorEL if (n,g) in model.GeneratorsOfNode)  
            - sum(model.ConverterOperational[n,r,h,i,w,gp] for r in model.Converter if (n,r) in model.ConverterOfNode)
            )
    return flow