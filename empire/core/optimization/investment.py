from pyomo.environ import AbstractModel, Constraint, value, BuildAction, Param, Var, NonNegativeReals
from .loading_utils import load_parameters


def define_investment_parameters(model, wacc):
    
    #Cost
    model.WACC = Param(initialize=wacc) # investment only

    model.genCapitalCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.transmissionTypeCapitalCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.storPWCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.genFixedOMCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.transmissionTypeFixedOMCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.storPWFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.genInvCost = Param(model.Generator, model.Period, default=9000000, mutable=True)
    
    model.transmissionInvCost = Param(model.BidirectionalArc, model.Period, default=3000000, mutable=True)
    model.storPWInvCost = Param(model.Storage, model.Period, default=1000000, mutable=True)
    model.storENInvCost = Param(model.Storage, model.Period, default=800000, mutable=True)
    model.transmissionLength = Param(model.BidirectionalArc, default=0, mutable=True)


    #Node dependent technology limitations
    model.genRefInitCap = Param(model.GeneratorsOfNode, default=0.0, mutable=True)
    model.genScaleInitCap = Param(model.Generator, model.Period, default=0.0, mutable=True)
    model.genInitCap = Param(model.GeneratorsOfNode, model.Period, default=0.0, mutable=True)
    model.transmissionInitCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.storPWInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.genMaxBuiltCap = Param(model.Node, model.Technology, model.Period, default=500000.0, mutable=True)
    model.transmissionMaxBuiltCap = Param(model.BidirectionalArc, model.Period, default=20000.0, mutable=True)
    model.storPWMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storENMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.genMaxInstalledCapRaw = Param(model.Node, model.Technology, default=0.0, mutable=True)
    model.genMaxInstalledCap = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
    model.transmissionMaxInstalledCapRaw = Param(model.BidirectionalArc, model.Period, default=0.0)
    model.transmissionMaxInstalledCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.storPWMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storPWMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)
    model.storENMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)

    model.genLifetime = Param(model.Generator, default=0.0, mutable=True)
    model.transmissionLifetime = Param(model.BidirectionalArc, default=40.0, mutable=True)
    model.storageLifetime = Param(model.Storage, default=0.0, mutable=True)
    return 


def load_investment_parameters(model, data, dataset_dir) -> None:
    investment_parameters = {
    "Generator": [
        "genCapitalCost",
        "genFixedOMCost",
        "genRefInitCap",
        "genScaleInitCap",
        "genInitCap",
        "genMaxBuiltCap",
        "genMaxInstalledCapRaw",
        "genLifetime",
    ],

    "Transmission": [
        "transmissionInitCap",
        "transmissionMaxBuiltCap",
        "transmissionMaxInstalledCapRaw",
        "transmissionLength",
        "transmissionTypeCapitalCost",
        "transmissionTypeFixedOMCost",
        "transmissionLifetime",
    ],

    "Storage": [
        "storENCapitalCost",
        "storENFixedOMCost",
        "storENInitCap",
        "storENMaxBuiltCap",
        "storENMaxInstalledCapRaw",
        "storPWCapitalCost",
        "storPWFixedOMCost",
        "storPWInitCap",
        "storPWMaxBuiltCap",
        "storPWMaxInstalledCapRaw",
        "storageLifetime",
    ],
    }
    for component, param_list in investment_parameters.items():
        load_parameters(
            data,
            full_path=dataset_dir / component,
            param_name_list=param_list,
            model=model,
        )
    return 


def define_investment_variables(model: AbstractModel) -> None:
    model.genInvCap = Var(model.GeneratorsOfNode, model.PeriodActive, domain=NonNegativeReals)
    model.transmissionInvCap = Var(model.BidirectionalArc, model.PeriodActive, domain=NonNegativeReals)
    model.storPWInvCap = Var(model.StoragesOfNode, model.PeriodActive, domain=NonNegativeReals)
    model.storENInvCap = Var(model.StoragesOfNode, model.PeriodActive, domain=NonNegativeReals)
    model.genInstalledCap = Var(model.GeneratorsOfNode, model.PeriodActive, domain=NonNegativeReals)
    model.transmissionInstalledCap = Var(model.BidirectionalArc, model.PeriodActive, domain=NonNegativeReals)
    model.storPWInstalledCap = Var(model.StoragesOfNode, model.PeriodActive, domain=NonNegativeReals)
    model.storENInstalledCap = Var(model.StoragesOfNode, model.PeriodActive, domain=NonNegativeReals)
    return 


def prep_investment_parameters(
        model: AbstractModel
    ):
    
    def prepInvCost_rule(model):
        #Build investment cost for generators, storages and transmission. Annual cost is calculated for the lifetime of the generator and discounted for a year.
        #Then cost is discounted for the investment period (or the remaining lifetime). 

        #Generator 
        for g in model.Generator:
            for i in model.PeriodActive:
                costperyear=(model.WACC/(1-((1+model.WACC)**(-model.genLifetime[g]))))*model.genCapitalCost[g,i]+model.genFixedOMCost[g,i]
                costperperiod=costperyear*1000*(1-(1+model.discountrate)**-(min(value((len(model.PeriodActive)-i+1)*model.LeapYearsInvestment), value(model.genLifetime[g]))))/(1-(1/(1+model.discountrate)))
                model.genInvCost[g,i]=costperperiod

        #Storage
        for b in model.Storage:
            for i in model.PeriodActive:
                costperyearPW=(model.WACC/(1-((1+model.WACC)**(-model.storageLifetime[b]))))*model.storPWCapitalCost[b,i]+model.storPWFixedOMCost[b,i]
                costperperiodPW=costperyearPW*1000*(1-(1+model.discountrate)**-(min(value((len(model.PeriodActive)-i+1)*model.LeapYearsInvestment), value(model.storageLifetime[b]))))/(1-(1/(1+model.discountrate)))
                model.storPWInvCost[b,i]=costperperiodPW
                costperyearEN=(model.WACC/(1-((1+model.WACC)**(-model.storageLifetime[b]))))*model.storENCapitalCost[b,i]+model.storENFixedOMCost[b,i]
                costperperiodEN=costperyearEN*1000*(1-(1+model.discountrate)**-(min(value((len(model.PeriodActive)-i+1)*model.LeapYearsInvestment), value(model.storageLifetime[b]))))/(1-(1/(1+model.discountrate)))
                model.storENInvCost[b,i]=costperperiodEN

        #Transmission
        for (n1,n2) in model.BidirectionalArc:
            for i in model.PeriodActive:
                for t in model.TransmissionType:
                    if (n1,n2,t) in model.TransmissionTypeOfDirectionalLink:
                        costperyear=(model.WACC/(1-((1+model.WACC)**(-model.transmissionLifetime[n1,n2]))))*model.transmissionLength[n1,n2]*model.transmissionTypeCapitalCost[t,i]+model.transmissionLength[n1,n2]*model.transmissionTypeFixedOMCost[t,i] 
                        costperperiod=costperyear*(1-(1+model.discountrate)**-(min(value((len(model.PeriodActive)-i+1)*model.LeapYearsInvestment), value(model.transmissionLifetime[n1,n2]))))/(1-(1/(1+model.discountrate)))
                        model.transmissionInvCost[n1,n2,i]=costperperiod

    model.build_InvCost = BuildAction(rule=prepInvCost_rule)


    def prepInitialCapacityNodeGen_rule(model):
        #Build initial capacity for generator type in node

        for (n,g) in model.GeneratorsOfNode:
            for i in model.PeriodActive:
                if value(model.genInitCap[n,g,i]) == 0:
                    model.genInitCap[n,g,i] = model.genRefInitCap[n,g]*(1-model.genScaleInitCap[g,i])

    model.build_InitialCapacityNodeGen = BuildAction(rule=prepInitialCapacityNodeGen_rule)

    def prepInitialCapacityTransmission_rule(model):
        #Build initial capacity for transmission lines to ensure initial capacity is the upper installation bound if infeasible

        for (n1,n2) in model.BidirectionalArc:
            for i in model.PeriodActive:
                if value(model.transmissionMaxInstalledCapRaw[n1,n2,i]) <= value(model.transmissionInitCap[n1,n2,i]):
                    model.transmissionMaxInstalledCap[n1,n2,i] = model.transmissionInitCap[n1,n2,i]
                else:
                    model.transmissionMaxInstalledCap[n1,n2,i] = model.transmissionMaxInstalledCapRaw[n1,n2,i]

    model.build_InitialCapacityTransmission = BuildAction(rule=prepInitialCapacityTransmission_rule)


    def prepGenMaxInstalledCap_rule(model):
        #Build resource limit (installed limit) for all Period. Avoid infeasibility if installed limit lower than initially installed cap.

        for t in model.Technology:
            for n in model.Node:
                for i in model.PeriodActive:
                    if value(model.genMaxInstalledCapRaw[n,t] <= sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)):
                        model.genMaxInstalledCap[n,t,i]=sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)
                    else:
                        model.genMaxInstalledCap[n,t,i]=model.genMaxInstalledCapRaw[n,t]
                        
    model.build_genMaxInstalledCap = BuildAction(rule=prepGenMaxInstalledCap_rule)

    def storENMaxInstalledCap_rule(model):
        #Build installed limit (resource limit) for storEN

        for (n,b) in model.StoragesOfNode:
            for i in model.PeriodActive:
                model.storENMaxInstalledCap[n,b,i]=model.storENMaxInstalledCapRaw[n,b]

    model.build_storENMaxInstalledCap = BuildAction(rule=storENMaxInstalledCap_rule)

    def storPWMaxInstalledCap_rule(model):
        #Build installed limit (resource limit) for storPW

        for (n,b) in model.StoragesOfNode:
            for i in model.PeriodActive:
                model.storPWMaxInstalledCap[n,b,i]=model.storPWMaxInstalledCapRaw[n,b]

    model.build_storPWMaxInstalledCap = BuildAction(rule=storPWMaxInstalledCap_rule)
    return 


def define_investment_constraints(
    model: AbstractModel,
    north_sea_flag: bool
    ):
    def lifetime_rule_gen(model, n, g, i):
        startPeriod=1
        if value(1+i-(model.genLifetime[g]/model.LeapYearsInvestment))>startPeriod:
            startPeriod=value(1+i-model.genLifetime[g]/model.LeapYearsInvestment)
        return sum(model.genInvCap[n,g,j]  for j in model.PeriodActive if j>=startPeriod and j<=i ) - model.genInstalledCap[n,g,i] + model.genInitCap[n,g,i]== 0   #
    model.installedCapDefinitionGen = Constraint(model.GeneratorsOfNode, model.PeriodActive, rule=lifetime_rule_gen)

    def lifetime_rule_trans(model, n1, n2, i):
        startPeriod=1
        if value(1+i-model.transmissionLifetime[n1,n2]*(1/model.LeapYearsInvestment))>startPeriod:
            startPeriod=value(1+i-model.transmissionLifetime[n1,n2]/model.LeapYearsInvestment)
        return sum(model.transmissionInvCap[n1,n2,j]  for j in model.PeriodActive if j>=startPeriod and j<=i )- model.transmissionInstalledCap[n1,n2,i] + model.transmissionInitCap[n1,n2,i] == 0   #
    model.installedCapDefinitionTrans = Constraint(model.BidirectionalArc, model.PeriodActive, rule=lifetime_rule_trans)

    def lifetime_rule_storEN(model, n, b, i):
        startPeriod=1
        if value(1+i-model.storageLifetime[b]*(1/model.LeapYearsInvestment))>startPeriod:
            startPeriod=value(1+i-model.storageLifetime[b]/model.LeapYearsInvestment)
        return sum(model.storENInvCap[n,b,j]  for j in model.PeriodActive if j>=startPeriod and j<=i )- model.storENInstalledCap[n,b,i] + model.storENInitCap[n,b,i]== 0   #
    model.installedCapDefinitionStorEN = Constraint(model.StoragesOfNode, model.PeriodActive, rule=lifetime_rule_storEN)

    def lifetime_rule_storPOW(model, n, b, i):
        startPeriod=1
        if value(1+i-model.storageLifetime[b]*(1/model.LeapYearsInvestment))>startPeriod:
            startPeriod=value(1+i-model.storageLifetime[b]/model.LeapYearsInvestment)
        return sum(model.storPWInvCap[n,b,j]  for j in model.PeriodActive if j>=startPeriod and j<=i )- model.storPWInstalledCap[n,b,i] + model.storPWInitCap[n,b,i]== 0   #
    model.installedCapDefinitionStorPOW = Constraint(model.StoragesOfNode, model.PeriodActive, rule=lifetime_rule_storPOW)

    def investment_gen_cap_rule(model, t, n, i):
        return sum(model.genInvCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology) - model.genMaxBuiltCap[n,t,i] <= 0
    model.investment_gen_cap = Constraint(model.Technology, model.Node, model.PeriodActive, rule=investment_gen_cap_rule)

    def investment_trans_cap_rule(model, n1, n2, i):
        return model.transmissionInvCap[n1,n2,i] - model.transmissionMaxBuiltCap[n1,n2,i] <= 0
    model.investment_trans_cap = Constraint(model.BidirectionalArc, model.PeriodActive, rule=investment_trans_cap_rule)

    def investment_storage_power_cap_rule(model, n, b, i):
        return model.storPWInvCap[n,b,i] - model.storPWMaxBuiltCap[n,b,i] <= 0
    model.investment_storage_power_cap = Constraint(model.StoragesOfNode, model.PeriodActive, rule=investment_storage_power_cap_rule)

    def investment_storage_energy_cap_rule(model, n, b, i):
        return model.storENInvCap[n,b,i] - model.storENMaxBuiltCap[n,b,i] <= 0
    model.investment_storage_energy_cap = Constraint(model.StoragesOfNode, model.PeriodActive, rule=investment_storage_energy_cap_rule)

    def installed_gen_cap_rule(model, t, n, i):
        return sum(model.genInstalledCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology) - model.genMaxInstalledCap[n,t,i] <= 0
    model.installed_gen_cap = Constraint(model.Technology, model.Node, model.PeriodActive, rule=installed_gen_cap_rule)

    def installed_trans_cap_rule(model, n1, n2, i):
        return model.transmissionInstalledCap[n1,n2,i] - model.transmissionMaxInstalledCap[n1,n2,i] <= 0
    model.installed_trans_cap = Constraint(model.BidirectionalArc, model.PeriodActive, rule=installed_trans_cap_rule)

    def installed_storage_power_cap_rule(model, n, b, i):
        return model.storPWInstalledCap[n,b,i] - model.storPWMaxInstalledCap[n,b,i] <= 0
    model.installed_storage_power_cap = Constraint(model.StoragesOfNode, model.PeriodActive, rule=installed_storage_power_cap_rule)

    def installed_storage_energy_cap_rule(model, n, b, i):
        return model.storENInstalledCap[n,b,i] - model.storENMaxInstalledCap[n,b,i] <= 0
    model.installed_storage_energy_cap = Constraint(model.StoragesOfNode, model.PeriodActive, rule=installed_storage_energy_cap_rule)

    def power_energy_relate_rule(model, n, b, i):
        if b in model.DependentStorage:
            return model.storPWInstalledCap[n,b,i] - model.storagePowToEnergy[b]*model.storENInstalledCap[n,b,i] == 0   #
        else:
            return Constraint.Skip
    model.power_energy_relate = Constraint(model.StoragesOfNode, model.PeriodActive, rule=power_energy_relate_rule)

    if north_sea_flag:
        def wind_farm_tranmission_cap_rule(model, n1, n2, i):
            if n1 in model.OffshoreNode or n2 in model.OffshoreNode:
                if (n1,n2) in model.BidirectionalArc:
                    if n1 in model.OffshoreNode:
                        return model.transmissionInstalledCap[(n1,n2),i] <= sum(model.genInstalledCap[n1,g,i] for g in model.Generator if (n1,g) in model.GeneratorsOfNode)
                    else:
                        return model.transmissionInstalledCap[(n1,n2),i] <= sum(model.genInstalledCap[n2,g,i] for g in model.Generator if (n2,g) in model.GeneratorsOfNode)
                elif (n2,n1) in model.BidirectionalArc:
                    if n1 in model.OffshoreNode:
                        return model.transmissionInstalledCap[(n2,n1),i] <= sum(model.genInstalledCap[n1,g,i] for g in model.Generator if (n1,g) in model.GeneratorsOfNode)
                    else:
                        return model.transmissionInstalledCap[(n2,n1),i] <= sum(model.genInstalledCap[n2,g,i] for g in model.Generator if (n2,g) in model.GeneratorsOfNode)
                else:
                    return Constraint.Skip
            else:
                return Constraint.Skip
        model.wind_farm_transmission_cap = Constraint(model.Node, model.Node, model.PeriodActive, rule=wind_farm_tranmission_cap_rule)
    return 