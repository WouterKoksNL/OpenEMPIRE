"""Operational parameters for the EMPIRE model (excluding module-specific parameters)."""
import pandas as pd

from pyomo.environ import Param
from empire.core.loading_utils import load_parameters, load_parameter

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
    model.sloadRaw = Param(model.Period, model.Scenario, model.Node, model.Operationalhour, default=0.0, mutable=True)
    model.sloadAnnualDemand = Param(model.Node, model.Period, default=0.0, mutable=True)
    model.sload = Param(model.Node, model.Operationalhour, model.Period, model.Scenario, default=0.0, mutable=True)
    model.genCapAvailStochRaw = Param(model.Period, model.Scenario, model.GeneratorsOfNode, model.Operationalhour, default=1.0, mutable=True)
    model.genCapAvail = Param(model.GeneratorsOfNode, model.Operationalhour, model.Scenario, model.Period, default=1.0, mutable=True)
    model.maxRegHydroGenRaw = Param(model.Period, model.Scenario, model.Node, model.HoursOfSeason, default=1.0, mutable=True)
    model.maxRegHydroGen = Param(model.Period, model.Scenario, model.Node, model.Season, default=1.0, mutable=True)
    model.maxHydroNode = Param(model.Node, default=0.0, mutable=True)
    
    # CVaR module parameters (conditional)
    if use_cvar:
        model.cvar_percentile = Param(initialize=cvar_percentile)  # alpha
        model.cvar_weight = Param(initialize=cvar_weight)  # lambda




def load_base_operational_parameter_data(data, dataset_dir, model, filtering_dict=None):
    """Load operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """

    input_parameters = {
        "Generator": [
            "genVariableOMCost",
            "genFuelCost",
            "genEfficiency",
            "genCO2TypeFactor",
            "genRampUpCap",
            "genCapAvailTypeRaw",
        ],
        "Transmission": [
            "lineEfficiency",
        ],
        "Storage": [
            "storageBleedEff",
            "storageChargeEff",
            "storageDischargeEff",
            "storagePowToEnergy",
            "storOperationalInit",
        ],
    }
    for component, param_list in input_parameters.items():
        load_parameters(
            data,
            full_path=dataset_dir / component,
            param_name_list=param_list,
            model=model,
            filtering_dict=filtering_dict
        )


def load_base_stochastic_parameter_data(
        data, 
        stochastic_input_dir,
        dataset_dir, 
        model,
        filtering_dict,
        ) -> None:
    
    generators_of_node_df = pd.read_csv(dataset_dir / "Sets" / "GeneratorsOfNode.csv")
    load_parameter(
            data,
            full_path=stochastic_input_dir,
            param_name="genCapAvailStochRaw",
            param=getattr(model, "genCapAvailStochRaw"),
            filtering_dict={("Node", "Generator"): generators_of_node_df, **filtering_dict},
    )
    stochastic_variables = [
            "sloadRaw",
            "maxRegHydroGenRaw",
        ]
    load_parameters(
            data,
            full_path=stochastic_input_dir,
            param_name_list=stochastic_variables,
            model=model,
            filtering_dict=filtering_dict
        )
    

    return 