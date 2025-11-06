"""Shared parameters used across investment and operational modules."""
from pyomo.environ import Param
from empire.core.loading_utils import load_parameters
from empire.core.config import EmpireConfiguration

def define_base_shared_parameters(model, empire_config: EmpireConfiguration):
    """Define parameters that are shared across investment and operational modules.
    
    Args:
        model: Pyomo abstract model
        empire_config: Empire configuration object
            - discount_rate [float]
            - WACC [float]
            - length_reg_season [int]
            - length_peak_season [int]
        EMISSION_CAP: Whether emission cap is enabled
    """
    
    # Scaling and temporal parameters
    model.discount_rate = Param(initialize=empire_config.discount_rate)
    model.WACC = Param(initialize=empire_config.wacc)
    model.operationalDiscountrate = Param(mutable=True)
    model.sceProbab = Param(model.Scenario, mutable=True)
    model.GasSceProbab = Param(model.GasScenario, mutable=True)
    model.seasScale = Param(model.Season, initialize=1.0, mutable=True)
    model.length_reg_season = Param(initialize=empire_config.length_regular_season)
    model.length_peak_season = Param(initialize=empire_config.length_peak_season)

    # General cost parameters
    model.nodeLostLoadCost = Param(model.Node, model.Period, default=22000.0)
    model.CO2price = Param(model.Period, default=0.0, mutable=True)
    
    # Available resources
    model.availableBioEnergy = Param(model.Period, default=0, mutable=True)
    
    # Emission cap (conditional)
    if empire_config.emission_cap_flag:
        model.CO2cap = Param(model.Period, default=5000.0, mutable=True)
    
    # Coordinates for map visualization
    model.Latitude = Param(model.Node, default=0.0, mutable=True)
    model.Longitude = Param(model.Node, default=0.0, mutable=True)

    model.leap_years_investment = Param(initialize=empire_config.leap_years_investment)
    model.repurposeEnergyFlowFactor = Param(initialize=empire_config.repurposeEnergyFlowFactor)
    model.gas_h2_repurpose_cost_factor = Param(initialize=empire_config.gas_h2_repurpose_cost_factor)


def load_base_shared_parameter_data(data, dataset_dir, model, period=None, scenario=None):
    """Load shared parameter data. Optionally filter by period and scenario (for Benders).
    """
    params = {
        "General": ["availableBioEnergy"],
        "Node": [
            "nodeLostLoadCost",
            "sloadAnnualDemand",
            "maxHydroNode",
            "Latitude",
            "Longitude",
        ]
    }

    if hasattr(model, 'CO2cap'):
        params["General"].append("CO2cap")
    else:
        params["General"].append("CO2price")

    for component, param_list in params.items():
        load_parameters(
            data,
            full_path=dataset_dir / component,
            param_name_list=param_list,
            model=model,
            filtering_dict={"Period": period, "Scenario": scenario}
        )
