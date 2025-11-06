"""Industry investment-specific parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_industry_investment_parameters(model):
    """Define parameters specific to industry module investments.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Steel industry investment parameters
    model.steelPlantLifetime = Param(model.SteelPlants, default=25, mutable=False)
    model.steel_initialCapacity = Param(model.SteelProducers, model.SteelPlants, default=0, mutable=True)
    model.steel_scaleFactorInitialCap = Param(model.SteelPlants, model.Period, default=0, mutable=True)
    model.steel_plantCapitalCost = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_plantInvCost = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    model.steel_plantFixedOM = Param(model.SteelPlants, model.Period, default=99999, mutable=True)
    
    # Cement industry investment parameters
    model.cementPlantLifetime = Param(model.CementPlants, default=25, mutable=False)
    model.cement_initialCapacity = Param(model.CementProducers, model.CementPlants, default=0, mutable=True)
    model.cement_scaleFactorInitialCap = Param(model.CementPlants, model.Period, default=0, mutable=True)
    model.cement_plantCapitalCost = Param(model.CementPlants, model.Period, default=99999, mutable=True)
    model.cement_plantInvCost = Param(model.CementPlants, model.Period, default=99999, mutable=True)
    model.cement_plantFixedOM = Param(model.CementPlants, model.Period, default=99999, mutable=True)
    
    # Ammonia industry investment parameters
    model.ammoniaPlantLifetime = Param(model.AmmoniaPlants, default=25, mutable=False)
    model.ammonia_initialCapacity = Param(model.AmmoniaProducers, model.AmmoniaPlants, default=0, mutable=True)
    model.ammonia_scaleFactorInitialCap = Param(model.AmmoniaPlants, model.Period, default=0, mutable=True)
    model.ammonia_plantCapitalCost = Param(model.AmmoniaPlants, model.Period, default=99999, mutable=True)
    model.ammonia_plantInvCost = Param(model.AmmoniaPlants, model.Period, default=99999, mutable=True)
    model.ammonia_plantFixedOM = Param(model.AmmoniaPlants, model.Period, default=99999, mutable=True)


def load_industry_investment_parameter_data(data, tab_file_path, model):
    """Load industry investment parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # Steel industry investment parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_InitialCapacity.tab', param=model.steel_initialCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_ScaleFactorInitialCap.tab', param=model.steel_scaleFactorInitialCap, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_InvCost.tab', param=model.steel_plantCapitalCost, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_FixedOM.tab', param=model.steel_plantFixedOM, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Steel_PlantLifetime.tab', param=model.steelPlantLifetime, format='table')
    
    # Cement industry investment parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_InitialCapacity.tab', param=model.cement_initialCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_ScaleFactorInitialCap.tab', param=model.cement_scaleFactorInitialCap, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_InvCost.tab', param=model.cement_plantCapitalCost, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_FixedOM.tab', param=model.cement_plantFixedOM, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Cement_PlantLifetime.tab', param=model.cementPlantLifetime, format='table')
    
    # Ammonia industry investment parameters
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_InitialCapacity.tab', param=model.ammonia_initialCapacity, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_ScaleFactorInitialCap.tab', param=model.ammonia_scaleFactorInitialCap, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_InvCost.tab', param=model.ammonia_plantCapitalCost, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_FixedOM.tab', param=model.ammonia_plantFixedOM, format='table')
    data.load(filename=tab_file_path + '/' + 'Industry_Ammonia_PlantLifetime.tab', param=model.ammoniaPlantLifetime, format='table')
