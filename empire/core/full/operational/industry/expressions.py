from pyomo.environ import BuildAction, Expression

from empire.core.constants import Constants

def define_industry_operational_expressions(model, EMISSION_CAP, steel_CCS_capture_rate=None):
    if steel_CCS_capture_rate is not None and steel_CCS_capture_rate <= 1:
        def prepsteelCCSCaptureRate(model):
            for p in model.SteelPlants:
                if 'ccs' in p.lower():
                    model.steel_CO2Emissions[p] = (1-steel_CCS_capture_rate) * model.steel_CO2Emissions['BF-BOF']
                    model.steel_CO2Captured[p] = (steel_CCS_capture_rate) * model.steel_CO2Emissions['BF-BOF']
        model.build_steel_ccs_capture_rate = BuildAction(rule=prepsteelCCSCaptureRate)
    
    def steel_opex_rule(model, i, w, gp):
        steel_opex = 0
        for p in model.SteelPlants:
            steel_opex += sum(model.seasScale[s] *  (model.genFuelCost['Coal',i] * model.steel_coalConsumption[p,i] +
                                                    model.genFuelCost['Oilexisting',i] * model.steel_oilConsumption[p,i] +
                                                    model.genFuelCost['Bioexisting',i] * model.steel_bioConsumption[p,i] +
                                                    model.steel_varOpex[p,i]) * model.steelProduced[n,p,h,i,w,gp] for n in model.SteelProducers for (s,h) in model.HoursOfSeason)
            if not EMISSION_CAP:
                steel_opex += sum(model.seasScale[s] * model.CO2price[i] * model.steel_CO2Emissions[p] * model.steelProduced[n,p,h,i,w,gp] for n in model.SteelProducers for (s,h) in model.HoursOfSeason)
        steel_opex += sum(model.seasScale[s] * model.industryShedCost * model.steelLoadShed[n,h,i,w,gp] for (s,h) in model.HoursOfSeason for n in model.SteelProducers)
        return model.operationalDiscountrate * steel_opex
    model.steel_opex = Expression(model.Period, model.Scenario, model.GasScenario, rule=steel_opex_rule)

    def cement_opex_rule(model, i, w, gp):
        cement_opex = 0
        for p in model.CementPlants:
            if "ng" in p.lower():
                if EMISSION_CAP is False:
                    cement_opex += sum(model.seasScale[s] * model.CO2price[i] * model.genCO2TypeFactor['Gasexisting'] * Constants.GJperMWh * Constants.ng_MWhPerTon / 1000 * model.cement_fuelConsumption[p,i] * model.cementProduced[n,p,h,i,w,gp] for n in model.CementProducers for (s,h) in model.HoursOfSeason)
        cement_opex += sum(model.seasScale[s] * model.industryShedCost * model.cementLoadShed[n,h,i,w,gp] for (s,h) in model.HoursOfSeason for n in model.CementProducers)
        return model.operationalDiscountrate * cement_opex
    model.cement_opex = Expression(model.Period, model.Scenario, model.GasScenario, rule=cement_opex_rule)

    def ammonia_opex_rule(model, i, w, gp):
        ammonia_opex = 0
        for p in model.AmmoniaPlants:
            if "ng" in p.lower():
                if EMISSION_CAP is False:
                    ammonia_opex += sum(model.seasScale[s] * model.CO2price[i] * model.genCO2TypeFactor['Gasexisting'] * Constants.GJperMWh * Constants.ng_MWhPerTon / 1000 * model.ammonia_fuelConsumption[p] * model.ammoniaProduced[n,p,h,i,w,gp] for n in model.AmmoniaProducers for (s,h) in model.HoursOfSeason)
        ammonia_opex += sum(model.seasScale[s] * model.industryShedCost * model.ammoniaLoadShed[n,h,i,w,gp] for (s,h) in model.HoursOfSeason for n in model.AmmoniaProducers)
        return model.operationalDiscountrate * ammonia_opex
    model.ammonia_opex = Expression(model.Period, model.Scenario, model.GasScenario, rule=ammonia_opex_rule)

    def oil_opex_rule(model, i, w, gp):
        oil_shed_cost = 1000000
        oil_opex = sum(model.seasScale[s] * oil_shed_cost * model.oilLoadShed[n,h,i,w,gp] for (s,h) in model.HoursOfSeason for n in model.OilProducers)
        return oil_opex
    model.oil_opex = Expression(model.Period, model.Scenario, model.GasScenario, rule=oil_opex_rule)


    # def transport_emissions_rule(model, i, w, gp):
    #     oil_emission_factor = model.genCO2TypeFactor['Oilexisting'] * GJperMWh
    #     return sum(model.seasScale[s] * oil_emission_factor * model.transport_energyConsumption[v,i] * model.transportDemandMet[n,v,h,i,w,gp] for (s,h) in model.HoursOfSeason for n in model.OnshoreNode for v in model.VehicleTypes if ('gasoline' in v.lower() or 'kerosene' in v.lower() or 'diesel' in v.lower()))
    # model.transportEmissions = Expression(model.Period, model.Scenario, model.GasScenario, rule=transport_emissions_rule)

    # def transport_opex_rule(model, i):
    #     transport_curtail_cost = 1000
    #     transport_opex = 0
    #     transport_opex += sum(model.seasScale[s] * model.sceProbab[w] * model.genFuelCost['Oilexisting',i] * model.transport_energyConsumption[v,i] * GJperMWh * model.transportDemandMet[n,v,h,i,w,gp] for n in model.OnshoreNode for (s,h) in model.HoursOfSeason for w in model.Scenario for v in model.VehicleTypes if ('kerosene' in v.lower() or 'diesel' in v.lower() or 'gasoline' in v.lower()))
    #     transport_opex += sum(model.seasScale[s] * model.sceProbab[w] * model.aviation_fuel_cost[v,i] * model.transport_energyConsumption[v,i] * GJperMWh * model.transportDemandMet[n,v,h,i,w,gp] for n in model.OnshoreNode for (s,h) in model.HoursOfSeason for w in model.Scenario for v in model.VehicleTypes if 'plane_bio' in v.lower())
    #     if EMISSION_CAP is False:
    #         transport_opex += sum(model.seasScale[s] * model.sceProbab[w] * model.genCO2TypeFactor['Oilexisting'] * GJperMWh * model.transportDemandMet[n,v,h,i,w,gp] for n in model.OnshoreNode for (s,h) in model.HoursOfSeason for w in model.Scenario for v in model.VehicleTypes if ('kerosene' in v.lower() or 'diesel' in v.lower() or 'gasoline' in v.lower()))
    #     transport_opex += sum(model.seasScale[s] * model.sceProbab[w] * transport_curtail_cost * model.transportDemandSlack[n,v,h,i,w,gp] for n in model.OnshoreNode for (s,h) in model.HoursOfSeason for v in model.VehicleTypes for w in model.Scenario)
    #     return model.operationalDiscountrate * transport_opex
    # model.transport_opex = Expression(model.Period, rule=transport_opex_rule)

