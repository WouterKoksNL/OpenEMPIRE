from empire.core.empire_types import Flags

from .base.sets import define_base_shared_sets, load_base_shared_set_data, define_base_shared_derived_sets
from .heat.sets import define_heat_sets, define_heat_derived_sets, load_heat_set_data
from .hydrogen.sets import define_hydrogen_sets, define_hydrogen_derived_sets, load_hydrogen_set_data
from .industry.sets import define_industry_sets, define_industry_derived_sets, load_industry_set_data
from .offshore_converters.sets import define_shared_offshore_converter_derived_sets


def define_shared_sets(
        model, 
        windfarmNodes,
        flags: Flags
    ):
    # Define shared sets (common across all modules)
    define_base_shared_sets(model, windfarmNodes)


    if flags.heat:
        define_heat_sets(model)

    if flags.hydrogen:
        define_hydrogen_sets(model)

    if flags.industry:
        define_industry_sets(model)


def load_shared_set_data(data, dataset_dir, model, flags: Flags, load_period, periods_active):
    load_base_shared_set_data(data, dataset_dir, model, load_period=load_period, periods_active=periods_active)
    
    # Load module-specific set data (conditional)
    if flags.heat:
        load_heat_set_data(data, dataset_dir, model)

    if flags.industry:
        load_industry_set_data(data, dataset_dir, model)

    if flags.hydrogen:
        load_hydrogen_set_data(data, dataset_dir, model)



def define_shared_derived_sets(model, offshoreNodesList, flags: Flags):
    """Build derived sets that depend on loaded data"""
    
    define_base_shared_derived_sets(model)

    if flags.offshore_converters:
        define_shared_offshore_converter_derived_sets(model, offshoreNodesList)

    if flags.heat:
        define_heat_derived_sets(model)

    if flags.industry:
        define_industry_derived_sets(model)

    if flags.hydrogen:
        define_hydrogen_derived_sets(model)