from empire_types import Flags

from base.shared.sets import define_base_shared_sets, load_base_shared_set_data, define_base_shared_derived_sets
from heat.shared.sets import define_heat_sets, define_heat_derived_sets, load_heat_set_data
from hydrogen.shared.sets import define_hydrogen_sets, define_hydrogen_derived_sets, load_hydrogen_set_data
from natural_gas.sets import define_natural_gas_sets, load_natural_gas_set_data
from industry.shared.sets import define_industry_sets, define_industry_derived_sets, load_industry_set_data

def define_shared_sets(
        model, 
        Period,
        windfarmNodes,
        flags: Flags
    ):
    # Define shared sets (common across all modules)
    define_base_shared_sets(model, Period, windfarmNodes)
    
    # Define module-specific sets (conditional)
    if flags.natural_gas:
        define_natural_gas_sets(model)

    if flags.heat:
        define_heat_sets(model)

    if flags.hydrogen:
        define_hydrogen_sets(model)

    if flags.industry:
        define_industry_sets(model)


def load_shared_set_data(model, data, tab_file_path, flags: Flags):
    load_base_shared_set_data(data, tab_file_path, model)
    
    # Load module-specific set data (conditional)
    if flags.heat:
        load_heat_set_data(data, tab_file_path, model)

    if flags.industry:
        load_industry_set_data(data, tab_file_path, model)
    
    # Load natural gas set data
    if flags.natural_gas:
        load_natural_gas_set_data(data, tab_file_path, model)

    if flags.hydrogen:
        load_hydrogen_set_data(data, tab_file_path, model)



def define_shared_derived_sets(model, offshoreNodesList, flags: Flags):
    define_base_shared_derived_sets(model, offshoreNodesList)
    # Build derived sets that depend on loaded data
    if flags.heat:
        define_heat_derived_sets(model)

    if flags.industry:
        define_industry_derived_sets(model)

    if flags.hydrogen:
        define_hydrogen_derived_sets(model)