"""Natural gas-specific parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_natural_gas_parameters(model):
    """Define parameters specific to the natural gas module.
    
    Args:
        model: Pyomo abstract model
        gas_stochasticity_flag: Whether to include gas stochasticity
    """
    
    # Storage parameters
    model.ng_storageCapacity = Param(model.NaturalGasNode, default=0, mutable=True)


    model.ng_storageInit = Param(default=0.5, mutable=True)
    model.ng_storageChargeEff = Param(default=1, mutable=True)
    model.ng_storageDischargeEff = Param(default=1, mutable=True)
    
    # Pipeline parameters
    model.ng_pipelineCapacity = Param(model.NaturalGasDirectionalLink, default=0, mutable=True)
    model.ng_pipelinePowerDemandPerTon = Param(default=0, mutable=True)
    
    # Terminal parameters
    model.ng_terminalCost = Param(model.NaturalGasTerminalsOfNode, model.Period, model.GasScenario, default=99999, mutable=True)
    model.ng_terminalCapacity = Param(model.NaturalGasTerminalsOfNode, model.Period, default=0, mutable=True)
    
    # Reserves
    model.ng_reserves = Param(model.NaturalGasNode, default=0, mutable=True)



def load_natural_gas_parameter_data(data, tab_file_path, model, gas_stochasticity_flag=False):
    """Load natural gas parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
        gas_stochasticity_flag: Whether to load stochastic gas price data
    """
    data.load(filename=tab_file_path + '/' + 'NaturalGas_StorageCapacity.tab', param=model.ng_storageCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'NaturalGas_PipelineCapacity.tab', param=model.ng_pipelineCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'NaturalGas_PipelineElectricityUse.tab', param=model.ng_pipelinePowerDemandPerTon, format='table')
    
    # Terminal cost - depends on stochasticity flag
    if not gas_stochasticity_flag:
        data.load(filename=tab_file_path + '/' + 'NaturalGas_TerminalCost.tab', param=model.ng_terminalCost, format='table')
    else:
        data.load(filename=tab_file_path + '/' + 'NaturalGas_TerminalCost_stochastic.tab', param=model.ng_terminalCost, format='table')
    
    data.load(filename=tab_file_path + '/' + 'NaturalGas_TerminalCapacity.tab', param=model.ng_terminalCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'NaturalGas_Reserves.tab', param=model.ng_reserves, format='table')
