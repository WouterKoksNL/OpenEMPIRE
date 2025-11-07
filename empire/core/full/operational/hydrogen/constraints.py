from pyomo.environ import Constraint, value
from empire.core.constants import Constants


def add_hydrogen_electric_demand(model, flow, n, h, i, w, gp):
    """Add hydrogen module's electricity demand to the electric flow.
    
    Args:
        model: Pyomo model
        flow: Current electric flow value
        n, h, i, w, gp: Indices for node, hour, period, scenario, gas scenario
        
    Returns:
        Updated flow with hydrogen electricity demands subtracted
    """
    if n not in model.HydrogenProdNode:
        return flow
    
    # Electrolyzer power consumption
    flow -= model.powerForHydrogen[n, h, i, w, gp]
    
    # Hydrogen pipeline compressor power (split 50/50 between sending and receiving nodes)
    for n2 in model.HydrogenLinks[n]:
        if (n, n2) in model.HydrogenBidirectionPipelines:
            flow -= 0.5 * model.hydrogenPipelinePowerDemandPerTon[n, n2] * (
                model.hydrogenSentPipeline[n, n2, h, i, w, gp] + 
                model.hydrogenSentPipeline[n2, n, h, i, w, gp])
        elif (n2, n) in model.HydrogenBidirectionPipelines:
            flow -= 0.5 * model.hydrogenPipelinePowerDemandPerTon[n2, n] * (
                model.hydrogenSentPipeline[n, n2, h, i, w, gp] + 
                model.hydrogenSentPipeline[n2, n, h, i, w, gp])
    
    # CO2 pipeline compressor power (split 50/50 between sending and receiving nodes)
    for n2 in model.CO2Links[n]:
        if (n, n2) in model.CO2BidirectionalPipelines:
            flow -= 0.5 * model.CO2PipelinePowerDemandPerTon[n, n2] * (
                model.CO2sentPipeline[n, n2, h, i, w, gp] + 
                model.CO2sentPipeline[n2, n, h, i, w, gp])
        elif (n2, n) in model.CO2BidirectionalPipelines:
            flow -= 0.5 * model.CO2PipelinePowerDemandPerTon[n2, n] * (
                model.CO2sentPipeline[n, n2, h, i, w, gp] + 
                model.CO2sentPipeline[n2, n, h, i, w, gp])
    
    # Reformer electricity use
    if n in model.ReformerLocations:
        flow -= sum(model.ReformerPlantElectricityUse[p, i] * 
                   model.hydrogenProducedReformer_ton[n, p, h, i, w, gp] 
                   for p in model.ReformerPlants)
    
    return flow


def add_hydrogen_transport_electric_demand(model, flow, n, h, i, w, gp):
    """Add hydrogen transport's electricity demand to the electric flow.
    
    Args:
        model: Pyomo model
        flow: Current electric flow value
        n, h, i, w, gp: Indices for node, hour, period, scenario, gas scenario
        
    Returns:
        Updated flow with transport electricity demands subtracted
    """
    if n in model.OnshoreNode:
        flow -= model.transport_electricityDemandMet[n, h, i, w, gp]
    
    return flow


def define_operational_hydrogen_constraints(model, industry_flag, transport_flag=False):
    
    # Constraints relevant for Benders cuts:
    
    def hydrogen_storage_initial_rule(model, n, b, h, i, w, gp):
        """Set the initial hydrogen storage level at the start of each season."""
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return (
                model.hydrogenStorageOperational[n, b, h, i, w, gp]
                == model.hydrogenStorageInitOperational * model.hydrogenTotalStorage[n, b, i]
                + model.hydrogenChargeStorage[n, b, h, i, w, gp]
                - model.hydrogenDischargeStorage[n, b, h, i, w, gp]
            )
        return Constraint.Skip

    model.hydrogen_storage_initial = Constraint(
        model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period,
        model.Scenario, model.GasScenario,
        rule=hydrogen_storage_initial_rule
    )

    def hydrogen_production_electrolyzer_capacity_rule(model, n, h, i, w, gp):
        return model.powerForHydrogen[n, h, i, w, gp] <= model.elyzerTotalCap[n, i]

    model.hydrogen_production_electrolyzer_capacity = Constraint(model.HydrogenProdNode, model.Operationalhour,
                                                                    model.Period, model.Scenario, model.GasScenario,
                                                                    rule=hydrogen_production_electrolyzer_capacity_rule)

    def hydrogen_production_reformer_capacity_rule(model, n, p, h, i, w, gp):
        return model.hydrogenProducedReformer_MWh[n, p, h, i, w, gp] <= model.ReformerTotalCap[n, p, i]

    model.hydrogen_production_reformer_capacity = Constraint(model.ReformerLocations, model.ReformerPlants,
                                                                model.Operationalhour, model.Period, model.Scenario,
                                                                model.GasScenario,
                                                                rule=hydrogen_production_reformer_capacity_rule)

    def hydrogen_reformer_ramp_rule(model, n, p, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return Constraint.Skip
        else:
            return model.hydrogenProducedReformer_MWh[n, p, h, i, w, gp] - model.hydrogenProducedReformer_MWh[
                n, p, h - 1, i, w, gp] <= 0.1 * model.ReformerTotalCap[n, p, i]

    model.hydrogen_reformer_ramp = Constraint(model.ReformerLocations, model.ReformerPlants, model.Operationalhour,
                                                model.Period, model.Scenario, model.GasScenario,
                                                rule=hydrogen_reformer_ramp_rule)

    
    def pipeline_cap_rule(model, n1, n2, h, i, w, gp):
        if (n1, n2) in model.HydrogenBidirectionPipelines:
            return model.hydrogenSentPipeline[(n1, n2), h, i, w, gp] - model.totalHydrogenPipelineCapacity[
                (n1, n2), i] <= 0
        elif (n2, n1) in model.HydrogenBidirectionPipelines:
            return model.hydrogenSentPipeline[(n1, n2), h, i, w, gp] - model.totalHydrogenPipelineCapacity[
                (n2, n1), i] <= 0
        else:
            print('Problem creating max pipeline capacity constraint for nodes ' + n1 + ' and ' + n2)
            exit()

    model.pipeline_cap = Constraint(model.AllowedHydrogenLinks, model.Operationalhour, model.Period, model.Scenario,
                                    model.GasScenario, rule=pipeline_cap_rule)

                                    
    def co2_pipeline_cap_rule(model, n1, n2, h, i, w, gp):
        if (n1, n2) in model.CO2BidirectionalPipelines:
            return model.CO2sentPipeline[(n1, n2), h, i, w, gp] - model.totalCO2PipelineCapacity[(n1, n2), i] <= 0
        elif (n2, n1) in model.CO2BidirectionalPipelines:
            return model.CO2sentPipeline[(n1, n2), h, i, w, gp] - model.totalCO2PipelineCapacity[(n2, n1), i] <= 0

    model.co2_pipeline_cap = Constraint(model.CO2DirectionalLinks, model.Operationalhour, model.Period, model.Scenario,
                                        model.GasScenario, rule=co2_pipeline_cap_rule)
    
    def co2_sequestering_max_hourly_capacity_rule(model, n, h, i, w, gp):
        return model.CO2sequestered[n, h, i, w, gp] <= sum(
            model.CO2SiteCapacityDeveloped[n, j] for j in model.Period if j <= i)

    model.co2_sequestering_max_capacity = Constraint(model.CO2SequestrationNodes, model.Operationalhour, model.Period,
                                                    model.Scenario, model.GasScenario,
                                                    rule=co2_sequestering_max_hourly_capacity_rule)


    # Constraints with no relevance to Benders cuts: 

    def naturalGas_for_hydrogen_rule(model, n, p, h, i, w, gp):
        return model.ng_forHydrogen[n,p,h,i,w,gp] * Constants.ng_MWhPerTon == model.hydrogenProducedReformer_MWh[n,p,h,i,w,gp] / model.ReformerPlantEfficiency[p,i]
    model.naturalGas_for_hydrogen = Constraint(model.ReformerLocations, model.ReformerPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_for_hydrogen_rule)

    def powerFromHydrogenRule(model, n, g, h, i, w, gp):
        if g in model.HydrogenGenerators:
            return model.genOperational[n,g,h,i,w,gp] == model.genEfficiency[g,i] * model.hydrogenForPower[g,n,h,i,w,gp] * Constants.hydrogen_MWhPerTon
        else:
            return Constraint.Skip

    model.powerFromHydrogen = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=powerFromHydrogenRule)


    def hydrogen_flow_balance_rule(model, n, h, i, w, gp):
        balance = 0
        balance += sum(
            model.hydrogenSentPipeline[(n2, n), h, i, w, gp] - model.hydrogenSentPipeline[(n, n2), h, i, w, gp] for
            n2 in model.HydrogenLinks[n])
        balance -= sum(model.hydrogenForPower[g, n, h, i, w, gp] for g in model.HydrogenGenerators)
        balance += sum(model.hydrogenDischargeStorage[n, b, h, i, w, gp] - model.hydrogenChargeStorage[n, b, h, i, w, gp] for b in model.H2Storages)
        if industry_flag and n in model.SteelProducers:
            balance -= sum(
                model.steel_hydrogenConsumption[p, i] / 1e3 * model.steelProduced[n, p, h, i, w, gp] for p in
                model.SteelPlants)
        if industry_flag and n in model.CementProducers:
            balance -= sum(
                model.cement_fuelConsumption[p, i] / 1e3 * model.cementProduced[n, p, h, i, w, gp] for p in
                model.CementPlants if 'H2' in p)
        if industry_flag and n in model.AmmoniaProducers:
            balance -= sum(
                model.ammonia_fuelConsumption[p] / 1e3 * model.ammoniaProduced[n, p, h, i, w, gp] for p in
                model.AmmoniaPlants if 'H2' in p)
        if industry_flag and n in model.OilProducers:
            balance -= model.refinery_hydrogenConsumption * model.oilRefined[n, h, i, w, gp]
        if n in model.HydrogenProdNode:
            balance += model.hydrogenProducedElectro_ton[n, h, i, w, gp]
        if n in model.ReformerLocations:
            balance += sum(model.hydrogenProducedReformer_ton[n, p, h, i, w, gp] for p in model.ReformerPlants)
        if n in model.OnshoreNode:
            balance -= model.transport_hydrogenDemandMet[n, h, i, w, gp]
            # balance -= sum(model.transport_energyConsumption[v,i] / Constants.hydrogen_MWhPerTon * model.transportDemandMet[n,v,h,i,w,gp] for v in model.VehicleTypes if ('hydrogen' in v.lower() or 'fuelcell' in v.lower()))
        if n in model.H2TerminalNodes:
            balance += sum(model.H2Imported_ton[n, t, h, i, w, gp] for t in model.H2Terminals if (n,t) in model.H2TerminalsOfNode)
        return balance == 0
    model.hydrogen_flow_balance = Constraint(model.HydrogenProdNode, model.Operationalhour, model.Period,
                                                model.Scenario, model.GasScenario, rule=hydrogen_flow_balance_rule)

    def hydrogen_production_rule(model, n, h, i, w, gp):
        return model.hydrogenProducedElectro_ton[n, h, i, w, gp] == model.powerForHydrogen[n, h, i, w, gp] / \
            model.elyzerPowerConsumptionPerTon[i]

    model.hydrogen_production = Constraint(model.HydrogenProdNode, model.Operationalhour, model.Period,
                                            model.Scenario, model.GasScenario, rule=hydrogen_production_rule)


    def hydrogen_link_reformer_ton_MWh_rule(model, n, p, h, i, w, gp):
        return model.hydrogenProducedReformer_ton[n, p, h, i, w, gp] == model.hydrogenProducedReformer_MWh[
            n, p, h, i, w, gp] / Constants.hydrogen_MWhPerTon

    model.hydrogen_link_reformer_ton_MWh = Constraint(model.ReformerLocations, model.ReformerPlants,
                                                        model.Operationalhour, model.Period, model.Scenario,
                                                        model.GasScenario, rule=hydrogen_link_reformer_ton_MWh_rule)

    

    def H2import_capacity_rule(model, n, t, h, i, w, gp):
        return model.H2Imported_ton[n, t, h, i, w, gp] <= model.H2ImportTotalCap[n, t, i]
    model.H2import_capacity = Constraint(model.H2TerminalsOfNode, model.Operationalhour, model.Period, model.Scenario,
                                            model.GasScenario, rule=H2import_capacity_rule)
    # def noHydrogenPowerRule(model,n,g,h,i,w,gp):
    #     if g in model.HydrogenGenerators:
    #         return model.hydrogenForPower[g,n,h,i,w,gp] == 0
    #     else:
    #         return Constraint.Skip
    # model.noHydrogenPower = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=noHydrogenPowerRule)

    # Commented out this constraint, because we initialize model.hydrogenForPower to 0 in the variable definition.
    # Early testing suggests that this is enough (all generators other than hydrogen generators have their associated
    # hydrogenForPower set to 0. Will not fully delete the constraint (yet) in case other results suggest we need to
    # explicitly limit hydrogenForPower for non-hydrogen generators.

    # def hydrogenToGenerator_rule(model,n,g,h,i,w,gp):
    # 	if n in model.HydrogenProdNode and g not in model.HydrogenGenerators:
    # 		return model.hydrogenForPower[g,n,h,i,w,gp]==0
    # 	else:
    # 		return Constraint.Skip
    # model.hydrogenToGenerator = Constraint(model.GeneratorsOfNode,model.Operationalhour,model.Period,model.Scenario, model.GasScenario, rule=hydrogenToGenerator_rule)

    # def meet_hydrogen_demand_rule(model,n,i,w,gp):
    # 	return sum(model.seasScale[s] * model.hydrogenSold[n,h,i,w,gp] for (s,h) in model.HoursOfSeason) >= model.hydrogenDemand[n,i]
    # model.meet_hydrogen_demand = Constraint(model.HydrogenProdNode, model.Period, model.Scenario, model.GasScenario, rule=meet_hydrogen_demand_rule)



    def hydrogen_storage_balance_rule(model, n, b, h, i, w, gp):
        """Ensure hydrogen storage continuity between consecutive hours (excluding season starts)."""
        if h not in model.FirstHoursOfRegSeason and h not in model.FirstHoursOfPeakSeason:
            return (
                model.hydrogenStorageOperational[n, b, h, i, w, gp]
                == model.hydrogenStorageOperational[n, b, h - 1, i, w, gp]
                + model.hydrogenChargeStorage[n, b, h, i, w, gp]
                - model.hydrogenDischargeStorage[n, b, h, i, w, gp]
            )
        return Constraint.Skip

    model.hydrogen_storage_balance = Constraint(
        model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period,
        model.Scenario, model.GasScenario,
        rule=hydrogen_storage_balance_rule
    )

    def hydrogen_storage_operational_capacity_rule(model, n, b, h, i, w, gp):
        return model.hydrogenStorageOperational[n, b, h, i, w, gp] <= model.hydrogenTotalStorage[n, b, i]

    model.hydrogen_storage_operational_capacity = Constraint(model.HydrogenProdNode, model.H2Storages, model.Operationalhour,
                                                                model.Period, model.Scenario, model.GasScenario,
                                                                rule=hydrogen_storage_operational_capacity_rule)

    def hydrogen_balance_storage_rule(model, n, b, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason:
            return model.hydrogenStorageOperational[
                n, b, h + value(model.length_reg_season) - 1, i, w, gp] - model.hydrogenStorageInitOperational * \
                model.hydrogenTotalStorage[n, b, i] == 0
        elif h in model.FirstHoursOfPeakSeason:
            return model.hydrogenStorageOperational[
                n, b, h + value(model.length_peak_season) - 1, i, w, gp] - model.hydrogenStorageInitOperational * \
                model.hydrogenTotalStorage[n, b, i] == 0
        else:
            return Constraint.Skip

    model.hydrogen_balance_storage = Constraint(model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period,
                                                model.Scenario, model.GasScenario,
                                                rule=hydrogen_balance_storage_rule)


    def H2import_link_ton_MWh_rule(model, n, t, h, i, w, gp):
        if (n, t) in model.H2TerminalsOfNode:
            return model.H2Imported_ton[n, t, h, i, w, gp] == model.H2Imported_MWh[n, t, h, i, w, gp] / Constants.hydrogen_MWhPerTon
        else:
            return Constraint.Skip
    model.H2import_link_ton_MWh = Constraint(model.H2TerminalNodes, model.H2Terminals, model.Operationalhour, model.Period, model.Scenario,
                                                model.GasScenario, rule=H2import_link_ton_MWh_rule)
    


    def co2_flow_balance_rule(model, n, h, i, w, gp):
        balance = 0
        balance += model.co2_captured_generators[n, h, i, w, gp]
        if industry_flag:
            balance += model.co2_captured_industry[n, h, i, w, gp]
        if n in model.ReformerLocations:
            balance += model.co2_captured_reformers[n, h, i, w, gp]
        balance += sum(model.CO2sentPipeline[n2, n, h, i, w, gp] - model.CO2sentPipeline[n, n2, h, i, w, gp] for n2 in
                    model.OnshoreNode if (n, n2) in model.CO2DirectionalLinks)
        if n in model.CO2SequestrationNodes:
            balance -= model.CO2sequestered[n, h, i, w, gp]
        return balance == 0

    model.co2_flow_balance = Constraint(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario,
                                        model.GasScenario, rule=co2_flow_balance_rule)


    def co2_max_total_sequestration_capacity_rule(model, n, w, gp):
        return sum(model.leap_years_investment * model.seasScale[s] * model.CO2sequestered[n, h, i, w, gp] for (s, h) in
                model.HoursOfSeason for i in model.Period) / 1e4 <= model.maxSequestrationCapacity[n] / 1e4

    model.co2_max_total_sequestration_capacity = Constraint(model.CO2SequestrationNodes, model.Scenario,
                                                            model.GasScenario,
                                                            rule=co2_max_total_sequestration_capacity_rule)

    # Transport demand constraints
    if transport_flag:
        def meet_transport_elec_demand_rule(model,n,i,w,gp):
            return sum(model.seasScale[s] * (model.transport_electricityDemandMet[n,h,i,w,gp] + model.transport_electricityDemandShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.transport_electricity_demand[n,i]
        model.meet_transport_elec_demand = Constraint(model.OnshoreNode, model.Period, model.Scenario, model.GasScenario, rule=meet_transport_elec_demand_rule)

        def meet_transport_hydrogen_demand_rule(model,n,i,w,gp):
            return sum(model.seasScale[s] * (model.transport_hydrogenDemandMet[n,h,i,w,gp] + model.transport_hydrogenDemandShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.transport_hydrogen_demand[n,i] / Constants.hydrogen_MWhPerTon
        model.meet_transport_hydrogen_demand = Constraint(model.OnshoreNode, model.Period, model.Scenario, model.GasScenario, rule=meet_transport_hydrogen_demand_rule)

        def meet_transport_naturalGas_demand_rule(model,n,i,w,gp):
            return sum(model.seasScale[s] * (model.transport_naturalGasDemandMet[n,h,i,w,gp] + model.transport_naturalGasDemandShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.transport_naturalGas_demand[n,i] / Constants.ng_MWhPerTon
        model.meet_transport_naturalGas_demand = Constraint(model.OnshoreNode, model.Period, model.Scenario, model.GasScenario, rule=meet_transport_naturalGas_demand_rule)


