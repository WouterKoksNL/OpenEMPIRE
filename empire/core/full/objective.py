from pyomo.environ import (Expression, Objective, minimize)

SCALING_FACTOR = 1  # scaling factor for reducing objective 

def investment_obj(model):
    return SCALING_FACTOR * sum(model.discount_multiplier[i] * (
        sum(model.genInvCost[g,i]* model.genInvCap[n,g,i] for (n,g) in model.GeneratorsOfNode)
        + sum(model.transmissionInvCost[n1,n2,i]*model.transmissionInvCap[n1,n2,i] for (n1,n2) in model.BidirectionalArc)  
        + sum((model.storPWInvCost[b,i]*model.storPWInvCap[n,b,i]+model.storENInvCost[b,i]*model.storENInvCap[n,b,i]) for (n,b) in model.StoragesOfNode) 
        ) for i in model.PeriodActive 
        ) 

def multiplier_rule(model,period):
    coeff=1
    if period>1:
        coeff=pow(1.0+model.discountrate,(-model.LeapYearsInvestment*(int(period)-1)))
    return coeff

def define_objective(model, include_investment=True, include_operational=True) -> None:
    model.discount_multiplier=Expression(model.PeriodActive, rule=multiplier_rule)

    def Obj_rule(model):
        obj = 0
        if include_investment:
            obj += investment_obj(model)
        if include_operational:
            obj += SCALING_FACTOR * sum(model.discount_multiplier[i] * model.operationalcost[i, w] for i in model.PeriodActive for w in model.Scenario)
        return obj 
    model.Obj = Objective(rule=Obj_rule, sense=minimize)

    return 


if use_cvar:
            returnSum += sum(model.discount_multiplier[i] * ((1 - model.cvar_weight) * model.operationalcost[i] + model.cvar_weight * model.cvar[i]) for i in model.Period)
        else:
            returnSum += sum(model.discount_multiplier[i] * model.operationalcost[i] for i in model.Period)

if hydrogen:
    returnSum += sum(model.discount_multiplier[i]*(
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

if industry:
    returnSum += sum(model.discount_multiplier[i]*(
        sum(model.steel_plantInvCost[p,i] * model.steelPlantBuiltCapacity[n,p,i] for p in model.SteelPlants for n in model.SteelProducers) + \
        sum(model.cement_plantInvCost[p,i] * model.cementPlantBuiltCapacity[n,p,i] for p in model.CementPlants for n in model.CementProducers) + \
        sum(model.ammonia_plantInvCost[p,i] * model.ammoniaPlantBuiltCapacity[n,p,i] for p in model.AmmoniaPlants for n in model.AmmoniaProducers)    
    ) for i in model.Period)

if HEATMODULE:
    returnSum += sum(model.discount_multiplier[i] * (sum(model.ConverterInvCost[r,i] * model.ConverterInvCap[n,r,i] for (n,r) in model.ConverterOfNode)
                                                        ) for i in model.Period)

