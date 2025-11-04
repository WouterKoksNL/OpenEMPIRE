from pyomo.environ import BuildAction, value


def define_hydrogen_investment_expressions(model, LeapYearsInvestment, repurposeCostFactor):
    """Define hydrogen module investment build actions."""
    

    def prepElectrolyzerInvCost_rule(model):
        for i in model.Period:
            costperyear = (model.WACC / (1 - ((1 + model.WACC) ** (1 - model.elyzerLifetime)))) * model.elyzerPlantCapitalCost[i] + model.elyzerFixedOMCost[i]
            costperperiod = costperyear * (1 - (1 + model.discountrate) ** -(min(value((len(model.Period) - i + 1) * LeapYearsInvestment), value(model.elyzerLifetime)))) / (1 - (1 / (1 + model.discountrate)))
            model.elyzerInvCost[i] = costperperiod
    model.build_elyzerInvCost = BuildAction(rule=prepElectrolyzerInvCost_rule)

    def prepReformerPlantInvCost_rule(model):
        for p in model.ReformerPlants:
            for i in model.Period:
                costperyear = (model.WACC/(1-((1+model.WACC)**(1-model.ReformerPlantLifetime[p]))))*model.ReformerPlantsCapitalCost[p,i]+model.ReformerPlantFixedOMCost[p,i]
                costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.ReformerPlantLifetime[p]))))/(1-(1/(1+model.discountrate)))
                model.ReformerPlantInvCost[p,i] = costperperiod
    model.build_ReformerPlantInvCost = BuildAction(rule=prepReformerPlantInvCost_rule)

    def prepH2TerminalInvCost_rule(model):
        for n in model.H2TerminalNodes:
            for t in model.H2Terminals:
                if (n,t) in model.H2TerminalsOfNode:
                    for i in model.Period:
                        costperyear = (model.WACC/(1-((1+model.WACC)**(1-model.H2TerminalLifetime[t]))))*model.H2TerminalCapitalCost[n,t,i]+model.H2TerminalFixedOM[n,t,i]
                        costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.H2TerminalLifetime[t]))))/(1-(1/(1+model.discountrate)))
                        model.H2TerminalInvCost[n,t,i] = costperperiod
    model.build_H2TerminalInvCost = BuildAction(rule=prepH2TerminalInvCost_rule)

    def prepPipelineInvcost_rule(model):
        for i in model.Period:
            for (n1,n2) in model.HydrogenBidirectionPipelines:
                costperyear= (model.WACC/(1-((1+model.WACC)**(1-model.hydrogenPipelineLifetime))))*model.PipelineLength[n1,n2]*(model.hydrogenPipelineCapCost[i]) + model.PipelineLength[n1,n2]*model.hydrogenPipelineOMCost[i]
                costperperiod =costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.hydrogenPipelineLifetime))))/(1-(1/(1+model.discountrate)))
                model.hydrogenPipelineInvCost[n1,n2,i] = costperperiod
    model.build_pipelineInvCost = BuildAction(rule=prepPipelineInvcost_rule)

    def prepRepurposedPipelineInvcost_rule(model):
        for i in model.Period:
            for (n1, n2) in model.RepurposeDirectionalLinks:
                if (n1,n2) in model.HydrogenBidirectionPipelines:
                    costperyear= (model.WACC/(1-((1+model.WACC)**(1-model.hydrogenPipelineLifetime))))*model.PipelineLength[n1,n2]*(model.hydrogenPipelineCapCost[i]) + model.PipelineLength[n1,n2]*model.hydrogenPipelineOMCost[i]
                    costperperiod =costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.hydrogenPipelineLifetime))))/(1-(1/(1+model.discountrate)))
                    model.repurposedPipelineInvCost[n1,n2,i] = costperperiod*repurposeCostFactor
                else:
                    costperyear= (model.WACC/(1-((1+model.WACC)**(1-model.hydrogenPipelineLifetime))))*model.PipelineLength[n2,n1]*(model.hydrogenPipelineCapCost[i]) + model.PipelineLength[n2,n1]*model.hydrogenPipelineOMCost[i]
                    costperperiod =costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.hydrogenPipelineLifetime))))/(1-(1/(1+model.discountrate)))
                    model.repurposedPipelineInvCost[n1,n2,i] = costperperiod*repurposeCostFactor
    model.build_repurposedPipelineInvCost = BuildAction(rule=prepRepurposedPipelineInvcost_rule)

    def prepHydrogenStorageInvcost_rule(model):
        for b in model.H2Storages:
            for i in model.Period:
                costperyear =(model.WACC/(1-((1+model.WACC)**(1-model.hydrogenStorageLifetime[b]))))*model.hydrogenStorageCapitalCost[b,i]+model.hydrogenStorageFixedOMCost[b,i]
                costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.hydrogenStorageLifetime[b]))))/(1-(1/(1+model.discountrate)))
                model.hydrogenStorageInvCost[b,i] = costperperiod
    model.build_hydrogenStorageInvCost = BuildAction(rule=prepHydrogenStorageInvcost_rule)

    def prepCO2InvCosts_rule(model):
        for i in model.Period:
            for (n1,n2) in model.CO2BidirectionalPipelines:
                costperyear = (model.WACC / (1 - ((1 + model.WACC) ** (1-model.CO2PipelineLifetime)))) * model.PipelineLength[n1,n2] * model.CO2PipelineCapCost + model.PipelineLength[n1,n2] * model.CO2PipelineOMCost
                costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.CO2PipelineLifetime))))/(1-(1/(1+model.discountrate)))
                model.CO2PipelineInvCost[n1,n2,i] = costperperiod

            for n in model.CO2SequestrationNodes:
                #Assume infinite lifetime of storage site -> annual cost approaches WACC * capital cost instead of the previous formula for equivalent annual cost
                costperyear = model.WACC * model.CO2StorageSiteCapitalCost[n] + model.StorageSiteFixedOMCost[n]
                costperperiod = costperyear * (1 - (1 + model.discountrate)**-(value((len(model.Period)-i+1)*LeapYearsInvestment)))/(1-(1/(1+model.discountrate)))
                model.CO2StorageSiteInvCost[n,i] = costperperiod
    model.build_CO2InvCosts = BuildAction(rule=prepCO2InvCosts_rule)
