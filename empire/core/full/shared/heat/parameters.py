"""Heat module-specific parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_heat_shared_parameters(model):
    
    model.storagePowToEnergyTR = Param(model.DependentStorageTR, default=1.0, mutable=True)
    



def load_heat_shared_parameter_data(data, tab_file_path, model):

    # Load shared parameters
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleStorage_StoragePowToEnergy.tab', param=model.storagePowToEnergyTR, format="table")
