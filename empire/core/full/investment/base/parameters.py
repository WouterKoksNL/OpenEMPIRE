"""Investment-related parameters for the EMPIRE model."""
from pyomo.environ import Param

from empire.core.loading_utils import load_parameters


def define_base_investment_parameters(model, offshore_wind=True):
    """Define parameters specific to investment decisions.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Generator investment parameters
    model.genCapitalCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.genFixedOMCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.genInvCost = Param(model.Generator, model.Period, default=9000000, mutable=True)
    model.genLifetime = Param(model.Generator, default=0.0, mutable=True)
    model.genRefInitCap = Param(model.GeneratorsOfNode, default=0.0, mutable=True)
    model.genScaleInitCap = Param(model.Generator, model.Period, default=0.0, mutable=True)
    model.genInitCap = Param(model.GeneratorsOfNode, model.Period, default=0.0, mutable=True)
    model.genMaxBuiltCap = Param(model.Node, model.Technology, model.Period, default=500000.0, mutable=True)
    model.genMaxInstalledCapRaw = Param(model.Node, model.Technology, default=0.0, mutable=True)
    model.genMaxInstalledCapByPeriod = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
    model.genMaxInstalledCap = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
    model.genMaxBiomethaneAvailability = Param(model.Node, model.Period, default=999999, mutable=True)
    
    # Transmission investment parameters
    model.transmissionTypeCapitalCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.transmissionTypeFixedOMCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.transmissionInvCost = Param(model.BidirectionalArc, model.Period, default=3000000, mutable=True)
    model.transmissionLength = Param(model.BidirectionalArc, mutable=True)
    model.transmissionInitCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.transmissionMaxBuiltCap = Param(model.BidirectionalArc, model.Period, default=10000.0, mutable=True)
    model.transmissionMaxInstalledCapRaw = Param(model.BidirectionalArc, model.Period, default=0.0)
    model.transmissionMaxInstalledCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.transmissionLifetime = Param(model.BidirectionalArc, default=40.0, mutable=True)
    
    # Storage investment parameters
    model.storPWCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storPWFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storPWInvCost = Param(model.Storage, model.Period, default=1000000, mutable=True)
    model.storENInvCost = Param(model.Storage, model.Period, default=800000, mutable=True)
    model.storPWInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storPWMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storENMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storPWMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storPWMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)
    model.storENMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)
    model.storageLifetime = Param(model.Storage, default=0.0, mutable=True)
    
    # Offshore converter investment parameters
    if offshore_wind:
        model.offshoreConvCapitalCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvInvCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvOMCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvLifetime = Param(default=40)




def load_base_investment_parameter_data(data, dataset_dir, model, filtering_dict=None, offshore_wind=True):
    """Load investment parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """


    input_parameters = {
        "Generator": [
            "genCapitalCost",
            "genFixedOMCost",
            "genRefInitCap",
            "genScaleInitCap",
            "genInitCap",
            "genMaxBuiltCap",
            "genMaxInstalledCapRaw",
            "genMaxInstalledCapByPeriod",
            "genMaxBiomethaneAvailability",
            "genLifetime",
        ],
        "Transmission": [
            "transmissionInitCap",
            "transmissionMaxBuiltCap",
            "transmissionMaxInstalledCapRaw",
            "transmissionLength",
            "transmissionTypeCapitalCost",
            "transmissionTypeFixedOMCost",
            "transmissionLifetime", 
        ],
        "Storage": [
            "storENCapitalCost",
            "storENFixedOMCost",
            "storENInitCap",
            "storENMaxBuiltCap",
            "storENMaxInstalledCapRaw",
            "storPWCapitalCost",
            "storPWFixedOMCost",
            "storPWInitCap",
            "storPWMaxBuiltCap",
            "storPWMaxInstalledCapRaw",
            "storageLifetime",
        ],
    }
    if offshore_wind:
        input_parameters["Transmission"].extend([
            "offshoreConvCapitalCost",
            "offshoreConvOMCost",
        ])

    for component, param_list in input_parameters.items():
        load_parameters(
            data,
            full_path=dataset_dir / component,
            param_name_list=param_list,
            model=model,
            filtering_dict=filtering_dict
        )