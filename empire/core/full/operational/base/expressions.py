from pyomo.environ import Expression, BuildAction, value, AbstractModel, ConcreteModel
import pandas as pd 

from empire.core.constants import Constants
from empire.core.config import EmpireConfiguration
from empire.core.empire_types import Flags

from ..hydrogen.constraints import add_hydrogen_electric_demand, add_hydrogen_transport_electric_demand
from ..industry.constraints import add_industry_electric_demand
from ..heat.constraints import add_heat_electric_demand
from ..natural_gas.constraints import add_natural_gas_electric_demand

def define_base_operational_build_actions(
        model,
        empire_config: EmpireConfiguration,
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
                model.seasScale[s] = (8760 - empire_config.length_peak_season * empire_config.n_peak_seasons) / (empire_config.n_reg_season * empire_config.length_regular_season)
            else:
                model.seasScale[s] = 1
    model.build_seasScale = BuildAction(rule=prepSeasScale)

    def prepOperationalDiscountrate_rule(model):
        #Build operational discount rate
        model.operationalDiscountrate = sum((1+model.discount_rate)**(-j) for j in list(range(0,value(model.leap_years_investment))))
    model.build_operationalDiscountrate = BuildAction(rule=prepOperationalDiscountrate_rule)



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
                - model.sload[n,h,i,w] + model.loadShed[n,h,i,w,gp]

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
                     model.shedcomponent[i,w,gp] 
        if flags.natural_gas:
            returnSum += model.ng_import_cost[i,w,gp]
        if flags.industry:
            returnSum += model.steel_opex[i,w,gp] + model.cement_opex[i,w,gp] + model.ammonia_opex[i,w,gp] + model.oil_opex[i,w,gp] + model.reformerOperationalCost[i,w,gp] 
        if flags.hydrogen:
            returnSum += model.transport_load_shed_cost[i,w,gp] + model.H2TerminalImportCost[i,w,gp]
        if flags.heat:
            returnSum += model.shedcomponentTR[i,w,gp]
        return returnSum
    model.operational_cost_scenario = Expression(model.Period, model.Scenario, model.GasScenario, rule=operational_cost_scenario_rule)

    if flags.cvar:
        def prep_cvar(model, i):
            return model.value_at_risk[i] + 1 / (1 - model.cvar_percentile) * sum(model.sceProbab[w] * model.GasSceProbab[gp] * model.aux_vars_cvar[i,w,gp] for w in model.Scenario for gp in model.GasScenario)
        model.cvar = Expression(model.Period, rule=prep_cvar)

    def generators_emissions_rule(model, i, w, gp):
        return sum(model.seasScale[s]*model.genCO2TypeFactor[g]*(Constants.GJperMWh/model.genEfficiency[g,i])*model.genOperational[n,g,h,i,w,gp] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason)
    model.generatorEmissions = Expression(model.Period, model.Scenario, model.GasScenario, rule=generators_emissions_rule)



def derive_instance_base_stochastic_parameters(instance: ConcreteModel, node_unscaled_yearly_demand_ser=None) -> None:
    """Set values for stochastic parameters based on raw inputs.
    E.g. compute sload from sloadRaw."""
    def _set_maxRegHydroGen(instance):
        """Assign values to maxRegHydroGen from maxRegHydroGenRaw."""
        for n in instance.Node:
            for s in instance.Season:
                for i in instance.Period:
                    for w in instance.Scenario:
                        total = sum(
                            instance.maxRegHydroGenRaw[i, w, n, s, h]
                            for h in instance.Operationalhour
                            if (s, h) in instance.HoursOfSeason
                        )
                        instance.maxRegHydroGen[i, w, n, s] = total
    _set_maxRegHydroGen(instance)

    def _set_sload(instance, node_unscaled_yearly_demand_ser=None):
        # Precompute cutoff
        cutoff = list(instance.FirstHoursOfRegSeason)[-1] + instance.length_reg_season
        for n in instance.Node:
            for i in instance.Period:
                # Compute probability-weighted raw demand
                if node_unscaled_yearly_demand_ser is None:
                    node_unscaled_yearly_demand = value(sum(
                        instance.sceProbab[w] * instance.seasScale[s] * instance.sloadRaw[i, w, n, h]
                        for (s, h) in instance.HoursOfSeason
                        # if h < cutoff  # adjust if you want peak hours included
                        for w in instance.Scenario
                    ))
                elif isinstance(node_unscaled_yearly_demand_ser, pd.Series):
                    node_unscaled_yearly_demand = node_unscaled_yearly_demand_ser.loc[n]

                # Scaling factor, safe for zero demand

                hourlyscale = value(instance.sloadAnnualDemand[n, i]) / node_unscaled_yearly_demand if node_unscaled_yearly_demand != 0 else 0

                for w in instance.Scenario:
                    for h in instance.Operationalhour:
                        instance.sload[n,h,i,w] = instance.sloadRaw[i, w, n, h] * hourlyscale

    
    _set_sload(instance, node_unscaled_yearly_demand_ser)

    def _set_genCapAvail(instance):
        """Assign generator availability based on type and stochastic raw availability."""
        for (n, g) in instance.GeneratorsOfNode:
            for h in instance.Operationalhour:
                for w in instance.Scenario:
                    for i in instance.Period:
                        if value(instance.genCapAvailTypeRaw[g]) < 1e-8:
                            raise ValueError(f"Generator {g} has zero available capacity. For now datasets the genCapAvailTypeRaw of stochastic generators should be set to 1.")
                        instance.genCapAvail[n, g, h, w, i] = (
                            instance.genCapAvailTypeRaw[g] * instance.genCapAvailStochRaw[i, w, n, g, h]
                        )
    _set_genCapAvail(instance)


    return 
