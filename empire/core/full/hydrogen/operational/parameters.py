
from pyomo.environ import Param, DataPortal

def define_hydrogen_operational_parameters(model):

    model.elyzerPowerConsumptionPerTon = Param(model.Period, default=99999, mutable=True)
    model.ReformerPlantVarOMCost = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerPlantEfficiency = Param(model.ReformerPlants, model.Period, default=0, mutable=True)
    model.ReformerPlantElectricityUse = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerEmissionFactor = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerCO2CaptureFactor = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.ReformerMargCost = Param(model.ReformerPlants, model.Period, default=99999, mutable=True)
    model.H2TerminalMargCost = Param(model.H2TerminalNodes, model.H2Terminals, model.Period, default=99999, mutable=True)
    model.hydrogenStorageInitOperational = Param(default=0.5)
    model.H2TerminalPrice = Param(model.H2TerminalNodes, model.H2Terminals, model.Period, default=99999, mutable=True)
    model.CO2PipelinePowerDemandPerTon = Param(model.CO2BidirectionalPipelines, default=99999, mutable=True)
    model.hydrogenPipelineCompressorElectricityUsage = Param(default=99999, mutable=True)
    model.hydrogenPipelinePowerDemandPerTon = Param(model.HydrogenBidirectionPipelines, default=99999, mutable=True)

    # Transport hydrogen demand parameters
    model.transport_electricity_demand = Param(model.OnshoreNode, model.Period)
    model.transport_hydrogen_demand = Param(model.OnshoreNode, model.Period)
    model.transport_naturalGas_demand = Param(model.OnshoreNode, model.Period)
    model.transport_curtail_cost = Param(default=10000, mutable=True)
    model.CO2PipelineElectricityUsage = Param(default=99999, mutable=True)

def load_hydrogen_operational_parameter_data(data: DataPortal, tab_file_path, model):
    """Load hydrogen operational parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # Electrolyzer operational parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ElectrolyzerPowerUse.tab', format="table", param=model.elyzerPowerConsumptionPerTon)
    
    # Terminal operational parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_H2TerminalPrice.tab', format="table", param=model.H2TerminalPrice)

    # Pipeline operational parameters
    data.load(filename=tab_file_path + '/' + 'Hydrogen_PipelineCompressorPowerUsage.tab', format="table", param=model.hydrogenPipelineCompressorElectricityUsage)
    
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerVariableOMCost.tab', format='table', param=model.ReformerPlantVarOMCost)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerEfficiency.tab', format='table', param=model.ReformerPlantEfficiency)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerElectricityUse.tab', format='table', param=model.ReformerPlantElectricityUse)

    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerEmissionFactor.tab', format='table', param=model.ReformerEmissionFactor)
    data.load(filename=tab_file_path + '/' + 'Hydrogen_ReformerCO2CaptureFactor.tab', format='table', param=model.ReformerCO2CaptureFactor)
    data.load(filename=tab_file_path + '/' + 'CO2_PipelineElectricityUsage.tab', format="table", param=model.CO2PipelineElectricityUsage)

    # Transport demand parameters
    data.load(filename=tab_file_path + '/' + 'Transport_ElectricityDemand.tab', param=model.transport_electricity_demand, format='table')
    data.load(filename=tab_file_path + '/' + 'Transport_HydrogenDemand.tab', param=model.transport_hydrogen_demand, format='table')
    data.load(filename=tab_file_path + '/' + 'Transport_NaturalGasDemand.tab', param=model.transport_naturalGas_demand, format='table')
    data.load(filename=tab_file_path + '/' + 'Transport_CurtailCost.tab', param=model.transport_curtail_cost, format='table')
