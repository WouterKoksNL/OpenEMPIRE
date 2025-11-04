from pyomo.environ import Param, NonNegativeReals


def define_base_investments_as_param(model, offshore_wind=True):
    # Redefine investment vars as input parameters
    model.genInvCap = Param(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
    model.transmissionInvCap = Param(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
    model.storPWInvCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.storENInvCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.genInstalledCap = Param(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
    model.transmissionInstalledCap = Param(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
    model.storPWInstalledCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    model.storENInstalledCap = Param(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
    
    if offshore_wind:
        # GD Offshore converter capacity built in period i and total capacity installed
        model.offshoreConvInvCap = Param(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
        model.offshoreConvInstalledCap = Param(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)

def load_base_oos_investments(model, data, result_file_path, offshore_wind=True):
    """Load investment decisions from in-sample runs as parameters for out-of-sample runs."""
    # Optimized investment decisions read from result file from in-sample runs
    data.load(filename=str(result_file_path + "/" + 'genInvCap.tab'), param=model.genInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'transmissionInvCap.tab'), param=model.transmissionInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'storPWInvCap.tab'), param=model.storPWInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'storENInvCap.tab'), param=model.storENInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'genInstalledCap.tab'), param=model.genInstalledCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'transmissionInstalledCap.tab'), param=model.transmissionInstalledCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'storPWInstalledCap.tab'), param=model.storPWInstalledCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'storENInstalledCap.tab'), param=model.storENInstalledCap, format="table")

    if offshore_wind:
        data.load(filename=str(result_file_path + "/" + 'offshoreConvInvCap.tab'), param=model.offshoreConvInvCap, format="table")
        data.load(filename=str(result_file_path + "/" + 'offshoreConvInstalledCap.tab'), param=model.offshoreConvInstalledCap, format="table")
