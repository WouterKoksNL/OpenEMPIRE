from empire.core.config import EmpireConfiguration

from .base.sets import define_base_shared_sets, load_base_shared_set_data, define_base_shared_derived_sets
from .heat.sets import define_heat_sets, define_heat_derived_sets, load_heat_set_data
from .hydrogen.sets import define_hydrogen_sets, define_hydrogen_derived_sets, load_hydrogen_set_data
from .industry.sets import define_industry_sets, define_industry_derived_sets, load_industry_set_data
from .offshore_converters.sets import define_shared_offshore_converter_derived_sets


def define_shared_sets(
        model, 
        windfarmNodes,
        empire_config: EmpireConfiguration
    ):
    # Define shared sets (common across all modules)
    define_base_shared_sets(model, windfarmNodes)


    if empire_config.heat_flag:
        define_heat_sets(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_sets(model)

    if empire_config.industry_flag:
        define_industry_sets(model)


def load_shared_set_data(data, dataset_dir, model, empire_config: EmpireConfiguration, load_period, periods_active):
    load_base_shared_set_data(data, dataset_dir, model, load_period=load_period, periods_active=periods_active)
    
    # Load module-specific set data (conditional)
    if empire_config.heat_flag:
        load_heat_set_data(data, dataset_dir, model)

    if empire_config.industry_flag:
        load_industry_set_data(data, dataset_dir, model)

    if empire_config.hydrogen_flag:
        load_hydrogen_set_data(data, dataset_dir, model)



def define_shared_derived_sets(model, offshoreNodesList, empire_config: EmpireConfiguration):
    """Build derived sets that depend on loaded data"""

    define_base_shared_derived_sets(model)

    if empire_config.offshore_converters_flag:
        define_shared_offshore_converter_derived_sets(model, offshoreNodesList)

    if empire_config.heat_flag:
        define_heat_derived_sets(model)

    if empire_config.industry_flag:
        define_industry_derived_sets(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_derived_sets(model)