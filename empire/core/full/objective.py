from pyomo.environ import (Expression, Objective, minimize)

from empire.core.config import EmpireConfiguration

SCALING_FACTOR = 1  # scaling factor for reducing objective 

def investment_obj(model, hydrogen_flag, industry_flag, heat_flag):
    investment_costs = sum(model.discount_multiplier[i] * (
        sum(model.genInvCost[g,i]* model.genInvCap[n,g,i] for (n,g) in model.GeneratorsOfNode)
        + sum(model.transmissionInvCost[n1,n2,i]*model.transmissionInvCap[n1,n2,i] for (n1,n2) in model.BidirectionalArc)  
        + sum((model.storPWInvCost[b,i]*model.storPWInvCap[n,b,i]+model.storENInvCost[b,i]*model.storENInvCap[n,b,i]) for (n,b) in model.StoragesOfNode) 
        ) for i in model.Period
        )

    if hydrogen_flag:
        investment_costs += sum(model.discount_multiplier[i]*(
                sum(model.elyzerInvCost[i] * model.elyzerCapBuilt[n,i] for n in model.HydrogenProdNode) + \
                sum(model.hydrogenPipelineInvCost[n1,n2,i] * model.hydrogenPipelineBuilt[n1,n2,i] for (n1,n2) in model.HydrogenBidirectionPipelines) + \
                sum(model.repurposedPipelineInvCost[n1, n2, i] *
                    model.repurposedPipelineBuilt[n1, n2, i] for (n1, n2) in
                    model.RepurposeDirectionalLinks) + \
                sum(model.ReformerPlantInvCost[p,i] * model.ReformerCapBuilt[n,p,i] for n in model.ReformerLocations for p in model.ReformerPlants) + \
                sum(model.hydrogenStorageInvCost[b,i] * model.hydrogenStorageBuilt[n,b,i] for n in model.HydrogenProdNode for b in model.H2Storages) + \
                sum(model.CO2PipelineInvCost[n1,n2,i] * model.CO2PipelineBuilt[n1,n2,i] for (n1,n2) in model.CO2BidirectionalPipelines) + \
                model.co2_storage_site_development_cost[i] + \
                sum(model.H2TerminalInvCost[n,t,i] * model.H2ImportCapBuilt[n,t,i] for (n,t) in model.H2TerminalsOfNode)
            ) for i in model.Period)

    if industry_flag:
        investment_costs += sum(model.discount_multiplier[i]*(
            sum(model.steel_plantInvCost[p,i] * model.steelPlantBuiltCapacity[n,p,i] for p in model.SteelPlants for n in model.SteelProducers) + \
            sum(model.cement_plantInvCost[p,i] * model.cementPlantBuiltCapacity[n,p,i] for p in model.CementPlants for n in model.CementProducers) + \
            sum(model.ammonia_plantInvCost[p,i] * model.ammoniaPlantBuiltCapacity[n,p,i] for p in model.AmmoniaPlants for n in model.AmmoniaProducers)    
        ) for i in model.Period)

    if heat_flag:
        investment_costs += sum(model.discount_multiplier[i] * (sum(model.ConverterInvCost[r,i] * model.ConverterInvCap[n,r,i] for (n,r) in model.ConverterOfNode)
                                                            ) for i in model.Period)
    return investment_costs


def multiplier_rule(model,period):
    coeff=1
    if period>1:
        coeff=pow(1.0+model.discount_rate,(-model.leap_years_investment*(int(period)-1)))
    return coeff

def define_objective(model, empire_config: EmpireConfiguration, include_investment=True, include_operational=True) -> None:
    model.discount_multiplier=Expression(model.Period, rule=multiplier_rule)

    def Obj_rule(model):
        obj = 0
        if include_investment:
            obj += investment_obj(model, empire_config.hydrogen_flag, empire_config.industry_flag, empire_config.heat_flag)
        if include_operational:
            expected_costs = sum(model.discount_multiplier[i] * model.operational_cost_scenario[i, w, gp] for i in model.Period for w in model.Scenario for gp in model.GasScenario)

            if empire_config.cvar_flag:
                 obj += (1 - model.cvar_weight) * expected_costs + model.cvar_weight * sum(model.discount_multiplier[i] * model.cvar[i] for i in model.Period)
            else:
                obj += expected_costs
        obj = obj * SCALING_FACTOR
        return obj 
    
    model.Obj = Objective(rule=Obj_rule, sense=minimize)

    return 

