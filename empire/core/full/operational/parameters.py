from .base.parameters import define_base_operational_parameters, load_base_operational_parameter_data, load_base_stochastic_parameter_data
from .heat.parameters import define_heat_operational_parameters, load_heat_operational_parameter_data
from .hydrogen.parameters import define_hydrogen_operational_parameters, load_hydrogen_operational_parameter_data
from .industry.parameters import define_industry_operational_parameters, load_industry_operational_parameter_data
from .natural_gas.parameters import define_natural_gas_parameters, load_natural_gas_parameter_data

def define_operational_parameters(model, flags, cvar_percentile, cvar_weight):
    define_base_operational_parameters(model, flags, cvar_percentile, cvar_weight)

    if flags.heat:
        define_heat_operational_parameters(model)

    if flags.hydrogen:
        define_hydrogen_operational_parameters(model)

    if flags.industry:
        define_industry_operational_parameters(model)

    if flags.natural_gas:
        define_natural_gas_parameters(model)


def load_operational_parameter_data(data, dataset_dir, model, flags, period=None, scenario=None, 
                                    out_of_sample_flag=False, sample_file_path=None):

    
    # Load operational parameter data
    load_base_operational_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)
    
    # Load stochastic parameter data

    load_base_stochastic_parameter_data(data, dataset_dir, model, out_of_sample_flag, sample_file_path, period, scenario)

    if flags.natural_gas:
        load_natural_gas_parameter_data(data, dataset_dir, model, flags.gas_stochasticity, period=period, scenario=scenario)

    if flags.heat:
        load_heat_operational_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)

    if flags.hydrogen:
        load_hydrogen_operational_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)

    if flags.industry:
        load_industry_operational_parameter_data(data, dataset_dir, model, period=period, scenario=scenario)