from .base.constraints import define_base_investment_constraints
from .heat.constraints import define_heat_investment_constraints
from .hydrogen.constraints import define_hydrogen_investment_constraints
from .industry.constraints import define_industry_investment_constraints


def define_investment_constraints(model, empire_config, windfarmNodes, flags):

    define_base_investment_constraints(model, windfarmNodes=windfarmNodes)
    if flags.heat:
        define_heat_investment_constraints(model)
    if flags.hydrogen:
        define_hydrogen_investment_constraints(model)
    if flags.industry:
        define_industry_investment_constraints(model)
