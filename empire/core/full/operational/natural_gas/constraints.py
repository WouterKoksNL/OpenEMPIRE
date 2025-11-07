from pyomo.environ import Constraint, value
from empire.core.constants import Constants

def add_natural_gas_electric_demand(model, flow, n, h, i, w, gp):
    # Natural gas module contribution (always active)
    if n in model.NaturalGasNode:
        flow -= sum(model.ng_pipelinePowerDemandPerTon * model.ng_transmission[n,n2,h,i,w,gp] for n2 in model.NaturalGasNode if (n,n2) in model.NaturalGasDirectionalLink)
    return flow

def define_operational_natural_gas_constraints(model, leap_years_investment, hydrogen, industry):
    """Defines the operational constraints for natural gas in the model.
    No constraints relevant for Benders. """



    def naturalGas_terminal_capacity_rule(model, n, t, h, i, w, gp):
        return model.ng_terminalImport[n,t,h,i,w,gp] <= model.ng_terminalCapacity[n,t,i]
    model.naturalGas_terminal_capacity = Constraint(model.NaturalGasTerminalsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_terminal_capacity_rule)

    def naturalGas_max_reserves_rule(model, n, t, w, gp):
        if (n,t) in model.NaturalGasTerminalsOfNode and ("domesticproduction" in t.lower() or 'pipelineimport' in t.lower()):
            return sum(leap_years_investment * model.seasScale[s] * model.ng_terminalImport[n,t,h,i,w,gp] for (s,h) in model.HoursOfSeason for i in model.Period if (n,t) in model.NaturalGasTerminalsOfNode) / 1e3 <= model.ng_reserves[n] / 1e3
        else:
            return Constraint.Skip
    model.naturalGas_max_reserves = Constraint(model.NaturalGasNode, model.NaturalGasTerminals, model.Scenario, model.GasScenario, rule=naturalGas_max_reserves_rule)
    
    def naturalGas_storage_initial_rule(model, n, h, i, w, gp):
        """Set the initial storage level at the start of each season."""
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return (
                model.ng_storageOperational[n, h, i, w, gp] 
                == model.ng_storageInit * model.ng_storageCapacity[n]
                + model.ng_storageChargeEff * model.ng_chargeStorage[n, h, i, w, gp]
                - model.ng_dischargeStorage[n, h, i, w, gp]
            ) / 1e3
        return Constraint.Skip

    model.naturalGas_storage_initial = Constraint(
        model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario,
        rule=naturalGas_storage_initial_rule
    )

    def naturalGas_storage_balance_rule(model, n, h, i, w, gp):
        """Ensure storage continuity between consecutive hours (excluding season starts)."""
        if h not in model.FirstHoursOfRegSeason and h not in model.FirstHoursOfPeakSeason:
            return (
                model.ng_storageOperational[n, h, i, w, gp]
                == model.ng_storageOperational[n, h-1, i, w, gp]
                + model.ng_storageChargeEff * model.ng_chargeStorage[n, h, i, w, gp]
                - model.ng_dischargeStorage[n, h, i, w, gp]
            ) / 1e3
        return Constraint.Skip

    model.naturalGas_storage_balance = Constraint(
        model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario,
        rule=naturalGas_storage_balance_rule
    )

    def naturalGas_Storage_maxCapacity_rule(model, n, h, i, w, gp):
        return model.ng_storageOperational[n,h,i,w,gp] / 1e3 <= model.ng_storageCapacity[n] / 1e3
    model.naturalGas_storage_maxCapacity = Constraint(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_Storage_maxCapacity_rule)

    def naturalGas_pipeline_capacity_rule(model,n,n2,h,i,w,gp):
        if (n,n2) in model.NaturalGasDirectionalLink:
            if (n,n2) in model.RepurposeDirectionalLinks:
                return model.ng_transmission[n,n2,h,i,w,gp] + sum(model.repurposedPipelineBuilt[n,n2,j] for j in range(1,i+1)) <= model.ng_pipelineCapacity[n,n2]
            else:
                return model.ng_transmission[n,n2,h,i,w,gp] <= model.ng_pipelineCapacity[n,n2]
        else:
            return Constraint.Skip
    model.naturalGas_pipeline_capacity = Constraint(model.NaturalGasNode, model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_pipeline_capacity_rule)

    def naturalGas_net_zero_seasonal_storage_rule(model, n, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason:
            return (model.ng_storageOperational[n,h+value(model.length_reg_season)-1,i,w,gp] - model.ng_storageInit * model.ng_storageCapacity[n]) /1e3 == 0
        elif h in model.FirstHoursOfPeakSeason:
            return (model.ng_storageOperational[n,h+value(model.length_peak_season)-1,i,w,gp] - model.ng_storageInit * model.ng_storageCapacity[n]) / 1e3 == 0
        else:
            return Constraint.Skip
    model.naturalGas_net_zero_seasonal_storage = Constraint(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_net_zero_seasonal_storage_rule)

    def naturalGas_flow_balance_rule(model, n, h, i, w, gp):
        returnSum = 0
        returnSum -= sum(model.ng_forPower[n,g,h,i,w,gp] for g in model.NaturalGasGenerators if (n,g) in model.GeneratorsOfNode)
        if hydrogen:
            if n in model.ReformerLocations:
                returnSum -= sum(model.ng_forHydrogen[n,p,h,i,w,gp] for p in model.ReformerPlants)
        returnSum -= model.ng_chargeStorage[n,h,i,w,gp]
        returnSum += model.ng_storageDischargeEff * model.ng_dischargeStorage[n,h,i,w,gp]
        returnSum -= sum(model.ng_transmission[n,n2,h,i,w,gp] for n2 in model.Node if (n,n2) in model.NaturalGasDirectionalLink)
        returnSum += sum(model.ng_transmission[n2,n,h,i,w,gp] for n2 in model.Node if (n2,n) in model.NaturalGasDirectionalLink)
        returnSum += sum(model.ng_terminalImport[n,t,h,i,w,gp] for t in model.NaturalGasTerminals if (n,t) in model.NaturalGasTerminalsOfNode)

        if industry and n in model.CementProducers:
            returnSum -= sum(model.cement_fuelConsumption[p,i] /1000 * model.cementProduced[n,p,h,i,w,gp] for p in model.CementPlants if 'NG' in p)
        if industry and n in model.AmmoniaProducers:
            returnSum -= sum(model.ammonia_fuelConsumption[p] / 1000 * model.ammoniaProduced[n,p,h,i,w,gp] for p in model.AmmoniaPlants if 'NG' in p)
        if n in model.OnshoreNode:
            returnSum -= model.transport_naturalGasDemandMet[n,h,i,w,gp]
        return returnSum == 0
    model.naturalGas_flow_balance = Constraint(model.NaturalGasNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_flow_balance_rule)
    

    
    def naturalGas_for_power_rule(model, n, g, h, i, w, gp):
        if (n,g) in model.GeneratorsOfNode:
            return model.ng_forPower[n,g,h,i,w,gp] * Constants.ng_MWhPerTon == model.genOperational[n,g,h,i,w,gp] / model.genEfficiency[g,i]
        else:
            return Constraint.Skip
    model.naturalGas_for_power = Constraint(model.NaturalGasNode, model.NaturalGasGenerators, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=naturalGas_for_power_rule)

    return 