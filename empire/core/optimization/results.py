from pathlib import Path
import csv
import os
import time

from pyomo.environ import value


def get_investment_periods(instance):
    """Terrible function to get the investment periods from the model instance. """
    inv_per = []
    for i in instance.PeriodActive:
        my_string = str(value(2020+int(i-1)*instance.LeapYearsInvestment.value))+"-"+str(value(2020+int(i)*instance.LeapYearsInvestment.value))
        inv_per.append(my_string)
    return inv_per


def write_pre_solve(
    instance,
    result_file_path,
    instance_name, 
    write_lp,
    use_temp_dir,
    temp_dir,
    logger
):
    if write_lp:
        logger.info("Writing LP-file...")
        start = time.time()
        lpstring = f"LP_{instance_name}.lp"
        if use_temp_dir:
            lpstring = temp_dir / lpstring
        instance.write(str(lpstring), io_options={'symbolic_solver_labels': True})
        end = time.time()
        logger.info("Writing LP-file took [sec]: %d", end - start)

    # Write marginal costs to results folder
    f = open(result_file_path / 'marginal_costs.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Generator","Period","MarginalCost_EurperMWh"])
    for g in instance.Generator:
        for i in instance.PeriodActive:
            writer.writerow([g, i, value(instance.genMargCost[g,i])])

    f.close()
    
    # Write investment costs to results folder
    f = open(result_file_path / 'investment_costs.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Generator","Period","InvestmentCost_EurperMW"])
    for g in instance.Generator:
        for i in instance.PeriodActive:
            writer.writerow([g, i, value(instance.genInvCost[g,i])])

    f.close()
    return 


def write_results(
        instance, 
        result_file_path: Path,
        instance_name: str,
        OUT_OF_SAMPLE: bool,
        EMISSION_CAP_FLAG: bool, 
        IAMC_PRINT: bool,
        logger,
        ) -> None:
    # Export the results to the specified file path

    

    ###########
    ##RESULTS##
    ###########

    logger.info("Writing results to .csv...")
    inv_per = get_investment_periods(instance)

    with open(result_file_path / 'results_objective.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Objective function value:" + str(value(instance.Obj))])

    with open(result_file_path / 'results_output_gen.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        my_string = ["Node","GeneratorType","Period","genInvCap_MW","genInstalledCap_MW","genExpectedCapacityFactor","DiscountedInvestmentCost_Euro","genExpectedAnnualProduction_GWh"]
        writer.writerow(my_string)
        for (n,g) in instance.GeneratorsOfNode:
            for i in instance.PeriodActive:
                writer.writerow([
                    n,
                    g,
                    inv_per[int(i-1)],
                    value(instance.genInvCap[n,g,i]),
                    value(instance.genInstalledCap[n,g,i]), 
                    value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.genOperational[n,g,h,i,w] for (s,h) in instance.HoursOfSeason for w in instance.Scenario)/(instance.genInstalledCap[n,g,i]*8760) if value(instance.genInstalledCap[n,g,i]) != 0 else 0), 
                    value(instance.discount_multiplier[i]*instance.genInvCap[n,g,i]*instance.genInvCost[g,i]),
                    value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.genOperational[n,g,h,i,w]/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario))
                ])


    f = open(result_file_path / 'results_output_stor.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Node","StorageType","Period","storPWInvCap_MW","storPWInstalledCap_MW","storENInvCap_MWh","storENInstalledCap_MWh","DiscountedInvestmentCostPWEN_EuroPerMWMWh","ExpectedAnnualDischargeVolume_GWh","ExpectedAnnualLossesChargeDischarge_GWh"])
    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            writer.writerow([
                n,
                b,
                inv_per[int(i-1)],
                value(instance.storPWInvCap[n,b,i]),
                value(instance.storPWInstalledCap[n,b,i]), 
                value(instance.storENInvCap[n,b,i]),
                value(instance.storENInstalledCap[n,b,i]), 
                value(instance.discount_multiplier[i]*(instance.storPWInvCap[n,b,i]*instance.storPWInvCost[b,i] + instance.storENInvCap[n,b,i]*instance.storENInvCost[b,i])), 
                value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.storDischarge[n,b,h,i,w]/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)), 
                value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,h,i,w] + (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario))])
    f.close()

    f = open(result_file_path / 'results_output_transmission.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["BetweenNode","AndNode","Period","transmissionInvCap_MW","transmissionInstalledCap_MW","DiscountedInvestmentCost_Euro","transmissionExpectedAnnualVolume_GWh","ExpectedAnnualLosses_GWh"])
    for (n1,n2) in instance.BidirectionalArc:
        for i in instance.PeriodActive:
            writer.writerow([
                n1,
                n2,
                inv_per[int(i-1)],
                value(instance.transmissionInvCap[n1,n2,i]),
                value(instance.transmissionInstalledCap[n1,n2,i]), 
                value(instance.discount_multiplier[i]*instance.transmissionInvCap[n1,n2,i]*instance.transmissionInvCost[n1,n2,i]), 
                value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.transmissionOperational[n1,n2,h,i,w]+instance.transmissionOperational[n2,n1,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)), 
                value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.lineEfficiency[n1,n2])*instance.transmissionOperational[n1,n2,h,i,w] + (1 - instance.lineEfficiency[n2,n1])*instance.transmissionOperational[n2,n1,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario))
            ])
    f.close()

    if not OUT_OF_SAMPLE:
        # Not interested in operational-files
        
        f = open(result_file_path / 'results_output_transmission_operational.csv', 'w', newline='')
        writer = csv.writer(f)
        writer.writerow(["FromNode","ToNode","Period","Season","Scenario","Hour","TransmissionRecieved_MW","Losses_MW"])
        for (n1,n2) in instance.DirectionalLink:
            for i in instance.PeriodActive:
                for (s,h) in instance.HoursOfSeason:
                    for w in instance.Scenario:
                        writer.writerow([
                            n1,
                            n2,
                            inv_per[int(i-1)],
                            s,
                            w,
                            h, 
                            value(instance.lineEfficiency[n1,n2]*instance.transmissionOperational[n1,n2,h,i,w]), 
                            value((1 - instance.lineEfficiency[n1,n2])*instance.transmissionOperational[n1,n2,h,i,w])
                        ])
        f.close()
        
        f = open(result_file_path / 'results_output_Operational.csv', 'w', newline='')
        writer = csv.writer(f)
        my_header = ["Node","Period","Scenario","Season","Hour","AllGen_MW","Load_MW","Net_load_MW"]
        for g in instance.Generator:
            my_string = str(g)+"_MW"
            my_header.append(my_string)
        my_header.extend(["storCharge_MW","storDischarge_MW","storEnergyLevel_MWh","LossesChargeDischargeBleed_MW","FlowOut_MW","FlowIn_MW","LossesFlowIn_MW","LoadShed_MW","Price_EURperMWh","AvgCO2_kgCO2perMWh"])    
        writer.writerow(my_header)
        for n in instance.Node:
            for i in instance.PeriodActive:
                for w in instance.Scenario:
                    for (s,h) in instance.HoursOfSeason:
                        my_string=[
                            n,
                            inv_per[int(i-1)],
                            w,
                            s,
                            h, 
                            value(sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)), 
                            value(-instance.sload[i,w,n,h]), 
                            value(-(instance.sload[i,w,n,h] - instance.loadShed[n,h,i,w] + sum(instance.storCharge[n,b,h,i,w] - instance.storageDischargeEff[b]*instance.storDischarge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode) + 
                            sum(instance.transmissionOperational[n,link,h,i,w] - instance.lineEfficiency[link,n]*instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])))
                        ]
                        for g in instance.Generator:
                            if (n,g) in instance.GeneratorsOfNode:
                                my_string.append(value(instance.genOperational[n,g,h,i,w]))
                            else:
                                my_string.append(0)
                        my_string.extend([value(sum(-instance.storCharge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                            value(sum(instance.storDischarge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                            value(sum(instance.storOperational[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                            value(sum(-(1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,h,i,w] - (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,h,i,w] - (1 - instance.storageBleedEff[b])*instance.storOperational[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                            value(sum(-instance.transmissionOperational[n,link,h,i,w] for link in instance.NodesLinked[n])), 
                            value(sum(instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])), 
                            value(sum(-(1 - instance.lineEfficiency[link,n])*instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])), 
                            value(instance.loadShed[n,h,i,w]), 
                            value(instance.dual[instance.FlowBalance[n,h,i,w]]/(instance.operationalDiscountrate*instance.seasScale[s]*instance.sceProbab[w])),
                            value(sum(instance.genOperational[n,g,h,i,w]*instance.genCO2TypeFactor[g]*(3.6/instance.genEfficiency[g,i]) for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)/sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode) if value(sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)) != 0 else 0)])
                        writer.writerow(my_string)
        f.close()

        f = open(result_file_path / 'results_output_curtailed_operational.csv', 'w', newline='')
        writer = csv.writer(f)
        writer.writerow(["Node", "Period", "Scenario", "Season", "Hour", "RESGeneratorType", "Curtailment_MWh"])
        for t in instance.Technology:
            if t == 'Hydro_ror' or t == 'Wind_onshr' or t == 'Wind_offshr' or t == 'Solar':
                for (n,g) in instance.GeneratorsOfNode:
                    if (t,g) in instance.GeneratorsOfTechnology: 
                        for i in instance.PeriodActive:
                            for w in instance.Scenario:
                                for (s,h) in instance.HoursOfSeason:
                                    writer.writerow([
                                        n,
                                        inv_per[int(i-1)],
                                        w,
                                        s,
                                        h,
                                        g,
                                        value(instance.sceProbab[w]*instance.seasScale[s]*(instance.genCapAvail[n,g,h,i,w]*instance.genInstalledCap[n,g,i] - instance.genOperational[n,g,h,i,w]))
                                    ])
        f.close()

    f = open(result_file_path / 'results_output_curtailed_prod.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Node","RESGeneratorType","Period","ExpectedAnnualCurtailment_GWh"])
    for t in instance.Technology:
        if t == 'Hydro_ror' or t == 'Wind_onshr' or t == 'Wind_offshr' or t == 'Solar':
            for (n,g) in instance.GeneratorsOfNode:
                if (t,g) in instance.GeneratorsOfTechnology: 
                    for i in instance.PeriodActive:
                        writer.writerow([
                            n,
                            g,
                            inv_per[int(i-1)], 
                            value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.genCapAvail[n,g,h,i,w]*instance.genInstalledCap[n,g,i] - instance.genOperational[n,g,h,i,w])/1000 for w in instance.Scenario for (s,h) in instance.HoursOfSeason))
                        ])
    f.close()

    f = open(result_file_path / 'results_output_EuropePlot.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Period","genInstalledCap_MW"])
    my_string=[""]
    for g in instance.Generator:
        my_string.append(g)
    writer.writerow(my_string)
    my_string=["Initial"]
    for g in instance.Generator:
        my_string.append((value(sum(instance.genInitCap[n,g,1] for n in instance.Node if (n,g) in instance.GeneratorsOfNode))))
    writer.writerow(my_string)
    for i in instance.PeriodActive:
        my_string=[inv_per[int(i-1)]]
        for g in instance.Generator:
            my_string.append(value(sum(instance.genInstalledCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)))
        writer.writerow(my_string)
    writer.writerow([""])
    writer.writerow(["Period","genExpectedAnnualProduction_GWh"])
    my_string=[""]
    for g in instance.Generator:
        my_string.append(g)
    writer.writerow(my_string)
    for i in instance.PeriodActive:
        my_string=[inv_per[int(i-1)]]
        for g in instance.Generator:
            my_string.append(value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.genOperational[n,g,h,i,w]/1000 for n in instance.Node if (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
        writer.writerow(my_string)
    writer.writerow([""])
    writer.writerow(["Period","storPWInstalledCap_MW"])
    my_string=[""]
    for b in instance.Storage:
        my_string.append(b)
    writer.writerow(my_string)
    for i in instance.PeriodActive:
        my_string=[inv_per[int(i-1)]]
        for b in instance.Storage:
            my_string.append(value(sum(instance.storPWInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))
        writer.writerow(my_string)
    writer.writerow([""])
    writer.writerow(["Period","storENInstalledCap_MW"])
    my_string=[""]
    for b in instance.Storage:
        my_string.append(b)
    writer.writerow(my_string)
    for i in instance.PeriodActive:
        my_string=[inv_per[int(i-1)]]
        for b in instance.Storage:
            my_string.append(value(sum(instance.storENInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))
        writer.writerow(my_string)
    writer.writerow([""])
    writer.writerow(["Period","storExpectedAnnualDischarge_GWh"])
    my_string=[""]
    for b in instance.Storage:
        my_string.append(b)
    writer.writerow(my_string)
    for i in instance.PeriodActive:
        my_string=[inv_per[int(i-1)]]
        for b in instance.Storage:
            my_string.append(value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.storDischarge[n,b,h,i,w]/1000 for n in instance.Node if (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
        writer.writerow(my_string)
    f.close()

    f = open(result_file_path / 'results_output_EuropeSummary.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Period","Scenario","AnnualCO2emission_Ton","CO2Price_EuroPerTon","CO2Cap_Ton","AnnualGeneration_GWh","AvgCO2factor_TonPerMWh","AvgELPrice_EuroPerMWh","TotAnnualCurtailedRES_GWh","TotAnnualLossesChargeDischarge_GWh","AnnualLossesTransmission_GWh"])
    for i in instance.PeriodActive:
        for w in instance.Scenario:
            my_string=[inv_per[int(i-1)],w, 
            value(sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w]*instance.genCO2TypeFactor[g]*(3.6/instance.genEfficiency[g,i]) for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason))]
            if EMISSION_CAP_FLAG:
                my_string.extend([value(instance.dual[instance.emission_cap[i,w]]/(instance.operationalDiscountrate*instance.sceProbab[w]*1e6)),value(instance.CO2cap[i]*1e6)])
            else:
                my_string.extend([value(instance.CO2price[i]),0])
            my_string.extend([value(sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w]/1000 for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)), 
            value(sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w]*instance.genCO2TypeFactor[g]*(3.6/instance.genEfficiency[g,i]) for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)/sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w] for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)), 
            value(sum(instance.dual[instance.FlowBalance[n,h,i,w]]/(instance.operationalDiscountrate*instance.seasScale[s]*instance.sceProbab[w]) for n in instance.Node for (s,h) in instance.HoursOfSeason)/value(len(instance.HoursOfSeason)*len(instance.Node))),
            value(sum(instance.seasScale[s]*(instance.genCapAvail[n,g,h,i,w]*instance.genInstalledCap[n,g,i] - instance.genOperational[n,g,h,i,w])/1000 for (n,g) in instance.GeneratorsOfNode if g == 'Hydrorun-of-the-river' or g == 'Windonshore' or g == 'Windoffshore' or g == 'Solar' for (s,h) in instance.HoursOfSeason)), 
            value(sum(instance.seasScale[s]*((1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,h,i,w] + (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,h,i,w])/1000 for (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason)), 
            value(sum(instance.seasScale[s]*((1 - instance.lineEfficiency[n1,n2])*instance.transmissionOperational[n1,n2,h,i,w] + (1 - instance.lineEfficiency[n2,n1])*instance.transmissionOperational[n2,n1,h,i,w])/1000 for (n1,n2) in instance.BidirectionalArc for (s,h) in instance.HoursOfSeason))])
            writer.writerow(my_string)
    writer.writerow([""])
    writer.writerow(["GeneratorType","Period","genInvCap_MW","genInstalledCap_MW","TotDiscountedInvestmentCost_Euro","genExpectedAnnualProduction_GWh"])
    for g in instance.Generator:
        for i in instance.PeriodActive:
            writer.writerow([g,inv_per[int(i-1)],value(sum(instance.genInvCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)), 
            value(sum(instance.genInstalledCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)), 
            value(sum(instance.discount_multiplier[i]*instance.genInvCap[n,g,i]*instance.genInvCost[g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)), 
            value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.genOperational[n,g,h,i,w]/1000 for n in instance.Node if (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario))])
    writer.writerow([""])
    writer.writerow(["StorageType","Period","storPWInvCap_MW","storPWInstalledCap_MW","storENInvCap_MWh","storENInstalledCap_MWh","TotDiscountedInvestmentCostPWEN_Euro","ExpectedAnnualDischargeVolume_GWh"])
    for b in instance.Storage:
        for i in instance.PeriodActive:
            writer.writerow([b,inv_per[int(i-1)],value(sum(instance.storPWInvCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)), 
            value(sum(instance.storPWInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)), 
            value(sum(instance.storENInvCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)), 
            value(sum(instance.storENInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)), 
            value(sum(instance.discount_multiplier[i]*(instance.storPWInvCap[n,b,i]*instance.storPWInvCost[b,i] + instance.storENInvCap[n,b,i]*instance.storENInvCost[b,i]) for n in instance.Node if (n,b) in instance.StoragesOfNode)), 
            value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.storDischarge[n,b,h,i,w]/1000 for n in instance.Node if (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario))])
    f.close()

    if OUT_OF_SAMPLE:
        return float(value(instance.Obj))

    # Print first stage decisions for out-of-sample
    f = open(result_file_path / 'genInvCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Generator","Period","genInvCap"])
    for (n,g) in instance.GeneratorsOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,g,i,value(instance.genInvCap[n,g,i])])
    f.close()

    f = open(result_file_path / 'transmissionInvCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["FromNode","ToNode","Period","transmissionInvCap"])
    for (n1,n2) in instance.BidirectionalArc:
        for i in instance.PeriodActive:
            writer.writerow([n1,n2,i,value(instance.transmissionInvCap[n1,n2,i])])
    f.close()

    f = open(result_file_path / 'storPWInvCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Storage","Period","storPWInvCap"])
    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,b,i,value(instance.storPWInvCap[n,b,i])])
    f.close()

    f = open(result_file_path / 'storENInvCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Storage","Period","storENInvCap"])
    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,b,i,value(instance.storENInvCap[n,b,i])])
    f.close()

    f = open(result_file_path / 'genInstalledCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Generator","Period","genInstalledCap"])
    for (n,g) in instance.GeneratorsOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,g,i,value(instance.genInstalledCap[n,g,i])])
    f.close()

    f = open(result_file_path / 'transmissionInstalledCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["FromNode","ToNode","Period","transmissionInstalledCap"])
    for (n1,n2) in instance.BidirectionalArc:
        for i in instance.PeriodActive:
            writer.writerow([n1,n2,i,value(instance.transmissionInstalledCap[n1,n2,i])])
    f.close()

    f = open(result_file_path / 'storPWInstalledCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Storage","Period","storPWInstalledCap"])
    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,b,i,value(instance.storPWInstalledCap[n,b,i])])
    f.close()

    f = open(result_file_path / 'storENInstalledCap.tab', 'w', newline='')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Node","Storage","Period","storENInstalledCap"])
    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            writer.writerow([n,b,i,value(instance.storENInstalledCap[n,b,i])])
    f.close()

    if IAMC_PRINT:
        ####################
        ###STANDARD PRINT###
        ####################
        
        import pandas as pd
        
        Modelname = "EMPIRE"
        Scenario = "1.5degree"

        dict_countries = {"Austria": "Austria",
                          "Bosnia and Herzegovina": "BosniaH",
                          "Belgium": "Belgium", "Bulgaria": "Bulgaria",
                          "Switzerland": "Switzerland", 
                          "Czech Republic": "CzechR", "Germany": "Germany",
                          "Denmark": "Denmark", "Estonia": "Estonia", 
                          "Spain": "Spain", "Finland": "Finland",
                          "France": "France", "United Kingdom": "GreatBrit.",
                          "Greece": "Greece", "Croatia": "Croatia", 
                          "Hungary": "Hungary", "Ireland": "Ireland", 
                          "Italy": "Italy", "Lithuania": "Lithuania",
                          "Luxembourg": "Luxemb.", "Latvia": "Latvia",
                          "North Macedonia": "Macedonia", 
                          "The Netherlands": "Netherlands", "Norway": "Norway",
                          "Poland": "Poland", "Portugal": "Portugal",
                          "Romania": "Romania", "Serbia": "Serbia", 
                          "Sweden": "Sweden", "Slovenia": "Slovenia",
                          "Slovakia": "Slovakia", "Norway|Ostland": "NO1", 
                          "Norway|Sorland": "NO2", "Norway|Norgemidt": "NO3",
                          "Norway|Troms": "NO4", "Norway|Vestmidt": "NO5"}

        dict_countries_reversed = dict([reversed(i) for i in dict_countries.items()])

        dict_generators = {"Bio": "Biomass", "Bioexisting": "Biomass",
                           "Coalexisting": "Coal|w/o CCS",
                           "Coal": "Coal|w/o CCS", "CoalCCS": "Coal|w/ CCS",
                           "CoalCCSadv": "Coal|w/ CCS", 
                           "Lignite": "Lignite|w/o CCS",
                           "Liginiteexisting": "Lignite|w/o CCS", 
                           "LigniteCCSadv": "Lignite|w/ CCS", 
                           "Gasexisting": "Gas|CCGT|w/o CCS", 
                           "GasOCGT": "Gas|OCGT|w/o CCS", 
                           "GasCCGT": "Gas|CCGT|w/o CCS", 
                           "GasCCS": "Gas|CCGT|w/ CCS", 
                           "GasCCSadv": "Gas|CCGT|w/ CCS", 
                           "Oilexisting": "Oil", "Nuclear": "Nuclear", 
                           "Wave": "Ocean", "Geo": "Geothermal", 
                           "Hydroregulated": "Hydro|Reservoir", 
                           "Hydrorun-of-the-river": "Hydro|Run-of-River", 
                           "Windonshore": "Wind|Onshore", 
                           "Windoffshore": "Wind|Offshore",
                           "Windoffshoregrounded": "Wind|Offshore", 
                           "Windoffshorefloating": "Wind|Offshore", 
                           "Solar": "Solar|PV", "Waste": "Waste", 
                           "Bio10cofiring": "Coal|w/o CCS", 
                           "Bio10cofiringCCS": "Coal|w/ CCS", 
                           "LigniteCCSsup": "Lignite|w/ CCS"}
        
        #Make datetime from HoursOfSeason       
        seasonstart={"winter": '2020-01-01',
                     "spring": '2020-04-01',
                     "summer": '2020-07-01',
                     "fall": '2020-10-01',
                     "peak1": '2020-11-01',
                     "peak2": '2020-12-01'}
        
        seasonhours=[]
    
        for s in instance.Season:
            if s not in 'peak':
                t=pd.to_datetime(list(range(instance.lengthRegSeason.value)), unit='h', origin=pd.Timestamp(seasonstart[s]))
                t=[str(i)[5:-3] for i in t]
                t=[str(i)+"+01:00" for i in t]
                seasonhours+=t
            else:
                t=pd.to_datetime(list(range(instance.lengthPeakSeason.value)), unit='h', origin=pd.Timestamp(seasonstart[s]))
                t=[str(i)[5:-3] for i in t]
                t=[str(i)+"+01:00" for i in t]
                seasonhours+=t       
        
        #Scalefactors to make units
        Mtonperton = (1/1000000)

        GJperMWh = 3.6
        EJperMWh = 3.6*10**(-9)

        GWperMW = (1/1000)

        USD10perEUR10 = 1.33 #Source: https://www.statista.com/statistics/412794/euro-to-u-s-dollar-annual-average-exchange-rate/ 
        EUR10perEUR18 = 154/171 #Source: https://www.inflationtool.com/euro 
        USD10perEUR18 = USD10perEUR10*EUR10perEUR18 

        logger.info("Writing standard output to .csv...")
        
        f = pd.DataFrame(columns=["model", "scenario", "region", "variable", "unit", "subannual"]+[value(2020+(i)*instance.LeapYearsInvestment) for i in instance.PeriodActive])

        def row_write(df, region, variable, unit, subannual, input_value, scenario=Scenario, modelname=Modelname):
            df2 = pd.DataFrame([[modelname, scenario, region, variable, unit, subannual]+input_value],
                               columns=["model", "scenario", "region", "variable", "unit", "subannual"]+[value(2020+(i)*instance.LeapYearsInvestment) for i in instance.PeriodActive])
            df = pd.concat([df, df2], ignore_index=True)
            return df

        f = row_write(f, "Europe", "Discount rate|Electricity", "%", "Year", [value(instance.discountrate*100)]*len(instance.PeriodActive)) #Discount rate
        f = row_write(f, "Europe", "Capacity|Electricity", "GW", "Year", [value(sum(instance.genInstalledCap[n,g,i]*GWperMW for (n,g) in instance.GeneratorsOfNode)) for i in instance.PeriodActive]) #Total European installed generator capacity 
        f = row_write(f, "Europe", "Investment|Energy Supply|Electricity", "billion US$2010/yr", "Year", [value((1/instance.LeapYearsInvestment)*USD10perEUR18* \
                    sum(instance.genInvCost[g,i]*instance.genInvCap[n,g,i] for (n,g) in instance.GeneratorsOfNode) + \
                    sum(instance.transmissionInvCost[n1,n2,i]*instance.transmissionInvCap[n1,n2,i] for (n1,n2) in instance.BidirectionalArc) + \
                    sum((instance.storPWInvCost[b,i]*instance.storPWInvCap[n,b,i]+instance.storENInvCost[b,i]*instance.storENInvCap[n,b,i]) for (n,b) in instance.StoragesOfNode)) for i in instance.PeriodActive]) #Total European investment cost (gen+stor+trans)
        f = row_write(f, "Europe", "Investment|Energy Supply|Electricity|Electricity storage", "billion US$2010/yr", "Year", [value((1/instance.LeapYearsInvestment)*USD10perEUR18* \
                    sum((instance.storPWInvCost[b,i]*instance.storPWInvCap[n,b,i]+instance.storENInvCost[b,i]*instance.storENInvCap[n,b,i]) for (n,b) in instance.StoragesOfNode)) for i in instance.PeriodActive]) #Total European storage investment cost
        f = row_write(f, "Europe", "Investment|Energy Supply|Electricity|Transmission and Distribution", "billion US$2010/yr", "Year", [value((1/instance.LeapYearsInvestment)*USD10perEUR18* \
                    sum(instance.transmissionInvCost[n1,n2,i]*instance.transmissionInvCap[n1,n2,i] for (n1,n2) in instance.BidirectionalArc)) for i in instance.PeriodActive]) #Total European transmission investment cost
        for w in instance.Scenario:
            f = row_write(f, "Europe", "Emissions|CO2|Energy|Supply|Electricity", "Mt CO2/yr", "Year", [value(Mtonperton*sum(instance.seasScale[s]*instance.genCO2TypeFactor[g]*(GJperMWh/instance.genEfficiency[g,i])* \
                    instance.genOperational[n,g,h,i,w] for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)) for i in instance.PeriodActive], Scenario+"|"+str(w)) #Total European emissions per scenario
            f = row_write(f, "Europe", "Secondary Energy|Electricity", "EJ/yr", "Year", \
                    [value(sum(EJperMWh*instance.seasScale[s]*instance.genOperational[n,g,h,i,w] for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)) for i in instance.PeriodActive], Scenario+"|"+str(w)) #Total European generation per scenario
            for g in instance.Generator:
                f = row_write(f, "Europe", "Active Power|Electricity|"+dict_generators[str(g)], "MWh", "Year", \
                    [value(sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w] for n in instance.Node if (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason)) for i in instance.PeriodActive], Scenario+"|"+str(w)) #Total generation per type and scenario
            for (s,h) in instance.HoursOfSeason:
                for n in instance.Node:
                    f = row_write(f, dict_countries_reversed[str(n)], "Price|Secondary Energy|Electricity", "US$2010/GJ", seasonhours[h-1], \
                        [value(instance.dual[instance.FlowBalance[n,h,i,w]]/(GJperMWh*instance.operationalDiscountrate*instance.seasScale[s]*instance.sceProbab[w])) for i in instance.PeriodActive], Scenario+"|"+str(w)+str(s))
        for g in instance.Generator:
            f = row_write(f, "Europe", "Capacity|Electricity|"+dict_generators[str(g)], "GW", "Year", [value(sum(instance.genInstalledCap[n,g,i]*GWperMW for n in instance.Node if (n,g) in instance.GeneratorsOfNode)) for i in instance.PeriodActive]) #Total European installed generator capacity per type
            f = row_write(f, "Europe", "Capital Cost|Electricity|"+dict_generators[str(g)], "US$2010/kW", "Year", [value(instance.genCapitalCost[g,i]*USD10perEUR18) for i in instance.PeriodActive]) #Capital generator cost
            if value(instance.genMargCost[g,instance.PeriodActive[1]]) != 0: 
                f = row_write(f, "Europe", "Variable Cost|Electricity|"+dict_generators[str(g)], "EUR/MWh", "Year", [value(instance.genMargCost[g,i]) for i in instance.PeriodActive])
            f = row_write(f, "Europe", "Investment|Energy Supply|Electricity|"+dict_generators[str(g)], "billion US$2010/yr", "Year", [value((1/instance.LeapYearsInvestment)*USD10perEUR18* \
                    sum(instance.genInvCost[g,i]*instance.genInvCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)) for i in instance.PeriodActive]) #Total generator investment cost per type
            if value(instance.genCO2TypeFactor[g]) != 0:
                f = row_write(f, "Europe", "CO2 Emmissions|Electricity|"+dict_generators[str(g)], "tons/MWh", "Year", [value(instance.genCO2TypeFactor[g]*(GJperMWh/instance.genEfficiency[g,i])) for i in instance.PeriodActive]) #CO2 factor per generator type
        for (n,g) in instance.GeneratorsOfNode:
            f = row_write(f, dict_countries_reversed[str(n)], "Capacity|Electricity|"+dict_generators[str(g)], "GW", "Year", [value(instance.genInstalledCap[n,g,i]*GWperMW) for i in instance.PeriodActive]) #Installed generator capacity per country and type
        
        f = f.groupby(['model','scenario','region','variable','unit','subannual']).sum().reset_index() #NB! DOES NOT WORK FOR UNIT COSTS; SHOULD BE FIXED
        
        if not os.path.exists(result_file_path / 'IAMC'):
            os.makedirs(result_file_path / 'IAMC')
        f.to_csv(result_file_path / 'IAMC/empire_iamc.csv', index=None)



def run_operational_model(
    instance, 
    opt,
    result_file_path,
    instance_name,
    logger
    ):

    logger.info("Computing operational dual values by fixing investment variables and resolving.")

    logger.info("Fixing investment variables")
    for (n,g) in instance.GeneratorsOfNode:
        for i in instance.PeriodActive:
            instance.genInvCap[n,g,i].fix()

    for (n1,n2) in instance.BidirectionalArc:
        for i in instance.PeriodActive:        
            instance.transmissionInvCap[n1,n2,i].fix()

    for (n,b) in instance.StoragesOfNode:
        for i in instance.PeriodActive:
            instance.storPWInvCap[n,b,i].fix()
            instance.storENInvCap[n,b,i].fix()

    logger.info("Resolving")

    opt.solve(instance, tee=True, logfile=result_file_path / f"logfile_{instance_name}_resolved.log")
    return 

def write_operational_results(
    instance,
    result_file_path,
    emission_cap_flag,
    logger
    ) -> None:

    logger.info("Writing new operational results to .csv..")
    inv_per = get_investment_periods(instance)
    f = open(result_file_path / 'results_output_Operational_resolved.csv', 'w', newline='')
    writer = csv.writer(f)
    my_header = ["Node","Period","Scenario","Season","Hour","AllGen_MW","Load_MW","Net_load_MW"]
    for g in instance.Generator:
        my_string = str(g)+"_MW"
        my_header.append(my_string)
    my_header.extend(["storCharge_MW","storDischarge_MW","storEnergyLevel_MWh","LossesChargeDischargeBleed_MW","FlowOut_MW","FlowIn_MW","LossesFlowIn_MW","LoadShed_MW","Price_EURperMWh","AvgCO2_kgCO2perMWh"])    
    writer.writerow(my_header)
    for n in instance.Node:
        for i in instance.PeriodActive:
            for w in instance.Scenario:
                for (s,h) in instance.HoursOfSeason:
                    my_string=[n,inv_per[int(i-1)],w,s,h, 
                        value(sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)), 
                        value(-instance.sload[i,w,n,h]), 
                        value(-(instance.sload[i,w,n,h] - instance.loadShed[n,h,i,w] + sum(instance.storCharge[n,b,h,i,w] - instance.storageDischargeEff[b]*instance.storDischarge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode) + 
                        sum(instance.transmissionOperational[n,link,h,i,w] - instance.lineEfficiency[link,n]*instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])))]
                    for g in instance.Generator:
                        if (n,g) in instance.GeneratorsOfNode:
                            my_string.append(value(instance.genOperational[n,g,h,i,w]))
                        else:
                            my_string.append(0)
                    my_string.extend([value(sum(-instance.storCharge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                        value(sum(instance.storDischarge[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                        value(sum(instance.storOperational[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                        value(sum(-(1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,h,i,w] - (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,h,i,w] - (1 - instance.storageBleedEff[b])*instance.storOperational[n,b,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)), 
                        value(sum(-instance.transmissionOperational[n,link,h,i,w] for link in instance.NodesLinked[n])), 
                        value(sum(instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])), 
                        value(sum(-(1 - instance.lineEfficiency[link,n])*instance.transmissionOperational[link,n,h,i,w] for link in instance.NodesLinked[n])), 
                        value(instance.loadShed[n,h,i,w]), 
                        value(instance.dual[instance.FlowBalance[n,h,i,w]]/(instance.operationalDiscountrate*instance.seasScale[s]*instance.sceProbab[w])),
                        value(sum(instance.genOperational[n,g,h,i,w]*instance.genCO2TypeFactor[g]*(3.6/instance.genEfficiency[g,i]) for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)/sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode) if value(sum(instance.genOperational[n,g,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)) != 0 else 0)])
                    writer.writerow(my_string)
    f.close()

    f = open(result_file_path / 'results_co2_price_resolved.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Period","Scenario","AnnualCO2emission_Ton","CO2Price_EuroPerTon"])
    for i in instance.PeriodActive:
        for w in instance.Scenario:
            my_string=[inv_per[int(i-1)],w, 
            value(sum(instance.seasScale[s]*instance.genOperational[n,g,h,i,w]*instance.genCO2TypeFactor[g]*(3.6/instance.genEfficiency[g,i]) for (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason))]
            if emission_cap_flag:
                my_string.extend([value(instance.dual[instance.emission_cap[i,w]]/(instance.operationalDiscountrate*instance.sceProbab[w]*1e6)),value(instance.CO2cap[i]*1e6)])
            else:
                my_string.extend([value(instance.CO2price[i]),0])