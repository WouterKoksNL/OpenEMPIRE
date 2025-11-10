"""Investment-related parameters for the EMPIRE model."""
from pyomo.environ import Param

from empire.core.loading_utils import load_parameter


def define_offshore_converter_investment_parameters(model):
    """Define parameters specific to investment decisions.
    
    Args:
        model: Pyomo abstract model
    """
    model.offshoreConvCapitalCost = Param(model.Period, default=999999, mutable=True)
    model.offshoreConvInvCost = Param(model.Period, default=999999, mutable=True)
    model.offshoreConvOMCost = Param(model.Period, default=999999, mutable=True)
    model.offshoreConvLifetime = Param(default=40)




def load_offshore_converter_investment_parameter_data(data, dataset_dir, model, filtering_dict=None):
    """Load investment parameter data for offshore converters.
    
    Args:
        data: Pyomo DataPortal object
        dataset_dir: Path to directory containing input data. 
        model: Pyomo model with parameters already defined
    """
    transmission_params = [
        "offshoreConvCapitalCost",
        "offshoreConvOMCost",
    ]

    for param in transmission_params:
        load_parameter(
            data,
            full_path=dataset_dir / "Transmission",
            param_name=param,
            param=getattr(model, param),
            model=model,
            filtering_dict=filtering_dict
        )