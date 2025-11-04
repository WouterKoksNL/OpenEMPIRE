from pyomo.environ import Expression, BuildAction, value
from constants import Constants

from empire_types import Flags

from hydrogen.operational.constraints import add_hydrogen_electric_demand, add_hydrogen_transport_electric_demand
from industry.operational.constraints import add_industry_electric_demand
from heat.operational.constraints import add_heat_electric_demand
from natural_gas.constraints import add_natural_gas_electric_demand

def define_base_operational_build_actions(
        model,
        lengthRegSeason, 
        NoOfRegSeason, 
        lengthPeakSeason, 
        NoOfPeakSeason, 
        LeapYearsInvestment, 
        result_file_path, 
        flags: Flags
        ):
    """Define BuildActions that must be executed before expressions that depend on them."""
     
    def prepSceProbab_rule(model):
        #Build an equiprobable probability distribution for scenarios
        for sce in model.Scenario:
            model.sceProbab[sce] = value(1/len(model.Scenario))

    model.build_SceProbab = BuildAction(rule=prepSceProbab_rule)

    def prepGasSceProbab_rule(model):
        #Build an equiprobable probability distribution for gas scenarios
        # Each gas price scenario is equally likely
        for gp in model.GasScenario:
            model.GasSceProbab[gp] = value(1/len(model.GasScenario))

    model.build_GasSceProbab = BuildAction(rule=prepGasSceProbab_rule)

    def prepSeasScale(model):
        for s in model.Season:
            if s in ["winter", "spring", "summer", "fall"]:
                model.seasScale[s] = (8760 - lengthPeakSeason * NoOfPeakSeason) / (NoOfRegSeason * lengthRegSeason)
            else:
                model.seasScale[s] = 1
    model.build_seasScale = BuildAction(rule=prepSeasScale)

    def prepOperationalDiscountrate_rule(model):
        #Build operational discount rate
        model.operationalDiscountrate = sum((1+model.discountrate)**(-j) for j in list(range(0,value(LeapYearsInvestment))))
    model.build_operationalDiscountrate = BuildAction(rule=prepOperationalDiscountrate_rule)

    def prepRegHydro_rule(model):
        #Build hydrolimits for all periods
        for n in model.Node:
            for s in model.Season:
                for i in model.Period:
                    for sce in model.Scenario:
                        model.maxRegHydroGen[n,i,s,sce]=sum(model.maxRegHydroGenRaw[n,i,s,h,sce] for h in model.Operationalhour if (s,h) in model.HoursOfSeason)

    model.build_maxRegHydroGen = BuildAction(rule=prepRegHydro_rule)

    def prepGenCapAvail_rule(model):
        #Build generator availability for all periods
        for (n,g) in model.GeneratorsOfNode:
            for h in model.Operationalhour:
                for s in model.Scenario:
                    for i in model.Period:
                        if value(model.genCapAvailTypeRaw[g]) == 0:
                            if value(model.genCapAvailStochRaw[n,g,h,s,i]) >= 0.001:
                                model.genCapAvail[n,g,h,s,i] = model.genCapAvailStochRaw[n,g,h,s,i]
                            else:
                                model.genCapAvail[n,g,h,s,i] = 0
                        else:
                            model.genCapAvail[n,g,h,s,i]=model.genCapAvailTypeRaw[g]

    model.build_genCapAvail = BuildAction(rule=prepGenCapAvail_rule)

    def prepSload_rule(model):
        #Build load profiles for all periods
        counter = 0
        f = open(result_file_path + '/AdjustedNegativeLoad.txt', 'w')
        for n in model.Node:
            for i in model.Period:
                noderawdemand = 0
                for (s,h) in model.HoursOfSeason:
                    if value(h) < value(model.FirstHoursOfRegSeason[-1] + model.lengthRegSeason):
                        for sce in model.Scenario:
                            noderawdemand += value(model.sceProbab[sce]*model.seasScale[s]*model.sloadRaw[n,h,sce,i])
                if noderawdemand > 0:
                    hourlyscale = model.sloadAnnualDemand[n,i].value / noderawdemand
                else:
                    hourlyscale = 0
                for h in model.Operationalhour:
                    for sce in model.Scenario:
                        for gp in model.GasScenario:
                            model.sload[n, h, i, sce, gp] = model.sloadRaw[n,h,sce,i]*hourlyscale
                            if flags.heat:
                                model.sload[n,h,i,sce,gp] = model.sload[n,h,i,sce,gp] - model.ElectricHeatShare[n]*model.sloadRawTR[n,h,sce,i]
                            if flags.industry:
                                if n in model.SteelProducers:
                                    model.sload[n,h,i,sce,gp] -= value(sum(model.steel_initialCapacity[n,p] * model.steel_electricityConsumption[p,i] for p in model.SteelPlants))
                            if flags.industry:
                                if n in model.CementProducers:
                                    model.sload[n,h,i,sce,gp] -= value(sum(model.cement_initialCapacity[n,p] * model.cement_electricityConsumption[p,i] for p in model.CementPlants))
                            if flags.industry:
                                if n in model.AmmoniaProducers:
                                    model.sload[n,h,i,sce,gp] -= value(sum(model.ammonia_initialCapacity[n,p] * model.ammonia_electricityConsumption[p] for p in model.AmmoniaPlants))
                            if value(model.sload[n,h,i,sce,gp]) < 0:
                                f.write('Adjusted electricity load: ' + str(value(model.sload[n,h,i,sce,gp])) + ', 10 MW for hour ' + str(h) + ' in period ' + str(i) + ' scenario ' + str(sce) + ' and gas scenario' + str(gp) + ' in ' + str(n) + "\n")
                                model.sload[n,h,i,sce,gp] = 10
                                counter += 1
        f.write('Hours with too small raw electricity load: ' + str(counter))
        f.close()

    model.build_sload = BuildAction(rule=prepSload_rule)


def define_base_operational_expressions(
        model,
        EMISSION_CAP: bool,
        flags: Flags
        ):
    """Define operational expressions that may depend on BuildActions from modules."""
     
    def prepOperationalCostGen_rule(model):
        #Build generator short term marginal costs
        for g in model.Generator:
            for i in model.Period:
                if not EMISSION_CAP:
                    costperenergyunit=(Constants.GJperMWh/model.genEfficiency[g,i])*(model.genCO2TypeFactor[g]*model.CO2price[i])+ \
                                      model.genVariableOMCost[g]
                    if g not in model.NaturalGasGenerators and g not in model.HydrogenGenerators:
                        costperenergyunit += (Constants.GJperMWh/model.genEfficiency[g,i])*(model.genFuelCost[g,i])
                else:
                    costperenergyunit = model.genVariableOMCost[g]
                    if g not in model.NaturalGasGenerators and g not in model.HydrogenGenerators:
                        costperenergyunit += (Constants.GJperMWh/model.genEfficiency[g,i])*(model.genFuelCost[g,i])
                model.genMargCost[g,i] = costperenergyunit

    model.build_OperationalCostGen = BuildAction(rule=prepOperationalCostGen_rule)
    
    def shed_component_rule(model,i,w, gp):
        return sum(model.operationalDiscountrate*model.seasScale[s]*model.nodeLostLoadCost[n,i]*model.loadShed[n,h,i,w,gp] for n in model.Node for (s,h) in model.HoursOfSeason)
    model.shedcomponent = Expression(model.Period, model.Scenario, model.GasScenario, rule=shed_component_rule)

    
    # For heat module: use CHP generators and electric storage, include converters
    def electric_flow_rule(model, n, h, i, w, gp):
        
        flow = sum((model.storageDischargeEff[b]*model.storDischarge[n,b,h,i,w,gp]-model.storCharge[n,b,h,i,w,gp]) for b in model.Storage if (n,b) in model.StoragesOfNode) \
                + sum((model.lineEfficiency[link,n]*model.transmissionOperational[link,n,h,i,w,gp] - model.transmissionOperational[n,link,h,i,w,gp]) for link in model.NodesLinked[n]) \
                - model.sload[n,h,i,w,gp] + model.loadShed[n,h,i,w,gp]

        if flags.heat:
            flow = add_heat_electric_demand(model, flow, n, h, i, w, gp)
        else:
            flow += sum(model.genOperational[n,g,h,i,w,gp] for g in model.Generator if (n,g) in model.GeneratorsOfNode) 

        if flags.natural_gas:
            flow = add_natural_gas_electric_demand(model, flow, n, h, i, w, gp)
        
        if flags.hydrogen:
            flow = add_hydrogen_electric_demand(model, flow, n, h, i, w, gp)
            flow = add_hydrogen_transport_electric_demand(model, flow, n, h, i, w, gp)

        if flags.industry:
            flow = add_industry_electric_demand(model, flow, n, h, i, w, gp)
        
        return flow
    
    model.electricFlow = Expression(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=electric_flow_rule)


    def operational_cost_scenario_rule(model, i, w, gp):
        returnSum = sum(model.operationalDiscountrate*model.seasScale[s]*model.genMargCost[g,i]*model.genOperational[n,g,h,i,w,gp] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason) + \
                     model.shedcomponent[i,w,gp] + model.ng_import_cost[i,w,gp] 
        if flags.industry:
            returnSum += model.steel_opex[i,w,gp] + model.cement_opex[i,w,gp] + model.ammonia_opex[i,w,gp] + model.oil_opex[i,w,gp] + model.reformerOperationalCost[i,w,gp] 
        if flags.hydrogen:
            returnSum += model.transport_load_shed_cost[i,w,gp] + model.H2TerminalImportCost[i,w,gp]
        if flags.heat:
            returnSum += model.shedcomponentTR[i,w,gp]
        return returnSum
    model.operational_cost_scenario = Expression(model.Period, model.Scenario, model.GasScenario, rule=operational_cost_scenario_rule)

    def operational_cost_rule(model, i):
        return sum(model.sceProbab[w]*model.GasSceProbab[gp]*model.operational_cost_scenario[i,w,gp] for w in model.Scenario for gp in model.GasScenario)
    model.operationalcost = Expression(model.Period, rule=operational_cost_rule)

    if flags.cvar:
        def prep_cvar(model, i):
            return model.value_at_risk[i] + 1 / (1 - model.cvar_percentile) * sum(model.sceProbab[w] * model.GasSceProbab[gp] * model.aux_vars_cvar[i,w,gp] for w in model.Scenario for gp in model.GasScenario)
        model.cvar = Expression(model.Period, rule=prep_cvar)

    def generators_emissions_rule(model, i, w, gp):
        return sum(model.seasScale[s]*model.genCO2TypeFactor[g]*(Constants.GJperMWh/model.genEfficiency[g,i])*model.genOperational[n,g,h,i,w,gp] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason)
    model.generatorEmissions = Expression(model.Period, model.Scenario, model.GasScenario, rule=generators_emissions_rule)
