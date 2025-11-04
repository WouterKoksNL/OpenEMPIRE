from base.investment.constraints import define_base_investment_constraints
from heat.investment.constraints import define_heat_investment_constraints
from hydrogen.investment.constraints import define_hydrogen_investment_constraints
from industry.investment.constraints import define_industry_investment_constraints
from empire_types import Flags

def define_investment_constraints(model, LeapYearsInvestment, repurposeEnergyFlowFactor, windfarmNodes, flags: Flags):

    define_base_investment_constraints(model, LeapYearsInvestment, windfarmNodes=windfarmNodes)
    if flags.heat:
        define_heat_investment_constraints(model, flags)
    if flags.hydrogen:
        define_hydrogen_investment_constraints(model, LeapYearsInvestment, repurposeEnergyFlowFactor)
    if flags.industry:
        define_industry_investment_constraints(model, flags)
