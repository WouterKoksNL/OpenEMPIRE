"""Natural gas-specific parameters for the EMPIRE model."""
from pyomo.environ import Param
from empire.core.loading_utils import load_parameters

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

        # Available resources
    model.availableBioEnergy = Param(model.Period, default=0, mutable=True)



def load_natural_gas_parameter_data(data, dataset_dir, model, gas_stochasticity_flag=False, filtering_dict=None):
    """Load natural gas parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        dataset_dir: Path to dataset input directory
        model: Pyomo model with parameters already defined
        gas_stochasticity_flag: Whether to load stochastic gas price data
    """
    param_list = [
        'ng_storageCapacity',
        'ng_pipelineCapacity',
        'ng_pipelinePowerDemandPerTon',
        'ng_terminalCapacity',
        'ng_reserves',
        'availableBioEnergy',
    ]
    if gas_stochasticity_flag:
        param_list.append('ng_terminalCostStochastic')
    else:
        param_list.append('ng_terminalCost')
    

    load_parameters(
        data, 
        dataset_dir / 'NaturalGas',
        param_name_list=param_list,
        model=model,
        filtering_dict=filtering_dict
        )

