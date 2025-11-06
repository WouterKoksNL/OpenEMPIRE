from pyomo.environ import BuildAction, Expression

def define_heat_shared_expressions(model):
    def prepSharedHeatOperationalParameters_rule(model):
        """Copy heat-specific operational parameters to base model parameters."""
        # Generator operational parameters
        # Storage operational parameters
        for b in model.StorageTR:
            if b in model.DependentStorageTR:
                model.storagePowToEnergy[b] = model.storagePowToEnergyTR[b]

    model.build_SharedHeatOperationalParameters = BuildAction(rule=prepSharedHeatOperationalParameters_rule)

    def shed_componentTR_rule(model,i,w, gp):
        return sum(model.operationalDiscountrate*model.seasScale[s]*(model.nodeLostLoadCostTR[n,i]*model.loadShedTR[n,h,i,w,gp]) for n in model.ThermalDemandNode for w in model.Scenario for gp in model.GasScenario for (s,h) in model.HoursOfSeason)
    model.shedcomponentTR=Expression(model.Period, model.Scenario, model.GasScenario, rule=shed_componentTR_rule)
