from pyomo.environ import Expression, AbstractModel, BuildAction


def define_hydrogen_operational_expressions(model: AbstractModel):
    def prep_CO2_storage_cost(model, i):
        return sum(model.CO2StorageSiteInvCost[n,i] * model.CO2SiteCapacityDeveloped[n,i] for n in model.CO2SequestrationNodes)
    model.co2_storage_site_development_cost = Expression(model.Period, rule=prep_CO2_storage_cost)

    def CO2_captured_generators_rule(model, n, h, i, w, gp):
        return sum(model.genCO2Captured[g] * model.genOperational[n,g,h,i,w,gp] * 3.6 / model.genEfficiency[g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode)
    model.co2_captured_generators = Expression(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=CO2_captured_generators_rule)

    def CO2_captured_reformers_rule(model, n, h, i, w, gp):
        return sum(model.ReformerCO2CaptureFactor[r,i] * model.hydrogenProducedReformer_ton[n,r,h,i,w,gp] for r in model.ReformerPlants)
    model.co2_captured_reformers = Expression(model.ReformerLocations, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=CO2_captured_reformers_rule)

    def reformer_operational_cost_rule(model, i, w, gp):
        return sum(model.operationalDiscountrate*model.seasScale[s]*model.ReformerMargCost[p,i]*model.hydrogenProducedReformer_ton[n,p,h,i,w,gp] for p in model.ReformerPlants for n in model.ReformerLocations for (s,h) in model.HoursOfSeason)
    model.reformerOperationalCost = Expression(model.Period, model.Scenario, model.GasScenario, rule=reformer_operational_cost_rule)

    def H2TerminalImportCost_rule(model, i, w, gp):
        return sum(model.operationalDiscountrate * model.seasScale[s] * model.H2TerminalMargCost[n, t, i] *
                    model.H2Imported_ton[n, t, h, i, w, gp] for t in model.H2Terminals for n in model.H2TerminalNodes if (n,t) in model.H2TerminalsOfNode for (s, h) in model.HoursOfSeason)
    model.H2TerminalImportCost = Expression(model.Period, model.Scenario, model.GasScenario, rule=H2TerminalImportCost_rule)

    def reformer_emissions_rule(model,i,w, gp): #Calculates tons of CO2 emissions per ton H2 produced with Reformer
        return sum(model.seasScale[s]*model.hydrogenProducedReformer_ton[n,p,h,i,w,gp]*model.ReformerEmissionFactor[p,i] for (s,h) in model.HoursOfSeason for n in model.ReformerLocations for p in model.ReformerPlants)
    model.reformerEmissions = Expression(model.Period, model.Scenario, model.GasScenario, rule=reformer_emissions_rule)

    def transport_load_shed_rule(model,i,w,gp):
        transport_shed_cost = sum(model.seasScale[s] * model.transport_curtail_cost * (model.transport_electricityDemandShed[n,h,i,w,gp] + model.transport_naturalGasDemandShed[n,h,i,w,gp] + model.transport_hydrogenDemandShed[n,h,i,w,gp]) for n in model.OnshoreNode for (s,h) in model.HoursOfSeason)
        return model.operationalDiscountrate * transport_shed_cost
    model.transport_load_shed_cost = Expression(model.Period, model.Scenario, model.GasScenario, rule=transport_load_shed_rule)


    def prepReformerMargCost_rule(model):
        for p in model.ReformerPlants:
            for i in model.Period:
                model.ReformerMargCost[p,i] = model.ReformerPlantVarOMCost[p,i]
    model.build_ReformerMargCost = BuildAction(rule=prepReformerMargCost_rule)

    #Converting price from €/kg to €/ton
    def prepH2TerminalMargCost_rule(model):
        for n in model.H2TerminalNodes:
            for t in model.H2Terminals:
                if (n,t) in model.H2TerminalsOfNode:
                    for i in model.Period:
                        model.H2TerminalMargCost[n,t,i] = model.H2TerminalPrice[n,t,i] * 1e3
    model.build_H2TerminalMargCost = BuildAction(rule=prepH2TerminalMargCost_rule)

    def prepHydrogenCompressorElectricityUsage_rule(model):
        for (n1,n2) in model.HydrogenBidirectionPipelines:
            model.hydrogenPipelinePowerDemandPerTon[n1,n2] = model.PipelineLength[n1,n2] * model.hydrogenPipelineCompressorElectricityUsage
    model.build_hydrogenPipelineCompressorPowerDemand = BuildAction(rule=prepHydrogenCompressorElectricityUsage_rule)

    def prep_CO2PipelinePowerUse(model):
        for (n1,n2) in model.CO2BidirectionalPipelines:
            model.CO2PipelinePowerDemandPerTon[n1,n2] = model.CO2PipelineElectricityUsage
    model.build_co2_pipeline_power_use = BuildAction(rule=prep_CO2PipelinePowerUse)
