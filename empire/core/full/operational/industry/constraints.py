from pyomo.environ import Constraint, Expression
from empire.core.constants import Constants


def add_industry_electric_demand(model, flow, n, h, i, w, gp):
    """Add industry module's electricity demand to the electric flow.
    
    Args:
        model: Pyomo model
        flow: Current electric flow value
        n, h, i, w, gp: Indices for node, hour, period, scenario, gas scenario
        
    Returns:
        Updated flow with industry electricity demands subtracted
    """
    # Steel production electricity consumption
    if n in model.SteelProducers:
        flow -= sum(model.steel_electricityConsumption[p, i] * 
                   model.steelProduced[n, p, h, i, w, gp] 
                   for p in model.SteelPlants)
    
    # Cement production electricity consumption
    if n in model.CementProducers:
        flow -= sum(model.cement_electricityConsumption[p, i] * 
                   model.cementProduced[n, p, h, i, w, gp] 
                   for p in model.CementPlants)
    
    # Ammonia production electricity consumption
    if n in model.AmmoniaProducers:
        flow -= sum(model.ammonia_electricityConsumption[p] * 
                   model.ammoniaProduced[n, p, h, i, w, gp] 
                   for p in model.AmmoniaPlants)
    
    return flow


def define_industry_operational_constraints(model, FLEX_IND):
    def steelMaxProduction_rule(model, n,p,h,i,w,gp):
        return model.steelProduced[n,p,h,i,w,gp] <= model.steelPlantInstalledCapacity[n,p,i]
    model.steelMaxProduction = Constraint(model.SteelProducers, model.SteelPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=steelMaxProduction_rule)

    #link EAF with H2-DRI and scrap
    def link_eaf_with_raw_materials_rule(model,n,h,i,w,gp):
        return sum(model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants if 'scrap' in p.lower() or 'dri' in p.lower()) == sum(model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants if 'eaf' in p.lower())
    model.link_eaf_with_raw_materials = Constraint(model.SteelProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=link_eaf_with_raw_materials_rule)

    def cementMaxProduction_rule(model, n,p,h,i,w,gp):
        return model.cementProduced[n,p,h,i,w,gp] <= model.cementPlantInstalledCapacity[n,p,i]
    model.cementMaxProduction = Constraint(model.CementProducers, model.CementPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=cementMaxProduction_rule)

    def ammoniaMaxProduction_rule(model, n,p,h,i,w,gp):
        return model.ammoniaProduced[n,p,h,i,w,gp] <= model.ammoniaPlantInstalledCapacity[n,p,i]
    model.ammoniaMaxProduction = Constraint(model.AmmoniaProducers, model.AmmoniaPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=ammoniaMaxProduction_rule)

    if FLEX_IND:
        def meet_steel_demand_rule(model, n, i, w, gp):
            return sum(model.seasScale[s] * (sum(model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants_FinalSteel) + model.steelLoadShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.steel_yearlyProduction[n,i]
        model.meet_steel_demand = Constraint(model.SteelProducers, model.Period, model.Scenario, model.GasScenario, rule=meet_steel_demand_rule)

        def meet_cement_demand_rule(model, n, i, w, gp):
            return sum(model.seasScale[s] * (sum(model.cementProduced[n,p,h,i,w,gp] for p in model.CementPlants) + model.cementLoadShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.cement_yearlyProduction[n]
        model.meet_cement_demand = Constraint(model.CementProducers, model.Period, model.Scenario, model.GasScenario, rule=meet_cement_demand_rule)

        def meet_ammonia_demand_rule(model, n, i, w, gp):
            return sum(model.seasScale[s] * (sum(model.ammoniaProduced[n,p,h,i,w,gp] for p in model.AmmoniaPlants) + model.ammoniaLoadShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.ammonia_yearlyProduction[n,i]
        model.meet_ammonia_demand = Constraint(model.AmmoniaProducers, model.Period, model.Scenario, model.GasScenario, rule=meet_ammonia_demand_rule)

        def meet_oil_demand_rule(model, n, i, w, gp):
            return sum(model.seasScale[s] * (model.oilRefined[n,h,i,w,gp] + model.oilLoadShed[n,h,i,w,gp]) for (s,h) in model.HoursOfSeason) == model.refinery_yearlyProduction[n,i]
        model.meet_oil_demand = Constraint(model.OilProducers, model.Period, model.Scenario, model.GasScenario, rule=meet_oil_demand_rule)
    else:
        def meet_steel_demand_rule(model, n, h, i, w, gp):
            return sum(model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants_FinalSteel) + model.steelLoadShed[n,h,i,w,gp] == model.steel_yearlyProduction[n,i] / 8760
        model.meet_steel_demand = Constraint(model.SteelProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=meet_steel_demand_rule)

        def meet_cement_demand_rule(model, n, h, i, w, gp):
            return sum(model.cementProduced[n,p,h,i,w,gp] for p in model.CementPlants) + model.cementLoadShed[n,h,i,w,gp] == model.cement_yearlyProduction[n] / 8760
        model.meet_cement_demand = Constraint(model.CementProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=meet_cement_demand_rule)

        def meet_ammonia_demand_rule(model, n, h, i, w, gp):
            return sum(model.ammoniaProduced[n,p,h,i,w,gp] for p in model.AmmoniaPlants) + model.ammoniaLoadShed[n,h,i,w,gp] == model.ammonia_yearlyProduction[n,i] / 8760
        model.meet_ammonia_demand = Constraint(model.AmmoniaProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=meet_ammonia_demand_rule)

        def meet_oil_demand_rule(model, n, h, i, w, gp):
            return model.oilRefined[n,h,i,w,gp] + model.oilLoadShed[n,h,i,w,gp] == model.refinery_yearlyProduction[n,i] / 8760
        model.meet_oil_demand = Constraint(model.OilProducers, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=meet_oil_demand_rule)

    def steel_ramping_rule(model,n,p,h,i,w,gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason or 'scrap' in p.lower():
            return Constraint.Skip
        else:
            return model.steelProduced[n,p,h,i,w,gp] - model.steelProduced[n,p,h-1,i,w,gp] <= 0.1 * model.steelPlantInstalledCapacity[n,p,i]
    model.steel_ramping = Constraint(model.SteelProducers, model.SteelPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=steel_ramping_rule)

    def cement_ramping_rule(model,n,p,h,i,w,gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return Constraint.Skip
        else:
            return model.cementProduced[n,p,h,i,w,gp] - model.cementProduced[n,p,h-1,i,w,gp] <= 0.1 * model.cementPlantInstalledCapacity[n,p,i]
    model.cement_ramping = Constraint(model.CementProducers, model.CementPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=cement_ramping_rule)

    def ammonia_ramping_rule(model,n,p,h,i,w,gp):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return Constraint.Skip
        else:
            return model.ammoniaProduced[n,p,h,i,w,gp] - model.ammoniaProduced[n,p,h-1,i,w,gp] <= 0.1 * model.ammoniaPlantInstalledCapacity[n,p,i]
    model.ammonia_ramping = Constraint(model.AmmoniaProducers, model.AmmoniaPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=ammonia_ramping_rule)

    def industry_emissions_rule(model, i, w, gp):
        return sum(model.seasScale[s] * (
                sum(model.steel_CO2Emissions[p] * model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants for n in model.SteelProducers)
                ### emissions from cement production are multiplied by 2.5 to account for process emissions (approx. 60% of total emissions)
                + sum((model.genCO2TypeFactor['Gasexisting'] * Constants.GJperMWh * Constants.ng_MWhPerTon * model.cement_fuelConsumption[p,i]/1000) * 2.5 * (1-model.cement_co2CaptureRate[p]) * model.cementProduced[n,p,h,i,w,gp] for p in model.CementPlants if "ng" in p.lower() for n in model.CementProducers)
                + sum(model.genCO2TypeFactor['Gasexisting'] * Constants.GJperMWh * Constants.ng_MWhPerTon * model.ammonia_fuelConsumption[p]/1000 * model.ammoniaProduced[n,p,h,i,w,gp] for p in model.AmmoniaPlants if "ng" in p.lower() for n in model.AmmoniaProducers)
        ) for (s,h) in model.HoursOfSeason)
    model.industryEmissions = Expression(model.Period, model.Scenario, model.GasScenario, rule=industry_emissions_rule)

    def CO2_captured_industry_rule(model,n,h,i,w,gp):
        ### emissions from cement production are multiplied by 2.5 to account for process emissions (approx. 60% of total emissions)
        captured = 0
        if n in model.CementProducers:
            captured += sum((model.genCO2TypeFactor['Gasexisting'] * Constants.GJperMWh * Constants.ng_MWhPerTon * model.cement_fuelConsumption[
                p,i]/1000) * 2.5 * model.cement_co2CaptureRate[p] * model.cementProduced[n,p,h,i,w,gp] for p in model.CementPlants if "ng" in p.lower())

        if n in model.SteelProducers:
            captured += sum(model.steel_CO2Captured[p] * model.steelProduced[n,p,h,i,w,gp] for p in model.SteelPlants)
        return captured
    model.co2_captured_industry = Expression(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=CO2_captured_industry_rule)
