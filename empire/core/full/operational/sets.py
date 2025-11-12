from .operational_input_params import OperationalInputParams
from empire.core.config import EmpireConfiguration

from .base.sets import define_base_operational_sets
from .natural_gas.sets import define_natural_gas_sets, load_natural_gas_set_data, define_natural_gas_derived_sets

def define_operational_sets(model, operational_input_params: OperationalInputParams, empire_config: EmpireConfiguration):
    """Define operational sets for the model."""
    define_base_operational_sets(model, operational_input_params)

    if empire_config.natural_gas_flag:
        define_natural_gas_sets(model, operational_input_params)

def load_operational_set_data(
    data,
    dataset_dir,
    model,
    empire_config: EmpireConfiguration,
):
    if empire_config.natural_gas_flag:
        load_natural_gas_set_data(data, dataset_dir, model)

def define_operational_derived_sets(model, empire_config: EmpireConfiguration):
    if empire_config.natural_gas_flag:
        define_natural_gas_derived_sets(model)