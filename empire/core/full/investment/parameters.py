from .offshore_converters.parameters import define_offshore_converter_investment_parameters, load_offshore_converter_investment_parameter_data
from .base.parameters import define_base_investment_parameters, load_base_investment_parameter_data
from .hydrogen.parameters import define_hydrogen_investment_parameters, load_hydrogen_investment_parameter_data
from .heat.parameters import define_heat_investment_parameters, load_heat_investment_parameter_data
from .industry.parameters import define_industry_investment_parameters, load_industry_investment_parameter_data

def define_investment_parameters(model, flags):
    define_base_investment_parameters(model)

    if flags.offshore_converters:
        define_offshore_converter_investment_parameters(model)

    if flags.hydrogen:
        define_hydrogen_investment_parameters(model)

    if flags.heat:
        define_heat_investment_parameters(model)

    if flags.industry:
        define_industry_investment_parameters(model)


def load_investment_parameter_data(data, dataset_dir, model, flags, filtering_dict=None):
    # Load investment parameter data
    load_base_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if flags.offshore_converters:
        load_offshore_converter_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)
        
    if flags.hydrogen:
        load_hydrogen_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if flags.heat:
        load_heat_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)

    if flags.industry:
        load_industry_investment_parameter_data(data, dataset_dir, model, filtering_dict=filtering_dict)