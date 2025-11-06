from pyomo.environ import BuildAction, value


def define_heat_investment_expressions(model):
    """Define heat module investment build actions."""
    
    def prepInvCostConverter_rule(model):
        #Build investment cost for Converter-converters
        for r in model.Converter:
            for i in model.Period:
                costperyear=(model.WACC/(1-((1+model.WACC)**(1-model.ConverterLifetime[r]))))*model.ConverterCapitalCost[r,i]+model.ConverterFixedOMCost[r,i]
                costperperiod=costperyear*1000*(1-(1+model.discount_rate)**-(min(value((len(model.period_active)-i+1)*model.leap_years_investment), value(model.ConverterLifetime[r]))))/(1-(1/(1+model.discount_rate)))
                model.ConverterInvCost[r,i]=costperperiod

    model.build_InvCostConverter = BuildAction(rule=prepInvCostConverter_rule)

    def ConverterMaxInstalledCap_rule(model):
        #Build resource limit for electricity to heat converters
        for (n,r) in model.ConverterOfNode:
            for i in model.Period:
                model.ConverterMaxInstalledCap[n,r,i]=model.ConverterMaxInstalledCapRaw[n,r]

    model.build_ConverterMaxInstalledCap = BuildAction(rule=ConverterMaxInstalledCap_rule)

    def prepHeatInvestmentParameters_rule(model):
        """Copy heat-specific investment parameters to base model parameters."""
        # Generator investment parameters
        for g in model.GeneratorTR:
            model.genLifetime[g] = model.genLifetimeHeat[g]
            for n in model.Node:
                if (n,g) in model.GeneratorsOfNode:
                    model.genRefInitCap[n,g] = model.genRefInitCapHeat[n,g]
            for i in model.Period:
                model.genCapitalCost[g,i] = model.genCapitalCostHeat[g,i]
                model.genFixedOMCost[g,i] = model.genFixedOMCostHeat[g,i]
                model.genScaleInitCap[g,i] = model.genScaleInitCapHeat[g,i]
        
        for g in model.GeneratorTR_Industrial:
            model.genLifetime[g] = model.genLifetimeHeat[g]
            for n in model.Node:
                if (n,g) in model.GeneratorsOfNode:
                    model.genRefInitCap[n,g] = model.genRefInitCapHeat[n,g]
            for i in model.Period:
                model.genCapitalCost[g,i] = model.genCapitalCostHeat[g,i]
                model.genFixedOMCost[g,i] = model.genFixedOMCostHeat[g,i]
                model.genScaleInitCap[g,i] = model.genScaleInitCapHeat[g,i]
        
        for t in model.TechnologyHeat:
            for n in model.Node:
                model.genMaxInstalledCapRaw[n,t] = model.genMaxInstalledCapRawHeat[n,t]
                for i in model.Period:
                    model.genMaxBuiltCap[n,t,i] = model.genMaxBuiltCapHeat[n,t,i]
        
        # Storage investment parameters
        for b in model.StorageTR:
            for i in model.Period:
                model.storPWCapitalCost[b,i] = model.storPWCapitalCostHeat[b,i]
                model.storENCapitalCost[b,i] = model.storENCapitalCostHeat[b,i]
                model.storPWFixedOMCost[b,i] = model.storPWFixedOMCostHeat[b,i]
                model.storENFixedOMCost[b,i] = model.storENFixedOMCostHeat[b,i]
            for n in model.Node:
                if (n,b) in model.StoragesOfNode:
                    model.storPWMaxInstalledCapRaw[n,b] = model.storPWMaxInstalledCapRawHeat[n,b]
                    model.storENMaxInstalledCapRaw[n,b] = model.storENMaxInstalledCapRawHeat[n,b]
                    for i in model.Period:
                        model.storPWInitCap[n,b,i] = model.storPWInitCapHeat[n,b,i]
                        model.storPWMaxBuiltCap[n,b,i] = model.storPWMaxBuiltCapHeat[n,b,i]
                        model.storENInitCap[n,b,i] = model.storENInitCapHeat[n,b,i]
                        model.storENMaxBuiltCap[n,b,i] = model.storENMaxBuiltCapHeat[n,b,i]
    
    model.build_HeatInvestmentParameters = BuildAction(rule=prepHeatInvestmentParameters_rule)
