from .offshore_converters.parameters import define_offshore_converter_investment_parameters, load_offshore_converter_investment_parameter_data
from .base.parameters import define_base_investment_parameters, load_base_investment_parameter_data
from .hydrogen.parameters import define_hydrogen_investment_parameters, load_hydrogen_investment_parameter_data
from .heat.parameters import define_heat_investment_parameters, load_heat_investment_parameter_data
from .industry.parameters import define_industry_investment_parameters, load_industry_investment_parameter_data

def define_investment_parameters(model, empire_config):
    define_base_investment_parameters(model)

    if empire_config.offshore_converters_flag:
        define_offshore_converter_investment_parameters(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_investment_parameters(model)

    if empire_config.heat_flag:
        define_heat_investment_parameters(model)

    if empire_config.industry_flag:
        define_industry_investment_parameters(model)


def load_investment_parameter_data(data, dataset_dir, model, empire_config, filtering_dict=None):
    # Load investment parameter data
    load_base_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if empire_config.offshore_converters_flag:
        load_offshore_converter_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if empire_config.hydrogen_flag:
        load_hydrogen_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if empire_config.heat_flag:
        load_heat_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if empire_config.industry_flag:
        load_industry_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)