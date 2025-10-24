from pyomo.environ import Constraint, Set, Var, value, BuildAction, Expression, AbstractModel, NonNegativeReals, Param, PercentFraction, ConcreteModel
import logging
from empire.core.config import OperationalInputParams
from .loading_utils import load_set_directly, load_data_from_files, load_params
import pandas as pd


logger = logging.getLogger(__name__)


def define_operational_sets(model: AbstractModel, operational_input_params: OperationalInputParams):
    # operational sets
    model.Operationalhour = Set(ordered=True, initialize=operational_input_params.Operationalhour) #h
    model.Season = Set(ordered=True, initialize=operational_input_params.Season) #s
    model.Scenario = Set(ordered=True) #w
    model.HoursOfSeason = Set(dimen=2, ordered=True, initialize=operational_input_params.HoursOfSeason) #(s,h) for all s in S, h in H_s
    model.FirstHoursOfRegSeason = Set(within=model.Operationalhour, ordered=True, initialize=operational_input_params.FirstHoursOfRegSeason)
    model.FirstHoursOfPeakSeason = Set(within=model.Operationalhour, ordered=True, initialize=operational_input_params.FirstHoursOfPeakSeason)

    return 


def define_operational_variables(
        model: AbstractModel
    ):
    # Define operational variables for the model
    model.genOperational = Var(model.GeneratorsOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals)
    model.storOperational = Var(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals)
    model.transmissionOperational = Var(model.DirectionalLink, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals) 
    model.storCharge = Var(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals)
    model.storDischarge = Var(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals)
    model.loadShed = Var(model.Node, model.Operationalhour, model.PeriodActive, model.Scenario, domain=NonNegativeReals)
    return 


def define_operational_parameters(
        model: AbstractModel,
        operational_input_params: OperationalInputParams,
    ):
    # operational deterministic parameters 
    model.operationalDiscountrate = Param(mutable=True)
    model.seasScale = Param(model.Season, initialize=1.0, mutable=True)
    model.lengthRegSeason = Param(initialize=operational_input_params.lengthRegSeason, mutable=False)
    model.lengthPeakSeason = Param(initialize=operational_input_params.lengthPeakSeason, mutable=False)

    model.lineEfficiency = Param(model.DirectionalLink, default=0.97, mutable=True)
    model.lineReactance   = Param(model.BidirectionalArc, default=0.0, mutable=True)
    model.lineSusceptance = Param(model.BidirectionalArc, default=0.0, mutable=True)
    model.storageChargeEff = Param(model.Storage, default=1.0, mutable=True)
    model.storageDischargeEff = Param(model.Storage, default=1.0, mutable=True)
    model.storageBleedEff = Param(model.Storage, default=1.0, mutable=True)
    model.genRampUpCap = Param(model.ThermalGenerators, default=0.0, mutable=True)
    model.storageDiscToCharRatio = Param(model.Storage, default=1.0, mutable=True) #NB! Hard-coded
    model.genCO2TypeFactor = Param(model.Generator, default=0.0, mutable=True)
    model.genVariableOMCost = Param(model.Generator, default=0.0, mutable=True)
    model.CCSRemFrac = Param(initialize=0.9)
    model.maxHydroNode = Param(model.Node, default=0.0, mutable=True)
    model.genCapAvailTypeRaw = Param(model.Generator, default=1.0, mutable=True)
    model.storOperationalInit = Param(model.Storage, default=0.0, mutable=True) #Percentage of installed energy capacity initially
    return 


def define_period_and_scenario_dependent_parameters(model: AbstractModel, emission_cap_flag: bool):
    # scenario and/or period-dependent parameters
    model.sceProbab = Param(model.Scenario, mutable=True)
    model.genEfficiency = Param(model.Generator, model.Period, mutable=True)
    model.sloadAnnualDemand = Param(model.Node, model.Period, mutable=True)
    model.genMargCost = Param(model.Generator, model.Period, mutable=True)
    model.nodeLostLoadCost = Param(model.Node, model.Period, default=22000.0)
    model.genFuelCost = Param(model.Generator, model.Period, mutable=True)
    model.CO2price = Param(model.Period, mutable=True)

    model.CCSCostTSVariable = Param(model.Period, default=0.0, mutable=True)
    if emission_cap_flag:
        model.CO2cap = Param(model.Period, default=5000.0, mutable=True)
    return 


def define_stochastic_input(model):
    model.sloadRaw = Param(model.Period, model.Scenario, model.Node, model.Operationalhour, default=0.0, mutable=True)
    model.sload = Param(model.Period, model.Scenario, model.Node, model.Operationalhour, default=0.0, mutable=True)
    model.genCapAvailStochRaw = Param(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, default=1., mutable=False, within=PercentFraction)
    model.genCapAvail = Param(model.GeneratorsOfNode, model.Operationalhour, model.Period, model.Scenario, default=0.0, mutable=True, within=PercentFraction)
    model.maxRegHydroGenRaw = Param(model.Period, model.Scenario, model.Node, model.HoursOfSeason, default=0.0, mutable=True)
    model.maxRegHydroGen = Param(model.Period, model.Scenario, model.Node, model.Season, default=0.0, mutable=True)
    return 


def load_operational_sets(model, data, scenarios):
    load_set_directly(data, model.Scenario, scenarios)
    return 

def load_operational_parameters(model, data, dataset_dir, emission_cap_flag, out_of_sample_flag, sample_file_path=None, scenario_data_path=None):
    input_parameters = {
    "Generator": [
        "genVariableOMCost",
        "CCSCostTSVariable",
        "genCO2TypeFactor",
        "genCapAvailTypeRaw",
        "genRampUpCap",
        "genEfficiency",
        "genFuelCost",
    ],
    "Transmission": [
        "lineEfficiency",
    ],
    "Storage": [
        "storageBleedEff",
        "storageChargeEff",
        "storageDischargeEff",
        "storOperationalInit",
    ],
    "Node": [
        "nodeLostLoadCost",
        "sloadAnnualDemand",
        "maxHydroNode",
    ],
    "General": [
        "seasScale",
    ],
    }
    if emission_cap_flag:
        input_parameters["General"].append("CO2cap")
    else:
        input_parameters["General"].append("CO2price")
    load_data_from_files(data, model, dataset_dir, inputs=input_parameters)

    return 


def load_stochastic_input(model, data, dataset_dir, out_of_sample_flag=False, sample_file_path=None):
    stochastic_variables = {
        "Stochastic": [
            "sloadRaw",
            "genCapAvailStochRaw",
            "maxRegHydroGenRaw",
        ]}
    input_dir = (dataset_dir if not out_of_sample_flag else sample_file_path)
    load_data_from_files(data, model, input_dir, inputs=stochastic_variables)
    return 


def prep_operational_parameters(model, num_scenarios=None) -> None:
    """Prepare operational parameters for the model. 

    """
    # if num_scenarios is None:
    #     num_scenarios = value(len(model.Scenario))
    def prepSceProbab_rule(model):
        #Build an equiprobable probability distribution for Scenario
        
        if num_scenarios is None:
            for sce in model.Scenario:
                model.sceProbab[sce] = value(1/len(model.Scenario))
        else:
            for sce in model.Scenario:
                model.sceProbab[sce] = value(1/num_scenarios)

    model.build_SceProbab = BuildAction(rule=prepSceProbab_rule)


    def prepOperationalCostGen_rule(model):
        #Build generator short term marginal costs

        for g in model.Generator:
            for i in model.PeriodActive:
                if ('CCS',g) in model.GeneratorsOfTechnology:
                    costperenergyunit=(3.6/model.genEfficiency[g,i])*(model.genFuelCost[g,i]+(1-model.CCSRemFrac)*model.genCO2TypeFactor[g]*model.CO2price[i])+ \
                    (3.6/model.genEfficiency[g,i])*(model.CCSRemFrac*model.genCO2TypeFactor[g]*model.CCSCostTSVariable[i])+ \
                    model.genVariableOMCost[g]
                else:
                    costperenergyunit=(3.6/model.genEfficiency[g,i])*(model.genFuelCost[g,i]+model.genCO2TypeFactor[g]*model.CO2price[i])+ \
                    model.genVariableOMCost[g]
                model.genMargCost[g,i]=costperenergyunit

    model.build_OperationalCostGen = BuildAction(rule=prepOperationalCostGen_rule)
    
    def prepOperationalDiscountrate_rule(model):
        #Build operational discount rate

        model.operationalDiscountrate = sum((1+model.discountrate)**(-j) for j in list(range(0,value(model.LeapYearsInvestment))))

    model.build_operationalDiscountrate = BuildAction(rule=prepOperationalDiscountrate_rule)     

    return 


def derive_stochastic_parameters(instance: ConcreteModel, node_unscaled_yearly_demand_ser=None) -> None:
    """Set values for stochastic parameters based on raw inputs.
    E.g. compute sload from sloadRaw."""
    def _set_maxRegHydroGen(instance):
        """Assign values to maxRegHydroGen from maxRegHydroGenRaw."""
        for n in instance.Node:
            for s in instance.Season:
                for i in instance.PeriodActive:
                    for w in instance.Scenario:
                        total = sum(
                            instance.maxRegHydroGenRaw[i, w, n, s, h]
                            for h in instance.Operationalhour
                            if (s, h) in instance.HoursOfSeason
                        )
                        instance.maxRegHydroGen[i, w, n, s] = total
    _set_maxRegHydroGen(instance)

    def _set_sload(instance, node_unscaled_yearly_demand_ser=None):
        for n in instance.Node:
            for i in instance.PeriodActive:
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
                        instance.sload[i, w, n, h] = instance.sloadRaw[i, w, n, h] * hourlyscale 

    
    _set_sload(instance, node_unscaled_yearly_demand_ser)

    def _set_genCapAvail(instance):
        """Assign generator availability based on type and stochastic raw availability."""
        for (n, g) in instance.GeneratorsOfNode:
            for h in instance.Operationalhour:
                for w in instance.Scenario:
                    for i in instance.PeriodActive:
                        instance.genCapAvail[n, g, h, i, w] = (
                            instance.genCapAvailTypeRaw[g] * instance.genCapAvailStochRaw[n, g, h, i, w]
                        )
    _set_genCapAvail(instance)


    return 


def define_operational_constraints(
        model: AbstractModel, 
        logger: logging.Logger,
        emission_cap_flag: bool, 
        include_hydro_node_limit_constraint_flag: bool
        ) -> None:
    # Define operational constraints for the model

    def shed_component_rule(model,i, w):
        """Defines load shedding cost"""
        return sum(model.operationalDiscountrate*model.seasScale[s]*model.sceProbab[w]*model.nodeLostLoadCost[n,i]*model.loadShed[n,h,i,w] for n in model.Node for (s,h) in model.HoursOfSeason)
    model.shedcomponent=Expression(model.PeriodActive,model.Scenario,rule=shed_component_rule)

    def operational_cost_rule(model,i, w):
        """Defines operational cost"""
        return model.shedcomponent[i,w] + sum(model.operationalDiscountrate*model.seasScale[s]*model.sceProbab[w]*model.genMargCost[g,i]*model.genOperational[n,g,h,i,w] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason)
    model.operationalcost=Expression(model.PeriodActive,model.Scenario,rule=operational_cost_rule)

    # note: this cannot be included in the Benders
    if include_hydro_node_limit_constraint_flag:
        def hydro_node_limit_rule(model, n, i):
            return sum(model.genOperational[n,g,h,i,w]*model.seasScale[s]*model.sceProbab[w] for g in model.HydroGenerator if (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason for w in model.Scenario) - model.maxHydroNode[n] <= 0   #
        model.hydro_node_limit = Constraint(model.Node, model.PeriodActive, rule=hydro_node_limit_rule)

    # scenario-dependent constraints:

    def FlowBalance_rule(model, n, h, i, w):
        return sum(model.genOperational[n,g,h,i,w] for g in model.Generator if (n,g) in model.GeneratorsOfNode) \
                    + sum((model.lineEfficiency[link,n]*model.transmissionOperational[link,n,h,i,w] - model.transmissionOperational[n,link,h,i,w]) for link in model.NodesLinked[n]) \
                    + sum((model.storageDischargeEff[b]*model.storDischarge[n,b,h,i,w]-model.storCharge[n,b,h,i,w]) for b in model.Storage if (n,b) in model.StoragesOfNode) \
                     - model.sload[i,w,n,h] + model.loadShed[n,h,i,w] \
                     == 0 
               
                     
    model.FlowBalance = Constraint(model.Node, model.Operationalhour, model.PeriodActive, model.Scenario, rule=FlowBalance_rule)

    def genMaxProd_rule(model, n, g, h, i, w):
            return model.genOperational[n,g,h,i,w] - model.genCapAvail[n, g, h, i, w]*model.genInstalledCap[n,g,i] <= 0
    model.maxGenProduction = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=genMaxProd_rule)

    #################################################################

    def ramping_rule(model, n, g, h, i, w):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return Constraint.Skip
        else:
            if g in model.ThermalGenerators:
                return model.genOperational[n,g,h,i,w]-model.genOperational[n,g,(h-1),i,w] - model.genRampUpCap[g]*model.genInstalledCap[n,g,i] <= 0   #
            else:
                return Constraint.Skip
    model.ramping = Constraint(model.GeneratorsOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=ramping_rule)


    #################################################################

    def storage_operational_cap_rule(model, n, b, h, i, w):
        return model.storOperational[n,b,h,i,w] - model.storENInstalledCap[n,b,i]  <= 0   #
    model.storage_operational_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_operational_cap_rule)

    #################################################################

    def storage_power_discharg_cap_rule(model, n, b, h, i, w):
        return model.storDischarge[n,b,h,i,w] - model.storageDiscToCharRatio[b]*model.storPWInstalledCap[n,b,i] <= 0   #
    model.storage_power_discharg_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_power_discharg_cap_rule)

    #################################################################

    def storage_power_charg_cap_rule(model, n, b, h, i, w):
        return model.storCharge[n,b,h,i,w] - model.storPWInstalledCap[n,b,i] <= 0   #
    model.storage_power_charg_cap = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_power_charg_cap_rule)

    #################################################################

    def hydro_gen_limit_rule(model, n, g, s, i, w):
        if g in model.RegHydroGenerator:
            return sum(model.genOperational[n,g,h,i,w] for h in model.Operationalhour if (s,h) in model.HoursOfSeason) - model.maxRegHydroGen[i,w,n,s] <= 0
        else:
            return Constraint.Skip  #
    model.hydro_gen_limit = Constraint(model.GeneratorsOfNode, model.Season, model.PeriodActive, model.Scenario, rule=hydro_gen_limit_rule)

    
    def storage_seasonal_net_zero_balance_rule(model, n, b, h, i, w):
        if h in model.FirstHoursOfRegSeason:
            return -model.storOperational[n,b,h+value(model.lengthRegSeason)-1,i,w] + model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] <= 0  #
        elif h in model.FirstHoursOfPeakSeason:
            return -model.storOperational[n,b,h+value(model.lengthPeakSeason)-1,i,w] + model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] <= 0  #
        else:
            return Constraint.Skip
    model.storage_seasonal_net_zero_balance = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_seasonal_net_zero_balance_rule)

    def storage_energy_balance_upper_rule(model, n, b, h, i, w):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return -model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] - model.storageChargeEff[b]*model.storCharge[n,b,h,i,w]+model.storDischarge[n,b,h,i,w]+model.storOperational[n,b,h,i,w] <= 0   #
        else: 
            return model.storageBleedEff[b]*model.storOperational[n,b,(h-1),i,w] + model.storageChargeEff[b]*model.storCharge[n,b,h,i,w]-model.storDischarge[n,b,h,i,w]-model.storOperational[n,b,h,i,w] == 0   #
    model.storage_energy_balance_upper = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_energy_balance_upper_rule)

    def storage_energy_balance_lower_rule(model, n, b, h, i, w):
        if h in model.FirstHoursOfRegSeason or h in model.FirstHoursOfPeakSeason:
            return -model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] - model.storageChargeEff[b]*model.storCharge[n,b,h,i,w]+model.storDischarge[n,b,h,i,w]+model.storOperational[n,b,h,i,w] >= 0   #
        else:
            return Constraint.Skip
    model.storage_energy_balance_lower = Constraint(model.StoragesOfNode, model.Operationalhour, model.PeriodActive, model.Scenario, rule=storage_energy_balance_lower_rule)

   
    #################################################################

    def transmission_cap_rule(model, n1, n2, h, i, w):
        if (n1,n2) in model.BidirectionalArc:
            return model.transmissionOperational[(n1,n2),h,i,w]  - model.transmissionInstalledCap[(n1,n2),i] <= 0
        elif (n2,n1) in model.BidirectionalArc:
            return model.transmissionOperational[(n1,n2),h,i,w]  - model.transmissionInstalledCap[(n2,n1),i] <= 0
    model.transmission_cap = Constraint(model.DirectionalLink, model.Operationalhour, model.PeriodActive, model.Scenario, rule=transmission_cap_rule)

    #################################################################

    if emission_cap_flag:
        def emission_cap_rule(model, i, w):
            return sum(model.seasScale[s]*model.genCO2TypeFactor[g]*(3.6/model.genEfficiency[g,i])*model.genOperational[n,g,h,i,w] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason)/1000000 \
                - model.CO2cap[i] <= 0   #
        model.emission_cap = Constraint(model.PeriodActive, model.Scenario, rule=emission_cap_rule)

    #################################################################
    
    return 
