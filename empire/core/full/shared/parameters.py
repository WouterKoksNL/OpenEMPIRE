from .base.parameters import define_base_shared_parameters, load_base_shared_parameter_data
from .heat.parameters import define_heat_shared_parameters, load_heat_shared_parameter_data
from .hydrogen.parameters import define_shared_hydrogen_parameters

def define_shared_parameters(model, empire_config, flags):
    # Define shared parameters (common across all modules)
    define_base_shared_parameters(model, empire_config)

    # Define module-specific parameters (conditional)
    if flags.heat:
        define_heat_shared_parameters(model)

    if flags.hydrogen:
        define_shared_hydrogen_parameters(model)



        
def load_shared_parameter_data(data, dataset_dir, model, flags, period=None, scenario=None):
    load_base_shared_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)

    if flags.heat:
        load_heat_shared_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)



    # hydrogen shared parameters are currently loaded in the expressions file