from .base.parameters import define_base_operational_parameters, load_base_operational_parameter_data, load_base_stochastic_parameter_data
from .heat.parameters import define_heat_operational_parameters, load_heat_operational_parameter_data
from .hydrogen.parameters import define_hydrogen_operational_parameters, load_hydrogen_operational_parameter_data
from .industry.parameters import define_industry_operational_parameters, load_industry_operational_parameter_data
from .natural_gas.parameters import define_natural_gas_parameters, load_natural_gas_parameter_data
from empire.core.config import EmpireConfiguration 

def define_operational_parameters(model, empire_config: EmpireConfiguration):
    define_base_operational_parameters(model, empire_config)

    if empire_config.heat_flag:
        define_heat_operational_parameters(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_operational_parameters(model)

    if empire_config.industry_flag:
        define_industry_operational_parameters(model)

    if empire_config.natural_gas_flag:
        define_natural_gas_parameters(model)


def load_operational_parameter_data(data, dataset_dir, stochastic_input_dir, model, empire_config: EmpireConfiguration, filtering_dict=None):

    # Load operational parameter data
    load_base_operational_parameter_data(data, dataset_dir, model, filtering_dict)
    
    # Load stochastic parameter data

    load_base_stochastic_parameter_data(data, stochastic_input_dir, dataset_dir, model, filtering_dict)

    if empire_config.natural_gas_flag:
        load_natural_gas_parameter_data(data, dataset_dir, model, empire_config.gas_stochasticity, filtering_dict)

    if empire_config.heat_flag:
        load_heat_operational_parameter_data(data, dataset_dir, model, ...)

    if empire_config.hydrogen_flag:
        load_hydrogen_operational_parameter_data(data, dataset_dir, model, filtering_dict, enable_transport=empire_config.transport_flag)

    if empire_config.industry_flag:
        load_industry_operational_parameter_data(data, dataset_dir, model, ...)