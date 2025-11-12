from .base.out_of_sample import define_base_investments_as_parameters, load_base_optimized_investments
from .heat.out_of_sample import define_heat_investments_as_param, load_heat_oos_investments
from .industry.out_of_sample import define_industry_investments_as_param, load_industry_oos_investments
from .hydrogen.out_of_sample import define_hydrogen_investments_as_param, load_hydrogen_oos_investments
from .offshore_converters.out_of_sample import define_offshore_converter_investments_as_param, load_offshore_converter_oos_investments

def define_investments_as_param(model, empire_config):

    define_base_investments_as_parameters(model)
    if empire_config.offshore_converters_flag:
        define_offshore_converter_investments_as_param(model)
    if empire_config.heat_flag:
        define_heat_investments_as_param(model)
    if empire_config.industry_flag:
        define_industry_investments_as_param(model)
    if empire_config.hydrogen_flag:
        define_hydrogen_investments_as_param(model)


def load_oos_investments(model, data, result_file_path, empire_config):
    load_base_optimized_investments(model, data, result_file_path)

    if empire_config.offshore_converters_flag:
        load_offshore_converter_oos_investments(model, data, result_file_path)
        
    if empire_config.heat_flag:
        load_heat_oos_investments(model, data, result_file_path)

    if empire_config.industry_flag:
        load_industry_oos_investments(model, data, result_file_path)

    if empire_config.hydrogen_flag:
        load_hydrogen_oos_investments(model, data, result_file_path)
