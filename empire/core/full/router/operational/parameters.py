from base.operational.parameters import define_base_operational_parameters, load_base_operational_parameter_data, load_base_stochastic_parameter_data
from heat.operational.parameters import define_heat_operational_parameters, load_heat_operational_parameter_data
from hydrogen.operational.parameters import define_hydrogen_operational_parameters, load_hydrogen_operational_parameter_data
from industry.operational.parameters import define_industry_operational_parameters, load_industry_operational_parameter_data

from empire_types import Flags

def define_operational_parameters(model, flags: Flags, cvar_percentile, cvar_weight):
    define_base_operational_parameters(model, flags, cvar_percentile, cvar_weight)

    if flags.heat:
        define_heat_operational_parameters(model)

    if flags.hydrogen:
        define_hydrogen_operational_parameters(model)

    if flags.industry:
        define_industry_operational_parameters(model)


def load_operational_parameter_data(data, model, scenariogeneration, tab_file_path, scenario_data_path, sample_file_path, flags: Flags):
    # Determine scenario path
    if scenariogeneration:
        scenariopath = tab_file_path
    else:
        scenariopath = scenario_data_path

    
    # Load operational parameter data
    load_base_operational_parameter_data(data, tab_file_path, model)
    
    # Load stochastic parameter data
    load_base_stochastic_parameter_data(data, scenariopath, sample_file_path, model, flags.out_of_sample)
    if flags.heat:
        load_heat_operational_parameter_data(data, tab_file_path, model)

    if flags.hydrogen:
        load_hydrogen_operational_parameter_data(data, tab_file_path, model)

    if flags.industry:
        load_industry_operational_parameter_data(data, tab_file_path, model)