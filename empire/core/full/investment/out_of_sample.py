from .base.out_of_sample import define_base_investments_as_param, load_base_oos_investments
from .heat.out_of_sample import define_heat_investments_as_param, load_heat_oos_investments
from .industry.out_of_sample import define_industry_investments_as_param, load_industry_oos_investments
from .hydrogen.out_of_sample import define_hydrogen_investments_as_param, load_hydrogen_oos_investments


def define_investments_as_param(model, flags):
    define_base_investments_as_param(model)
    if flags.heat:
        define_heat_investments_as_param(model)
    if flags.industry:
        define_industry_investments_as_param(model)
    if flags.hydrogen:
        define_hydrogen_investments_as_param(model)


def load_oos_investments(model, data, result_file_path, flags):
    load_base_oos_investments(model, data, result_file_path)

    if flags.heat:
        load_heat_oos_investments(model, data, result_file_path)

    if flags.industry:
        load_industry_oos_investments(model, data, result_file_path)

    if flags.hydrogen:
        load_hydrogen_oos_investments(model, data, result_file_path)
