from .base.constraints import define_base_investment_constraints
from .heat.constraints import define_heat_investment_constraints
from .hydrogen.constraints import define_hydrogen_investment_constraints
from .industry.constraints import define_industry_investment_constraints
from .offshore_converters.constraints import define_offshore_converter_investment_constraints

def define_investment_constraints(model, empire_config, windfarmNodes):

    define_base_investment_constraints(model, windfarmNodes=windfarmNodes)
    
    if empire_config.offshore_converters_flag:
        define_offshore_converter_investment_constraints(model)

    if empire_config.heat_flag:
        define_heat_investment_constraints(model)
    if empire_config.hydrogen_flag:
        define_hydrogen_investment_constraints(model)
    if empire_config.industry_flag:
        define_industry_investment_constraints(model)
