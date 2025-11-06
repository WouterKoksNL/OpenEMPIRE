"""Industry operational-specific parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_industry_operational_parameters(model):
    """Define parameters specific to industry module operational model.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Steel industry operational parameters
    model.steel_varOpex = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_coalConsumption = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_hydrogenConsumption = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_bioConsumption = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_oilConsumption = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_electricityConsumption = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_CO2Emissions = Param(model.SteelPlants, default=99999, mutable=True)
    model.steel_CO2Captured = Param(model.SteelPlants, default=0, mutable=True)
    model.steel_yearlyProduction = Param(model.SteelProducers, model.Period, default=0, mutable=True)
    
    # Cement industry operational parameters
    model.cement_fuelConsumption = Param(model.CementPlants, model.Period, default=99999, mutable=True)
    model.cement_co2CaptureRate = Param(model.CementPlants, default=0, mutable=True)
    model.cement_electricityConsumption = Param(model.CementPlants, model.Period, default=99999, mutable=True)
    model.cement_yearlyProduction = Param(model.CementProducers, default=0, mutable=True)
    
    # Ammonia industry operational parameters
    model.ammonia_fuelConsumption = Param(model.AmmoniaPlants, default=99999, mutable=True)
    model.ammonia_electricityConsumption = Param(model.AmmoniaPlants, default=99999, mutable=True)
    model.ammonia_yearlyProduction = Param(model.AmmoniaProducers, model.Period, default=0, mutable=True)
    
    # Refinery operational parameters
    model.refinery_hydrogenConsumption = Param(default=99999, mutable=True)
    model.refinery_heatConsumption = Param(default=99999, mutable=True)
    model.refinery_yearlyProduction = Param(model.OilProducers, model.Period, default=0, mutable=True)
    model.industryShedCost = Param(default=10000, mutable=True)

    model.steel_opex = Param(model.Period, model.Scenario, model.GasScenario, mutable=True)
    model.cement_opex = Param(model.Period, model.Scenario, model.GasScenario, mutable=True)
    model.ammonia_opex = Param(model.Period, model.Scenario, model.GasScenario, mutable=True)
    model.oil_opex = Param(model.Period, model.Scenario, model.GasScenario, mutable=True)
    
def load_industry_operational_parameter_data(data, tab_file_path, model):
    """Load industry operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # Steel industry operational parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_VarOpex.tab', param=model.steel_varOpex, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_CoalConsumption.tab', param=model.steel_coalConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_HydrogenConsumption.tab', param=model.steel_hydrogenConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_BioConsumption.tab', param=model.steel_bioConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_OilConsumption.tab', param=model.steel_oilConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_ElConsumption.tab', param=model.steel_electricityConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_CO2Emissions.tab', param=model.steel_CO2Emissions, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_CO2Captured.tab', param=model.steel_CO2Captured, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_YearlyProduction.tab', param=model.steel_yearlyProduction, format='table')
    
    # Cement industry operational parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_FuelConsumption.tab', param=model.cement_fuelConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_CO2CaptureRate.tab', param=model.cement_co2CaptureRate, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_ElConsumption.tab', param=model.cement_electricityConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_YearlyProduction.tab', param=model.cement_yearlyProduction, format='table')
    
    # Ammonia industry operational parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_FeedstockConsumption.tab', param=model.ammonia_fuelConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_ElConsumption.tab', param=model.ammonia_electricityConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_YearlyProduction.tab', param=model.ammonia_yearlyProduction, format='table')
    
    # Refinery operational parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Refinery_HydrogenConsumption.tab', param=model.refinery_hydrogenConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Refinery_HeatConsumption.tab', param=model.refinery_heatConsumption, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Refinery_YearlyProduction.tab', param=model.refinery_yearlyProduction, format='table')
