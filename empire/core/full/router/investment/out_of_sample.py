from base.investment.out_of_sample import define_base_investments_as_param, load_base_oos_investments
from heat.investment.out_of_sample import define_heat_investments_as_param, load_heat_oos_investments
from industry.investment.out_of_sample import define_industry_investments_as_param, load_industry_oos_investments
from hydrogen.investment.out_of_sample import define_hydrogen_investments_as_param, load_hydrogen_oos_investments
from empire_types import Flags


def define_investments_as_param(model, flags: Flags):
    define_base_investments_as_param(model)
    if flags.heat:
        define_heat_investments_as_param(model)
    if flags.industry:
        define_industry_investments_as_param(model)
    if flags.hydrogen:
        define_hydrogen_investments_as_param(model)


def load_oos_investments(model, data, result_file_path, flags: Flags):
    load_base_oos_investments(model, data, result_file_path)

    if flags.heat:
        load_heat_oos_investments(model, data, result_file_path)

    if flags.industry:
        load_industry_oos_investments(model, data, result_file_path)

    if flags.hydrogen:
        load_hydrogen_oos_investments(model, data, result_file_path)
