from pyomo.environ import Param, DataPortal

def define_hydrogen_investment_parameters(model):

    
    # Electrolyzer parameters
    model.elyzerPlantCapitalCost = Param(model.Period, default=99999, mutable=True)
    model.elyzerStackCapitalCost = Param(model.Period, default=99999, mutable=True)
    model.elyzerFixedOMCost = Param(model.Period, default=99999, mutable=True)
    model.elyzerLifetime = Param(default=20, mutable=True)
    model.elyzerInvCost = Param(model.Period, default=99999, mutable=True)
    
    # Reformer parameters
    model.ReformerPlantsCapitalCost = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerPlantFixedOMCost = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerPlantInvCost = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerPlantLifetime = Param(model.ReformerPlants, default=25, mutable=True)

    
    # Pipeline parameters
    model.repurposedPipelineInvCost = Param(model.RepurposeDirectionalLinks, model.Period, default=999999, mutable=True)
    model.hydrogenPipelineLifetime = Param(default=40)
    model.hydrogenPipelineCapCost = Param(model.Period, default=99999, mutable=True)
    model.hydrogenPipelineOMCost = Param(model.Period, default=99999, mutable=True)
    model.hydrogenPipelineInvCost = Param(model.HydrogenBidirectionPipelines, model.Period, default=999999, mutable=True)
    
    # H2 terminal parameters
    model.H2TerminalCapitalCost = Param(model.H2TerminalNodes, model.H2Terminals, model.Period, default=99999, mutable=True)
    model.H2TerminalFixedOM = Param(model.H2TerminalNodes, model.H2Terminals, model.Period, default=99999, mutable=True)
    model.H2TerminalLifetime = Param(model.H2Terminals, default=1, mutable=True)
    model.H2TerminalInvCost = Param(model.H2TerminalNodes, model.H2Terminals, model.Period, default=99999, mutable=True)

    # Storage parameters
    model.hydrogenMaxStorageCapacity = Param(model.HydrogenProdNode, model.H2Storages, default=0, mutable=True)
    model.hydrogenStorageCapitalCost = Param(model.H2Storages, model.Period, default=99999999, mutable=True)
    model.hydrogenStorageFixedOMCost = Param(model.H2Storages, model.Period, default=99999999, mutable=True)
    model.hydrogenStorageInvCost = Param(model.H2Storages, model.Period, default=99999999, mutable=True)
    model.hydrogenStorageLifetime = Param(model.H2Storages, default=30)
    

    # CO2 storage parameters
    model.CO2StorageSiteCapitalCost = Param(model.CO2SequestrationNodes, default=999999999, mutable=True)
    model.CO2StorageSiteInvCost = Param(model.CO2SequestrationNodes, model.Period, default=999999999, mutable=True)
    model.StorageSiteFixedOMCost = Param(model.CO2SequestrationNodes, default=999999999, mutable=True)
    model.CO2PipelineLifetime = Param(default=50, mutable=True)
    model.CO2PipelineCapCost = Param(default=99999, mutable=True)
    model.CO2PipelineOMCost = Param(default=99999, mutable=True)
    model.CO2PipelineInvCost = Param(model.CO2BidirectionalPipelines, model.Period, default=99999, mutable=True)
    model.maxSequestrationCapacity = Param(model.CO2SequestrationNodes, default=0, mutable=True)
    model.CO2StorageMaxHourlyCapacity = Param(model.CO2SequestrationNodes, model.Period, default=0, mutable=True)
    

def load_hydrogen_investment_parameter_data(data: DataPortal, tab_file_path, model):
    """Load hydrogen investment parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # H2 Terminal parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_H2TerminalCapitalCost.tab', format="table", param=model.H2TerminalCapitalCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_H2TerminalFixedOM.tab', format="table", param=model.H2TerminalFixedOM)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_H2TerminalLifetime.tab', format="table", param=model.H2TerminalLifetime)

    # Electrolyzer parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ElectrolyzerPlantCapitalCost.tab', format="table", param=model.elyzerPlantCapitalCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ElectrolyzerStackCapitalCost.tab', format="table", param=model.elyzerStackCapitalCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ElectrolyzerFixedOMCost.tab', format="table", param=model.elyzerFixedOMCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ElectrolyzerLifetime.tab', format="table", param=model.elyzerLifetime)
    
    # Reformer parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerCapitalCost.tab', format='table', param=model.ReformerPlantsCapitalCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerFixedOMCost.tab', format='table', param=model.ReformerPlantFixedOMCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerLifetime.tab', format='table', param=model.ReformerPlantLifetime)
    
    # Pipeline parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_PipelineCapitalCost.tab', format="table", param=model.hydrogenPipelineCapCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_PipelineOMCostPerKM.tab', format="table", param=model.hydrogenPipelineOMCost)

    # Storage parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_StorageCapitalCost.tab', format="table", param=model.hydrogenStorageCapitalCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_StorageFixedOMCost.tab', format="table", param=model.hydrogenStorageFixedOMCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_StorageMaxCapacity.tab', format="table", param=model.hydrogenMaxStorageCapacity)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_StorageLifetime.tab', format='table', param=model.hydrogenStorageLifetime)
    
    # CO2 sequestration parameters
    data.load(filename=tab_file_path + '/' + 'CO2_StorageSiteCapitalCost.tab', format="table", param=model.CO2StorageSiteCapitalCost)
    data.load(filename=tab_file_path + '/' + 'CO2_StorageSiteFixedOMCost.tab', format="table", param=model.StorageSiteFixedOMCost)
    data.load(filename=tab_file_path + '/' + 'CO2_PipelineCapitalCost.tab', format="table", param=model.CO2PipelineCapCost)
    data.load(filename=tab_file_path + '/' + 'CO2_PipelineFixedOM.tab', format="table", param=model.CO2PipelineOMCost)
    data.load(filename=tab_file_path + '/' + 'CO2_PipelineLifetime.tab', format="table", param=model.CO2PipelineLifetime)
    data.load(filename=tab_file_path + '/' + 'CO2_MaxSequestrationCapacity.tab', format="table", param=model.maxSequestrationCapacity)
    data.load(filename=tab_file_path + '/' + 'CO2_StorageMaxCapacity.tab', format="table", param=model.CO2StorageMaxHourlyCapacity)
