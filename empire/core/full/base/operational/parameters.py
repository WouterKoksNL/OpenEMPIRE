"""Operational parameters for the EMPIRE model (excluding module-specific parameters)."""
from pyomo.environ import Param

def define_base_operational_parameters(model, use_cvar=False, cvar_percentile=None, cvar_weight=None):
    """Define parameters specific to operational constraints.
    
    These are general operational parameters. Module-specific parameters (hydrogen, 
    industry, heat, natural gas) are defined in their respective modules.
    
    Args:
        model: Pyomo abstract model
        use_cvar: Whether to use CVaR
        cvar_percentile: CVaR percentile (alpha)
        cvar_weight: CVaR weight (lambda)
    """
    
    # Generator operational parameters
    model.genVariableOMCost = Param(model.Generator, default=0.0, mutable=True)
    model.genFuelCost = Param(model.Generator, model.Period, mutable=True)
    model.genMargCost = Param(model.Generator, model.Period, default=600, mutable=True)
    model.genCO2TypeFactor = Param(model.Generator, default=0.0, mutable=True)
    model.genCO2Captured = Param(model.Generator, default=0.0, mutable=True)
    model.genEfficiency = Param(model.Generator, model.Period, default=1.0, mutable=True)
    model.genRampUpCap = Param(model.RampingGenerators, default=0.0, mutable=True)
    model.genCapAvailTypeRaw = Param(model.Generator, default=1.0, mutable=True)
    
    # Storage operational parameters
    model.storageChargeEff = Param(model.Storage, default=1.0, mutable=True)
    model.storageDischargeEff = Param(model.Storage, default=1.0, mutable=True)
    model.storageBleedEff = Param(model.Storage, default=1.0, mutable=True)
    model.storageDiscToCharRatio = Param(model.Storage, default=1.0, mutable=True)
    model.storagePowToEnergy = Param(model.DependentStorage, default=1.0, mutable=True)
    model.storOperationalInit = Param(model.Storage, default=0.0, mutable=True)
    
    # Transmission operational parameters
    model.lineEfficiency = Param(model.DirectionalLink, default=0.97, mutable=True)
    
    # Stochastic input
    model.sloadRaw = Param(model.Node, model.Operationalhour, model.Scenario, model.Period, default=0.0, mutable=True)
    model.sloadAnnualDemand = Param(model.Node, model.Period, default=0.0, mutable=True)
    model.sload = Param(model.Node, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, default=0.0, mutable=True)
    model.genCapAvailStochRaw = Param(model.GeneratorsOfNode, model.Operationalhour, model.Scenario, model.Period, default=0.0, mutable=True)
    model.genCapAvail = Param(model.GeneratorsOfNode, model.Operationalhour, model.Scenario, model.Period, default=0.0, mutable=True)
    model.maxRegHydroGenRaw = Param(model.Node, model.Period, model.HoursOfSeason, model.Scenario, default=1.0, mutable=True)
    model.maxRegHydroGen = Param(model.Node, model.Period, model.Season, model.Scenario, default=1.0, mutable=True)
    model.maxHydroNode = Param(model.Node, default=0.0, mutable=True)
    
    # CVaR module parameters (conditional)
    if use_cvar:
        model.cvar_percentile = Param(initialize=cvar_percentile)  # alpha
        model.cvar_weight = Param(initialize=cvar_weight)  # lambda




def load_base_operational_parameter_data(data, tab_file_path, model):
    """Load operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # Generator operational parameters
    data.load(filename=tab_file_path + "/" + 'Generator_VariableOMCosts.tab', param=model.genVariableOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_FuelCosts.tab', param=model.genFuelCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_Efficiency.tab', param=model.genEfficiency, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_CO2Content.tab', param=model.genCO2TypeFactor, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_CO2Captured.tab', param=model.genCO2Captured, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_RampRate.tab', param=model.genRampUpCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_GeneratorTypeAvailability.tab', param=model.genCapAvailTypeRaw, format="table")
    
    # Transmission operational parameters
    data.load(filename=tab_file_path + "/" + 'Transmission_lineEfficiency.tab', param=model.lineEfficiency, format="table")
    
    # Storage operational parameters
    data.load(filename=tab_file_path + "/" + 'Storage_StorageBleedEfficiency.tab', param=model.storageBleedEff, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_StorageChargeEff.tab', param=model.storageChargeEff, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_StorageDischargeEff.tab', param=model.storageDischargeEff, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_StoragePowToEnergy.tab', param=model.storagePowToEnergy, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_StorageInitialEnergyLevel.tab', param=model.storOperationalInit, format="table")


def load_base_stochastic_parameter_data(data, scenariopath, sample_file_path, model, OUT_OF_SAMPLE):
    """Load stochastic operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        scenariopath: Path to directory containing scenario tab files
        sample_file_path: Path to directory containing out-of-sample tab files
        model: Pyomo model with parameters already defined
        OUT_OF_SAMPLE: Boolean indicating whether to load out-of-sample data
    """
    # Load stochastic operational data (load, availability, hydro)
    if OUT_OF_SAMPLE:
        if sample_file_path:
            # Load operational input data EMPIRE has not seen when optimizing (in-sample)
            data.load(filename=str(sample_file_path + "/" + 'Stochastic_HydroGenMaxSeasonalProduction.tab'), param=model.maxRegHydroGenRaw, format="table")
            data.load(filename=str(sample_file_path + "/" + 'Stochastic_StochasticAvailability.tab'), param=model.genCapAvailStochRaw, format="table")
            data.load(filename=str(sample_file_path + "/" + 'Stochastic_ElectricLoadRaw.tab'), param=model.sloadRaw, format="table")
        else:
            raise ValueError("'OUT_OF_SAMPLE = True' needs to be run with existing 'sample_file_path'")
    else:
        data.load(filename=scenariopath + "/" + 'Stochastic_HydroGenMaxSeasonalProduction.tab', param=model.maxRegHydroGenRaw, format="table")
        data.load(filename=scenariopath + "/" + 'Stochastic_StochasticAvailability.tab', param=model.genCapAvailStochRaw, format="table")
        data.load(filename=scenariopath + "/" + 'Stochastic_ElectricLoadRaw.tab', param=model.sloadRaw, format="table")
    return 