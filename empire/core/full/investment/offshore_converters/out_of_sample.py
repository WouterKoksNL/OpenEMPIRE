from pyomo.environ import Param, NonNegativeReals




def define_offshore_converter_investments_as_param(model):
    # Redefine investment vars as input parameters
    # GD Offshore converter capacity built in period i and total capacity installed
    model.offshoreConvInvCap = Param(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
    model.offshoreConvInstalledCap = Param(model.OffshoreEnergyHubs, model.Period, domain=NonNegativeReals)
    

def load_offshore_converter_oos_investments(model, data, result_file_path):
    """Load investment decisions from in-sample runs as parameters for out-of-sample runs."""
    # Optimized investment decisions read from result file from in-sample runs

    data.load(filename=str(result_file_path + "/" + 'offshoreConvInvCap.tab'), param=model.offshoreConvInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'offshoreConvInstalledCap.tab'), param=model.offshoreConvInstalledCap, format="table")


