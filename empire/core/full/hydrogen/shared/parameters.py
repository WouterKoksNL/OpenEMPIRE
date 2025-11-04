"""Hydrogen-specific shared parameters for the EMPIRE model.

Parameters in this file are used by both investment and operational modules.
Investment-specific parameters are in hydrogen/investment/parameters.py
Operational-specific parameters are in hydrogen/operational/parameters.py
Data loading has been moved to hydrogen/shared/data_loader.py
"""
from pyomo.environ import Param

# where to load pipeline length?!
def define_shared_hydrogen_parameters(model):
    """Define parameters specific to the hydrogen module that are shared across investment and operational.
    
    Args:
        model: Pyomo abstract model
    """
    model.PipelineLength = Param(model.HydrogenBidirectionPipelines, mutable=True, default=9999)  # data is loaded in 

