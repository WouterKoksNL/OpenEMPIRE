from pyomo.environ import Param


def define_heat_operational_parameters(model):
    """Define parameters specific to heat module operational model.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Converter operational parameters
    model.ConverterEff = Param(model.Converter, initialize=1.0, mutable=True)
    
    # Generator heat operational parameters
    model.genVariableOMCostHeat = Param(model.Generator, default=0.0)
    model.genFuelCostHeat = Param(model.Generator, model.Period, default=0.0)
    model.genCO2TypeFactorHeat = Param(model.Generator, default=0.0)
    model.genEfficiencyHeat = Param(model.Generator, model.Period, default=1.0)
    model.genCHPEfficiencyRaw = Param(model.GeneratorEL, model.Period, default=0.0)
    model.genCHPEfficiency = Param(model.GeneratorEL, model.Period, default=1.0, mutable=True)
    model.genRampUpCapHeat = Param(model.RampingGenerators, default=0.0)
    model.genCapAvailTypeRawHeat = Param(model.Generator, default=1.0, mutable=True)
    
    # Storage heat operational parameters
    model.storageLifetimeHeat = Param(model.Storage, default=0.0)
    model.storageChargeEffHeat = Param(model.Storage, default=1.0)
    model.storageDischargeEffHeat = Param(model.Storage, default=1.0)
    model.storageBleedEffHeat = Param(model.Storage, default=1.0)
    model.storPWInitCapHeat = Param(model.StoragesOfNode, model.Period, default=0.0)
    model.storENInitCapHeat = Param(model.StoragesOfNode, model.Period, default=0.0)
    model.storOperationalInitHeat = Param(model.Storage, default=0.0, mutable=True)
    
    # Stochastic heat parameters
    model.sloadRawTR = Param(model.Node, model.Operationalhour, model.Scenario, model.Period, default=0.0, mutable=True)
    model.sloadTR = Param(model.Node, model.Operationalhour, model.Period, model.Scenario, default=0.0, mutable=True)
    model.convAvail = Param(model.ConverterOfNode, model.Operationalhour, model.Scenario, model.Period, default=1.0, mutable=True)
    
    # Node heat parameters
    model.nodeLostLoadCostTR = Param(model.Node, model.Period, default=22000.0)
    model.sloadAnnualDemandTR = Param(model.Node, model.Period, default=0.0, mutable=True)
    model.ElectricHeatShare = Param(model.Node, default=0.0, mutable=True)



def load_heat_operational_parameter_data(data, tab_file_path, scenario_path, model):
    """Load heat module operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing static tab files
        scenario_path: Path to directory containing scenario-specific data
        model: Pyomo model with parameters already defined
    """
    # Generator heat operational parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_VariableOMCosts.tab', param=model.genVariableOMCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_FuelCosts.tab', param=model.genFuelCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_Efficiency.tab', param=model.genEfficiencyHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_CO2Content.tab', param=model.genCO2TypeFactorHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_RampRate.tab', param=model.genRampUpCapHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_GeneratorTypeAvailability.tab', param=model.genCapAvailTypeRawHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_CHPEfficiency.tab', param=model.genCHPEfficiencyRaw, format="table")
    
    # Storage heat operational parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_StorageBleedEfficiency.tab', param=model.storageBleedEffHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_StorageChargeEff.tab', param=model.storageChargeEffHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_StorageDischargeEff.tab', param=model.storageDischargeEffHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_StorageInitialEnergyLevel.tab', param=model.storOperationalInitHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_Lifetime.tab', param=model.storageLifetimeHeat, format="table")
    
    # Stochastic heat parameters
    data.load(filename=scenario_path + "/" + 'HeatModule/HeatModuleStochastic_HeatLoadRaw.tab', param=model.sloadRawTR, format="table")
    data.load(filename=scenario_path + "/" + 'HeatModule/HeatModuleStochastic_ConverterAvail.tab', param=model.convAvail, format="table")
    
    # Node heat parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleNode_HeatAnnualDemand.tab', param=model.sloadAnnualDemandTR, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleNode_NodeLostLoadCost.tab', param=model.nodeLostLoadCostTR, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleNode_ElectricHeatShare.tab', param=model.ElectricHeatShare, format="table")
