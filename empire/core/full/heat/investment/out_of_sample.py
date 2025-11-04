from pyomo.environ import Param, NonNegativeReals

def define_heat_investments_as_param(model):
    model.ConverterInvCap = Param(model.ConverterOfNode, model.Period, domain=NonNegativeReals)
    model.ConverterInstalledCap = Param(model.ConverterOfNode, model.Period, domain=NonNegativeReals)

def load_heat_oos_investments(model, data, result_file_path):
    """Load heat module investment decisions from in-sample runs as parameters for out-of-sample run.
    """
    data.load(filename=str(result_file_path + "/" + 'ConverterInvCap.tab'), param=model.ConverterInvCap, format="table")
    data.load(filename=str(result_file_path + "/" + 'ConverterInstalledCap.tab'), param=model.ConverterInstalledCap, format="table")
    