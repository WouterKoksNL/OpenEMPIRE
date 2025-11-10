from pyomo.core import value


def define_offshore_converter_investment_expressions(model):
    #Offshore converter
    for i in model.Period:
        costperyear = (model.WACC/(1-((1+model.WACC)**(1-model.offshoreConvLifetime))))*model.offshoreConvCapitalCost[i] + model.offshoreConvOMCost[i]
        costperperiod = costperyear*(1-(1+model.discount_rate)**-(min(value((len(model.Period)-i+1)*model.leap_years_investment),model.offshoreConvLifetime)))/(1-(1/(1+model.discount_rate)))
        model.offshoreConvInvCost[i] = costperperiod

       
       #     # GD: Offshore converter investment cost expression
#     def offshoreConvInvCost_expression_rule(model, i):
#         return calculate_period_cost_routine(
#             model.offshoreConvCapitalCost[i],
#             model.offshoreConvOMCost[i],
#             model.offshoreConvLifetime,
#             i,
#             static_data
#         )
#     model.offshoreConvInvCost = Expression(model.Period, rule=offshoreConvInvCost_expression_rule)