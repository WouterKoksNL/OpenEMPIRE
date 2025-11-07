from pyomo.environ import BuildAction, value


def define_heat_operational_expressions(model, result_file_path):
    """Define heat module operational build actions."""
    
    def prepSloadTR_rule(model):
        #Build heat load profiles for all periods
        counter = 0
        f = open(result_file_path / 'AdjustedNegativeLoad.txt', 'w')
        f.write('')
        for n in model.Node:
            for i in model.Period:
                noderawdemandTR = 0
                for (s,h) in model.HoursOfSeason:
                    if value(h) < value(model.FirstHoursOfRegSeason[-1] + model.length_reg_season):
                        for sce in model.Scenario:
                            noderawdemandTR += value(model.sceProbab[sce]*model.seasScale[s]*model.sloadRawTR[n,h,sce,i])
                if noderawdemandTR > 0:
                    hourlyscaleTR = model.sloadAnnualDemandTR[n,i].value / noderawdemandTR
                else:
                    hourlyscaleTR = 0
                for h in model.Operationalhour:
                    for sce in model.Scenario:
                        for gp in model.GasScenario:
                            model.sloadTR[n,h,i,sce] = model.sloadRawTR[n,h,sce,i]*hourlyscaleTR
                            if value(model.sloadTR[n,h,i,sce]) < 0:
                                f.write('Adjusted heat load: ' + str(value(model.sloadTR[n,h,i,sce])) + ', 0 MW for hour ' + str(h) + ' and scenario ' + str(sce) + ' in ' + str(n) + "\n")
                                model.sloadTR[n,h,i,sce] = 0
                                counter += 1
        f.write('Hours with too small raw heat load: ' + str(counter))
        f.close()

    model.build_sloadTR = BuildAction(rule=prepSloadTR_rule)

    def prepCHP_rule(model):
        #Build CHP coefficients for CHP generators
        for i in model.Period:
            for g in model.GeneratorEL:
                if g in model.GeneratorTR:
                    model.genCHPEfficiency[g,i] = model.genCHPEfficiencyRaw[g,i]
                else:
                    model.genCHPEfficiency[g,i] = 1.0
    model.build_CHPeff = BuildAction(rule=prepCHP_rule)

    def prepHeatOperationalParameters_rule(model):
        """Copy heat-specific operational parameters to base model parameters."""
        # Generator operational parameters
        for g in model.GeneratorTR:
            model.genVariableOMCost[g] = model.genVariableOMCostHeat[g]
            if g in model.RampingGenerators:
                model.genRampUpCap[g] = model.genRampUpCapHeat[g]
            model.genCapAvailTypeRaw[g] = model.genCapAvailTypeRawHeat[g]
            model.genCO2TypeFactor[g] = model.genCO2TypeFactorHeat[g]
            for i in model.Period:
                model.genFuelCost[g,i] = model.genFuelCostHeat[g,i]
                model.genEfficiency[g,i] = model.genEfficiencyHeat[g,i]
        
        for g in model.GeneratorTR_Industrial:
            model.genVariableOMCost[g] = model.genVariableOMCostHeat[g]
            if g in model.RampingGenerators:
                model.genRampUpCap[g] = model.genRampUpCapHeat[g]
            model.genCapAvailTypeRaw[g] = model.genCapAvailTypeRawHeat[g]
            model.genCO2TypeFactor[g] = model.genCO2TypeFactorHeat[g]
            for i in model.Period:
                model.genFuelCost[g,i] = model.genFuelCostHeat[g,i]
                model.genEfficiency[g,i] = model.genEfficiencyHeat[g,i]
        
        # Storage operational parameters
        for b in model.StorageTR:
            model.storOperationalInit[b] = model.storOperationalInitHeat[b]
            model.storageChargeEff[b] = model.storageChargeEffHeat[b]
            model.storageDischargeEff[b] = model.storageDischargeEffHeat[b]
            model.storageBleedEff[b] = model.storageBleedEffHeat[b]
            model.storageLifetime[b] = model.storageLifetimeHeat[b]
    
    model.build_HeatOperationalParameters = BuildAction(rule=prepHeatOperationalParameters_rule)
