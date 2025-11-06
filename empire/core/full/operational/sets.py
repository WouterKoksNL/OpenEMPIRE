from .operational_input_params import OperationalInputParams

from .base.sets import define_base_operational_sets
from .natural_gas.sets import define_natural_gas_sets, load_natural_gas_set_data

def define_operational_sets(model, operational_input_params: OperationalInputParams, flags):
    """Define operational sets for the model."""
    define_base_operational_sets(model, operational_input_params)

    if flags.natural_gas:
        define_natural_gas_sets(model, operational_input_params)

def load_operational_set_data(
    data,
    dataset_dir,
    model,
):
    load_natural_gas_set_data(data, dataset_dir, model)