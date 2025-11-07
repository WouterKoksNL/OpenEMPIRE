
from pyomo.environ import Param, DataPortal

from empire.core.loading_utils import load_parameters

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


def load_hydrogen_operational_parameter_data(data: DataPortal, dataset_dir, model, filtering_dict=None, enable_transport=False):
    """Load hydrogen and optionally transport operational parameter data.
    
    Args:
        data: Pyomo DataPortal object
        dataset_dir: Path to dataset input directory
        model: AbstractModel
        filtering_dict: Optional dict for filtering data to load. Keys are column names, values are lists of accepted values.
        enable_transport: Whether to load transport parameters
    """

    hydrogen_param_list = [
        'elyzerPowerConsumptionPerTon',
        'H2TerminalPrice',
        'hydrogenPipelineCompressorElectricityUsage',
        'ReformerPlantVarOMCost',
        'ReformerPlantEfficiency',
        'ReformerPlantElectricityUse',
        'ReformerEmissionFactor',
        'ReformerCO2CaptureFactor',
        'CO2PipelineElectricityUsage',
    ]

    load_parameters(
        data,
        full_path=dataset_dir/ 'Hydrogen',
        param_name_list=hydrogen_param_list,
        model=model,
        filtering_dict=filtering_dict
    )

    if enable_transport:
        transport_param_list = [
            'transport_electricity_demand',
            'transport_hydrogen_demand',
            'transport_naturalGas_demand',
            'transport_curtail_cost',
        ]

        load_parameters(
            data,
            full_path=dataset_dir / 'Transport',
            param_name_list=transport_param_list,
            model=model,
            filtering_dict=filtering_dict
        )