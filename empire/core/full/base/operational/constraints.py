from pyomo.environ import Constraint, value

from constants import Constants
from empire_types import Flags



def define_base_operational_constraints(model, EMISSION_CAP, flags: Flags):
    # Define the electric flow expression with all module contributions

    # Simple constraint: electric flow must balance to zero
    def flow_balance_constraint_rule(model, n, h, i, w, gp):
        return model.electricFlow[n, h, i, w, gp] == 0
    model.FlowBalance = Constraint(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=flow_balance_constraint_rule)

    def max_bio_availability_rule(model, i, w, gp):
        bio_use = 0
        for n in model.NaturalGasNode:
            for g in model.Generator:
                if (n,g) in model.GeneratorsOfNode:
                    if 'bio' in g.lower():
                        if 'cofiring' in g.lower():
                            bio_use += sum(model.seasScale[s] * 0.1 * model.genOperational[n,g,h,i,w,gp] / model.genEfficiency[g,i] * Constants.GJperMWh for (s,h) in model.HoursOfSeason)
                        else:
                            bio_use += sum(model.seasScale[s] * model.genOperational[n,g,h,i,w,gp] / model.genEfficiency[g,i] * Constants.GJperMWh for (s,h) in model.HoursOfSeason)
        if flags.industry:
            for n in model.SteelProducers:
                bio_use += sum(model.seasScale[s] * model.steel_bioConsumption[p,i] * model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants for (s,h) in model.HoursOfSeason)
        return bio_use <= model.availableBioEnergy[i]
    # model.max_bio_availability = Constraint(model.Period, model.Scenario, model.GasScenario, rule=max_bio_availability_rule)

    def genFuelUse_limit_rule(model, n, i, w, gp):
        biomethane_use = 0
        for g in model.Generator:
            if (n,g) in model.GeneratorsOfNode:
                if 'biomethane' in g.lower():
                    biomethane_use += sum(model.seasScale[s] * model.genOperational[n,g,h,i,w,gp] / model.genEfficiency[g,i] * Constants.GJperMWh for (s,h) in model.HoursOfSeason)
        return biomethane_use <= model.genMaxBiomethaneAvailability[n,i] * 1e3
    model.genFuelUse_limit_rule = Constraint(model.Node, model.Period, model.Scenario, model.GasScenario, rule=genFuelUse_limit_rule)
    
    #################################################################

    def shed_limit_rule(model,n,h,i,w,gp):
        return model.loadShed[n,h,i,w,gp] <= model.sload[n,h,i,w,gp]
    # model.shed_limit = Constraint(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=shed_limit_rule)

    #################################################################

    def genMaxProd_rule(model, n, g, h, i, w, gp):
        return model.genOperational[n,g,h,i,w,gp] - model.genCapAvail[n,g,h,w,i]*model.genInstalledCap[n,g,i] <= 0
    model.maxGenProduction = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=genMaxProd_rule)

    #################################################################

    def ramping_rule(model, n, g, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return Constraint.Skip
        else:
            if g in model.RampingGenerators:
                return model.genOperational[n,g,h,i,w,gp]-model.genOperational[n,g,(h-1),i,w,gp] - model.genRampUpCap[g]*model.genInstalledCap[n,g,i] <= 0   #
            else:
                return Constraint.Skip
    model.ramping = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=ramping_rule)

    #################################################################

    def storage_energy_balance_rule(model, n, b, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] + model.storageChargeEff[b]*model.storCharge[n,b,h,i,w,gp]-model.storDischarge[n,b,h,i,w,gp]-model.storOperational[n,b,h,i,w,gp] == 0   #
        else:
            return model.storageBleedEff[b]*model.storOperational[n,b,(h-1),i,w,gp] + model.storageChargeEff[b]*model.storCharge[n,b,h,i,w,gp]-model.storDischarge[n,b,h,i,w,gp]-model.storOperational[n,b,h,i,w,gp] == 0   #
    model.storage_energy_balance = Constraint(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=storage_energy_balance_rule)

    #################################################################

    def storage_seasonal_net_zero_balance_rule(model, n, b, h, i, w, gp):
        if h in model.FirstHoursOfRegSeason:
            return model.storOperational[n,b,h+value(model.lengthRegSeason)-1,i,w,gp] - model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] == 0  #
        elif h in model.FirstHoursOfPeakSeason:
            return model.storOperational[n,b,h+value(model.lengthPeakSeason)-1,i,w,gp] - model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] == 0  #
        else:
            return Constraint.Skip
    model.storage_seasonal_net_zero_balance = Constraint(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=storage_seasonal_net_zero_balance_rule)

    #################################################################

    def storage_operational_cap_rule(model, n, b, h, i, w, gp):
        return model.storOperational[n,b,h,i,w,gp] - model.storENInstalledCap[n,b,i] <= 0   #
    model.storage_operational_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=storage_operational_cap_rule)

    #################################################################

    def storage_power_discharg_cap_rule(model, n, b, h, i, w, gp):
        return model.storDischarge[n,b,h,i,w,gp] - model.storageDiscToCharRatio[b]*model.storPWInstalledCap[n,b,i] <= 0   #
    model.storage_power_discharg_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=storage_power_discharg_cap_rule)

    #################################################################

    def storage_power_charg_cap_rule(model, n, b, h, i, w, gp):
        return model.storCharge[n,b,h,i,w,gp] - model.storPWInstalledCap[n,b,i] <= 0   #
    model.storage_power_charg_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=storage_power_charg_cap_rule)

    #################################################################

    def hydro_gen_limit_rule(model, n, g, s, i, w, gp):
        if g in model.RegHydroGenerator:
            return sum(model.genOperational[n,g,h,i,w,gp] for h in model.Operationalhour if (s,h) in model.HoursOfSeason) - model.maxRegHydroGen[n,i,s,w] <= 0
        else:
            return Constraint.Skip  #
    model.hydro_gen_limit = Constraint(model.GeneratorsOfNode, model.Season, model.Period, model.Scenario, model.GasScenario, rule=hydro_gen_limit_rule)

    #################################################################

    def hydro_node_limit_rule(model, n, i):
        return sum(model.genOperational[n,g,h,i,w,gp]*model.seasScale[s]*model.sceProbab[w]*model.GasSceProbab[gp] for g in model.HydroGenerator if (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason for w in model.Scenario for gp in model.GasScenario) /1e3 - model.maxHydroNode[n] / 1e3 <= 0   #
    model.hydro_node_limit = Constraint(model.Node, model.Period, rule=hydro_node_limit_rule)

    #################################################################

    def transmission_cap_rule(model, n1, n2, h, i, w, gp):
        if (n1,n2) in model.BidirectionalArc:
            return model.transmissionOperational[(n1,n2),h,i,w,gp] - model.transmissionInstalledCap[(n1,n2),i] <= 0
        elif (n2,n1) in model.BidirectionalArc:
            return model.transmissionOperational[(n1,n2),h,i,w,gp] - model.transmissionInstalledCap[(n2,n1),i] <= 0
    model.transmission_cap = Constraint(model.DirectionalLink, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=transmission_cap_rule)

    #################################################################

    if EMISSION_CAP:
        def emission_cap_rule(model, i, w, gp):
            # return (model.generatorEmissions[i,w,gp] + model.industryEmissions[i,w,gp]  + model.reformerEmissions[i,w,gp]) / co2_scale_factor <= (model.CO2cap[i] * 1e6 + model.CO2CapExceeded[i,w,gp]) / co2_scale_factor
            #return (model.generatorEmissions[i,w,gp] + model.industryEmissions[i,w,gp]  + model.reformerEmissions[i,w,gp]) / co2_scale_factor <= model.CO2cap[i] * 1e6 / co2_scale_factor
            emissions = model.generatorEmissions[i, w, gp]
            if flags.hydrogen:
                emissions += model.reformerEmissions[i, w, gp]  
            if flags.industry:
                emissions += model.industryEmissions[i, w, gp] 
            return emissions / Constants.co2_scale_factor <= model.CO2cap[i] * 1e6 / Constants.co2_scale_factor
        model.emission_cap = Constraint(model.Period, model.Scenario, model.GasScenario, rule=emission_cap_rule)


    
    # GD: Ensuring that power sent from offshore hub is no greater than its capacity
    def offshore_hub_capacity_in_rule(model, n,h,i,w,gp):
        return sum(model.transmissionOperational[n2,n,h,i,w,gp] for n2 in model.NodesLinked[n]) - model.offshoreConvInstalledCap[n,i] <= 0
    model.offshore_hub_capacity_in = Constraint(model.OffshoreEnergyHubs, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=offshore_hub_capacity_in_rule)

    def offshore_hub_capacity_out_rule(model, n,h,i,w,gp):
        return sum(model.transmissionOperational[n,n2,h,i,w,gp] for n2 in model.NodesLinked[n]) - model.offshoreConvInstalledCap[n,i] <= 0
    model.offshore_hub_capacity_out = Constraint(model.OffshoreEnergyHubs, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=offshore_hub_capacity_out_rule)


    if flags.cvar:
        def prep_auxiliary_vars_cvar(model, i, w, gp):
            return model.aux_vars_cvar[i, w, gp] >= model.operational_cost_scenario[i, w, gp] - model.value_at_risk[i]

        model.aux_cvar_constraint = Constraint(model.Period, model.Scenario, model.GasScenario,
                                               rule=prep_auxiliary_vars_cvar)