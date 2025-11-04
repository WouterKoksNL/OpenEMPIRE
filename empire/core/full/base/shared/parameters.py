"""Shared parameters used across investment and operational modules."""
from pyomo.environ import Param


def define_base_shared_parameters(model, discountrate, WACC, lengthRegSeason, lengthPeakSeason, EMISSION_CAP=False):
    """Define parameters that are shared across investment and operational modules.
    
    Args:
        model: Pyomo abstract model
        discountrate: Discount rate value
        WACC: Weighted average cost of capital
        lengthRegSeason: Length of regular season
        lengthPeakSeason: Length of peak season
        EMISSION_CAP: Whether emission cap is enabled
    """
    
    # Scaling and temporal parameters
    model.discountrate = Param(initialize=discountrate)
    model.WACC = Param(initialize=WACC)
    model.operationalDiscountrate = Param(mutable=True)
    model.sceProbab = Param(model.Scenario, mutable=True)
    model.GasSceProbab = Param(model.GasScenario, mutable=True)
    model.seasScale = Param(model.Season, initialize=1.0, mutable=True)
    model.lengthRegSeason = Param(initialize=lengthRegSeason)
    model.lengthPeakSeason = Param(initialize=lengthPeakSeason)
    
    # General cost parameters  
    model.nodeLostLoadCost = Param(model.Node, model.Period, default=22000.0)
    model.CO2price = Param(model.Period, default=0.0, mutable=True)
    
    # Available resources
    model.availableBioEnergy = Param(model.Period, default=0, mutable=True)
    
    # Emission cap (conditional)
    if EMISSION_CAP:
        model.CO2cap = Param(model.Period, default=5000.0, mutable=True)
    
    # Coordinates for map visualization
    model.Latitude = Param(model.Node, default=0.0, mutable=True)
    model.Longitude = Param(model.Node, default=0.0, mutable=True)



def load_base_shared_parameter_data(data, tab_file_path, model):
    """Load shared parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing static tab files
        scenario_path: Path to directory containing scenario-specific data
        model: Pyomo model with parameters already defined
    """
    # Load CO2 pricing and caps
    if hasattr(model, 'CO2cap'):
        data.load(filename=tab_file_path + "/" + 'General_CO2Cap.tab', param=model.CO2cap, format="table")
    else:
        data.load(filename=tab_file_path + "/" + 'General_CO2Price.tab', param=model.CO2price, format="table")
    
    # Load available bio energy
    data.load(filename=tab_file_path + "/" + 'General_AvailableBioEnergy.tab', param=model.availableBioEnergy, format="table")
    
    # Load node-related parameters
    data.load(filename=tab_file_path + "/" + 'Node_NodeLostLoadCost.tab', param=model.nodeLostLoadCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Node_ElectricAnnualDemand.tab', param=model.sloadAnnualDemand, format="table")
    data.load(filename=tab_file_path + "/" + 'Node_HydroGenMaxAnnualProduction.tab', param=model.maxHydroNode, format="table")
    data.load(filename=tab_file_path + "/" + 'Node_Latitude.tab', param=model.Latitude, format="table")
    data.load(filename=tab_file_path + "/" + 'Node_Longitude.tab', param=model.Longitude, format="table")
