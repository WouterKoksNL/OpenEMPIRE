from base.shared.parameters import define_base_shared_parameters, load_base_shared_parameter_data
from heat.shared.parameters import define_heat_shared_parameters, load_heat_shared_parameter_data
from hydrogen.shared.parameters import define_shared_hydrogen_parameters
from natural_gas.parameters import define_natural_gas_parameters, load_natural_gas_parameter_data

from empire_types import Flags

def define_shared_parameters(model, discountrate, WACC, lengthRegSeason, lengthPeakSeason, EMISSION_CAP, flags: Flags):
    # Define shared parameters (common across all modules)
    define_base_shared_parameters(model, discountrate, WACC, lengthRegSeason, lengthPeakSeason, EMISSION_CAP)

    # Define module-specific parameters (conditional)
    if flags.heat:
        define_heat_shared_parameters(model)

    if flags.hydrogen:
        define_shared_hydrogen_parameters(model)

    if flags.natural_gas:
        define_natural_gas_parameters(model)


        
def load_shared_parameter_data(model, data, tab_file_path, flags: Flags):
    load_base_shared_parameter_data(data, tab_file_path, model)

    if flags.natural_gas:
        load_natural_gas_parameter_data(data, tab_file_path, model, flags.gas_stochasticity)

    if flags.heat:
        load_heat_shared_parameter_data(data, tab_file_path, model)



    # hydrogen shared parameters are currently loaded in the expressions file