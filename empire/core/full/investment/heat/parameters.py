"""Heat module investment-specific parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_heat_investment_parameters(model, WACC):
    """Define parameters specific to heat module investments.
    
    Args:
        model: Pyomo abstract model
        WACC: Weighted average cost of capital
    """
    
    # Converter investment parameters
    model.ConverterCapitalCost = Param(model.Converter, model.Period, default=0)
    model.ConverterFixedOMCost = Param(model.Converter, model.Period, default=0)
    model.ConverterInvCost = Param(model.Converter, model.Period, mutable=True)
    model.ConverterLifetime = Param(model.Converter, default=0)
    model.ConverterInitCap = Param(model.ConverterOfNode, model.Period, default=0)
    model.ConverterMaxBuiltCap = Param(model.ConverterOfNode, model.Period, default=50000)
    model.ConverterMaxInstalledCapRaw = Param(model.ConverterOfNode, default=200000)
    model.ConverterMaxInstalledCap = Param(model.ConverterOfNode, model.Period, default=0, mutable=True)
    
    # Generator heat investment parameters
    model.genCapitalCostHeat = Param(model.Generator, model.Period, default=0)
    model.genFixedOMCostHeat = Param(model.Generator, model.Period, default=0)
    model.genLifetimeHeat = Param(model.Generator, default=0.0)
    model.genRefInitCapHeat = Param(model.GeneratorsOfNode, default=0.0)
    model.genScaleInitCapHeat = Param(model.Generator, model.Period, default=0.0)
    model.genInitCapHeat = Param(model.GeneratorsOfNode, model.Period, default=0.0, mutable=True)
    model.genMaxBuiltCapHeat = Param(model.Node, model.Technology, model.Period, default=500000.0, mutable=True)
    model.genMaxInstalledCapRawHeat = Param(model.Node, model.Technology, default=0.0, mutable=True)
    
    # Storage heat investment parameters
    model.storPWCapitalCostHeat = Param(model.Storage, model.Period, default=0)
    model.storENCapitalCostHeat = Param(model.Storage, model.Period, default=0)
    model.storPWFixedOMCostHeat = Param(model.Storage, model.Period, default=0)
    model.storENFixedOMCostHeat = Param(model.Storage, model.Period, default=0)
    model.storPWMaxBuiltCapHeat = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storENMaxBuiltCapHeat = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storPWMaxInstalledCapRawHeat = Param(model.StoragesOfNode, default=2000000.0, mutable=True)
    model.storENMaxInstalledCapRawHeat = Param(model.StoragesOfNode, default=2000000.0, mutable=True)



def load_heat_investment_parameter_data(data, tab_file_path, model):
    """Load heat module investment parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing static tab files
        model: Pyomo model with parameters already defined
    """
    # Converter investment parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_CapitalCosts.tab', param=model.ConverterCapitalCost, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_FixedOMCosts.tab', param=model.ConverterFixedOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_InitialCapacity.tab', param=model.ConverterInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_MaxBuildCapacity.tab', param=model.ConverterMaxBuiltCap, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_MaxInstallCapacity.tab', param=model.ConverterMaxInstalledCapRaw, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleConverter_Lifetime.tab', param=model.ConverterLifetime, format="table")
    
    # Generator heat investment parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_CapitalCosts.tab', param=model.genCapitalCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_FixedOMCosts.tab', param=model.genFixedOMCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_RefInitialCap.tab', param=model.genRefInitCapHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_ScaleFactorInitialCap.tab', param=model.genScaleInitCapHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_MaxInstalledCapacity.tab', param=model.genMaxInstalledCapRawHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleGenerator_Lifetime.tab', param=model.genLifetimeHeat, format="table")
    
    # Storage heat investment parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_EnergyCapitalCost.tab', param=model.storENCapitalCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_EnergyFixedOMCost.tab', param=model.storENFixedOMCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_EnergyInitialCapacity.tab', param=model.storENInitCapHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_PowerCapitalCost.tab', param=model.storPWCapitalCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_PowerFixedOMCost.tab', param=model.storPWFixedOMCostHeat, format="table")
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_InitialPowerCapacity.tab', param=model.storPWInitCapHeat, format="table")
