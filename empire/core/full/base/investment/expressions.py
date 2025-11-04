from pyomo.environ import BuildAction, value, Expression


# def annualized_factor(WACC, discountrate, lifetime, period, periods):
#     time_left = min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.genLifetime[g]))
#     (WACC / (1 - ((1 + WACC) ** (1 - lifetime)))) * (1 - (1 + discountrate) ** - 


def define_base_investment_expressions(model, LeapYearsInvestment):
    
    def multiplier_rule(model,period):
        coeff=1
        if period>1:
            coeff=pow(1.0+model.discountrate,(-LeapYearsInvestment*(int(period)-1)))
        return coeff
    model.discount_multiplier = Expression(model.Period, rule=multiplier_rule)

    def prepInvCost_rule(model):
        #Build investment cost for generators, storages and transmission. Annual cost is calculated for the lifetime of the generator and discounted for a year.
        #Then cost is discounted for the investment period (or the remaining lifetime). CCS generators has additional fixed costs depending on emissions.

        #Generator
        for g in model.Generator:
            for i in model.Period:
                costperyear=(model.WACC / (1 - ((1+model.WACC) ** (1-model.genLifetime[g])))) * model.genCapitalCost[g,i] + model.genFixedOMCost[g,i]
                costperperiod = costperyear * 1000 * (1 - (1+model.discountrate) **-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.genLifetime[g]))))/ (1 - (1 / (1 + model.discountrate)))
                # if ('CCS',g) in model.GeneratorsOfTechnology:
                # 	costperperiod+=model.CCSCostTSFix*model.CCSRemFrac*model.genCO2TypeFactor[g]*(GJperMWh/model.genEfficiency[g,i])
                model.genInvCost[g,i]=costperperiod

        #Storage
        for b in model.Storage:
            for i in model.Period:
                costperyearPW=(model.WACC/(1-((1+model.WACC)**(1-model.storageLifetime[b]))))*model.storPWCapitalCost[b,i]+model.storPWFixedOMCost[b,i]
                costperperiodPW=costperyearPW*1000*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.storageLifetime[b]))))/(1-(1/(1+model.discountrate)))
                model.storPWInvCost[b,i]=costperperiodPW
                costperyearEN=(model.WACC/(1-((1+model.WACC)**(1-model.storageLifetime[b]))))*model.storENCapitalCost[b,i]+model.storENFixedOMCost[b,i]
                costperperiodEN=costperyearEN*1000*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.storageLifetime[b]))))/(1-(1/(1+model.discountrate)))
                model.storENInvCost[b,i]=costperperiodEN

        #Transmission
        for (n1,n2) in model.BidirectionalArc:
            for i in model.Period:
                for t in model.TransmissionType:
                    if (n1,n2,t) in model.TransmissionTypeOfDirectionalLink:
                        costperyear=(model.WACC/(1-((1+model.WACC)**(1-model.transmissionLifetime[n1,n2]))))*model.transmissionLength[n1,n2]*model.transmissionTypeCapitalCost[t,i] + model.transmissionLength[n1,n2]* model.transmissionTypeFixedOMCost[t,i]
                        costperperiod=costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment), value(model.transmissionLifetime[n1,n2]))))/(1-(1/(1+model.discountrate)))
                        model.transmissionInvCost[n1,n2,i]=costperperiod

        #Offshore converter
        for i in model.Period:
            costperyear = (model.WACC/(1-((1+model.WACC)**(1-model.offshoreConvLifetime))))*model.offshoreConvCapitalCost[i] + model.offshoreConvOMCost[i]
            costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment),model.offshoreConvLifetime)))/(1-(1/(1+model.discountrate)))
            model.offshoreConvInvCost[i] = costperperiod

       
            # #transport
            # for i in model.Period:
            #     for v in model.VehicleTypes:
            #         costperyear = (model.WACC/(1-((1+model.WACC)**(1-model.transport_lifetime[v]))))*model.transport_vehicleCapitalCost[v,i]
            #         costperperiod = costperyear*(1-(1+model.discountrate)**-(min(value((len(model.Period)-i+1)*LeapYearsInvestment),value(model.transport_lifetime[v]))))/(1-(1/(1+model.discountrate)))
            #         model.transport_invCost[v,i] = costperperiod
    model.build_InvCost = BuildAction(rule=prepInvCost_rule)

    
    def prepInitialCapacityNodeGen_rule(model):
        #Build initial capacity for generator type in node

        for (n,g) in model.GeneratorsOfNode:
            for i in model.Period:
                if value(model.genInitCap[n,g,i]) == 0:
                    model.genInitCap[n,g,i] = model.genRefInitCap[n,g]*(1-model.genScaleInitCap[g,i])

    model.build_InitialCapacityNodeGen = BuildAction(rule=prepInitialCapacityNodeGen_rule)

    def prepInitialCapacityTransmission_rule(model):
        #Build initial capacity for transmission lines to ensure initial capacity is the upper installation bound if infeasible

        for (n1,n2) in model.BidirectionalArc:
            for i in model.Period:
                if value(model.transmissionMaxInstalledCapRaw[n1,n2,i]) <= value(model.transmissionInitCap[n1,n2,i]):
                    model.transmissionMaxInstalledCap[n1,n2,i] = model.transmissionInitCap[n1,n2,i]
                else:
                    model.transmissionMaxInstalledCap[n1,n2,i] = model.transmissionMaxInstalledCapRaw[n1,n2,i]
    model.build_InitialCapacityTransmission = BuildAction(rule=prepInitialCapacityTransmission_rule)


    def prepGenMaxInstalledCap_rule(model):
        #Build resource limit (installed limit) for all periods. Avoid infeasibility if installed limit lower than initially installed cap.
        for t in model.Technology:
            for n in model.Node:
                for i in model.Period:
                    if value(model.genMaxInstalledCapRaw[n,t] <= sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)):
                        model.genMaxInstalledCap[n,t,i] = sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)
                    elif (value(sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology))
                          < value(model.genMaxInstalledCapByPeriod[n, t, i]) < value(model.genMaxInstalledCapRaw[n, t])):
                        model.genMaxInstalledCap[n,t,i] = value(model.genMaxInstalledCapByPeriod[n,t,i])
                    else:
                        model.genMaxInstalledCap[n,t,i] = value(model.genMaxInstalledCapRaw[n,t])
    model.build_genMaxInstalledCap = BuildAction(rule=prepGenMaxInstalledCap_rule)

    def storENMaxInstalledCap_rule(model):
        #Build installed limit (resource limit) for storEN
        for (n,b) in model.StoragesOfNode:
            for i in model.Period:
                model.storENMaxInstalledCap[n,b,i]=model.storENMaxInstalledCapRaw[n,b]

    model.build_storENMaxInstalledCap = BuildAction(rule=storENMaxInstalledCap_rule)

    def storPWMaxInstalledCap_rule(model):
        #Build installed limit (resource limit) for storPW
        for (n,b) in model.StoragesOfNode:
            for i in model.Period:
                model.storPWMaxInstalledCap[n,b,i]=model.storPWMaxInstalledCapRaw[n,b]

    model.build_storPWMaxInstalledCap = BuildAction(rule=storPWMaxInstalledCap_rule)