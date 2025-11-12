from pyomo.environ import Param, NonNegativeReals

from empire.core.loading_utils import load_params


def define_base_investments_as_parameters(model, set_only_capacities: bool = False):
    # Redefine investment vars as input parameters
    model.genInstalledCap = Param(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals, mutable=True)
    model.transmissionInstalledCap = Param(model.BidirectionalArc, model.Period, domain=NonNegativeReals, mutable=True)
    model.storPWInstalledCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals, mutable=True)
    model.storENInstalledCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals, mutable=True)
    if set_only_capacities: 
        return 
    model.genInvCap = Param(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
    model.transmissionInvCap = Param(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
    model.storPWInvCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.storENInvCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    return 


def load_base_optimized_investments(model, data, result_file_path, set_only_capacities: bool = False):
    """Optimized investment decisions read from result file from in-sample runs"""
    investment_params = [
        "genInstalledCap",
        "transmissionInstalledCap",
        "storPWInstalledCap",
        "storENInstalledCap",
    ]
    if not set_only_capacities:
        investment_params += [
            "genInvCap",
            "transmissionInvCap",
            "storPWInvCap",
            "storENInvCap",
        ]
    load_params(data, model, result_file_path, investment_params, component="investments")  
    return 
