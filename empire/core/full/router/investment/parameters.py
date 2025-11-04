from base.investment.parameters import define_base_investment_parameters, load_base_investment_parameter_data
from hydrogen.investment.parameters import define_hydrogen_investment_parameters, load_hydrogen_investment_parameter_data
from heat.investment.parameters import define_heat_investment_parameters, load_heat_investment_parameter_data
from industry.investment.parameters import define_industry_investment_parameters, load_industry_investment_parameter_data

def define_investment_parameters(model, flags):
    define_base_investment_parameters(model)

    if flags.hydrogen:
        define_hydrogen_investment_parameters(model)

    if flags.heat:
        define_heat_investment_parameters(model)

    if flags.industry:
        define_industry_investment_parameters(model)


def load_investment_parameter_data(data, tab_file_path, model, flags):
    # Load investment parameter data
    load_base_investment_parameter_data(data, tab_file_path, model)

    if flags.hydrogen:
        load_hydrogen_investment_parameter_data(data, tab_file_path, model)

    if flags.heat:
        load_heat_investment_parameter_data(data, tab_file_path, model)

    if flags.industry:
        load_industry_investment_parameter_data(data, tab_file_path, model)