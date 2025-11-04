"""Industry investment build actions."""
from pyomo.environ import BuildAction, value


def define_industry_investment_expressions(model, LeapYearsInvestment, steel_CCS_cost_increase):
    """Define build actions for industry plant investment costs.
    
    Args:
        model: Pyomo abstract model
        LeapYearsInvestment: Number of years per investment period
        steel_CCS_cost_increase: Optional cost increase factor for steel CCS plants
    """
    
    def prepIndustryInvCost_rule(model):
        """Build investment cost for industry plants."""
        # Steel plants
        for i in model.Period:
            for p in model.SteelPlants:
                if steel_CCS_cost_increase is not None and 'ccs' in p.lower():
                    model.steel_plantCapitalCost[p, i] = (1 + steel_CCS_cost_increase) * model.steel_plantCapitalCost[p, i]
                costperyear = (model.WACC / (1 - ((1 + model.WACC) ** (1 - model.steelPlantLifetime[p])))) * \
                             model.steel_plantCapitalCost[p, i] + model.steel_plantFixedOM[p, i]
                costperperiod = costperyear * (1 - (1 + model.discountrate) ** 
                               -(min(value((len(model.Period) - i + 1) * LeapYearsInvestment), 
                                    model.steelPlantLifetime[p]))) / (1 - (1 / (1 + model.discountrate)))
                model.steel_plantInvCost[p, i] = costperperiod

        # Cement plants
        for i in model.Period:
            for p in model.CementPlants:
                costperyear = (model.WACC / (1 - ((1 + model.WACC) ** (1 - model.cementPlantLifetime[p])))) * \
                             model.cement_plantCapitalCost[p, i] + model.cement_plantFixedOM[p, i]
                costperperiod = costperyear * (1 - (1 + model.discountrate) ** 
                               -(min(value((len(model.Period) - i + 1) * LeapYearsInvestment), 
                                    model.cementPlantLifetime[p]))) / (1 - (1 / (1 + model.discountrate)))
                model.cement_plantInvCost[p, i] = costperperiod

        # Ammonia plants
        for i in model.Period:
            for p in model.AmmoniaPlants:
                costperyear = (model.WACC / (1 - ((1 + model.WACC) ** (1 - model.ammoniaPlantLifetime[p])))) * \
                             model.ammonia_plantCapitalCost[p, i] + model.ammonia_plantFixedOM[p, i]
                costperperiod = costperyear * (1 - (1 + model.discountrate) ** 
                               -(min(value((len(model.Period) - i + 1) * LeapYearsInvestment), 
                                    model.ammoniaPlantLifetime[p]))) / (1 - (1 / (1 + model.discountrate)))
                model.ammonia_plantInvCost[p, i] = costperperiod
    model.build_IndustryInvCost = BuildAction(rule=prepIndustryInvCost_rule)

