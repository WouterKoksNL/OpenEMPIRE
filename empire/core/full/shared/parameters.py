from empire.core.config import EmpireConfiguration
from .base.parameters import define_base_shared_parameters, load_base_shared_parameter_data
from .heat.parameters import define_heat_shared_parameters, load_heat_shared_parameter_data
from .hydrogen.parameters import define_shared_hydrogen_parameters

def define_shared_parameters(model, empire_config: EmpireConfiguration):
    # Define shared parameters (common across all modules)
    define_base_shared_parameters(model, empire_config)

    # Define module-specific parameters (conditional)
    if empire_config.heat_flag:
        define_heat_shared_parameters(model)

    if empire_config.hydrogen_flag:
        define_shared_hydrogen_parameters(model)




def load_shared_parameter_data(data, dataset_dir, model, empire_config: EmpireConfiguration, filtering_dict=None):
    load_base_shared_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if empire_config.heat_flag:
        load_heat_shared_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)



    # hydrogen shared parameters are currently loaded in the expressions file