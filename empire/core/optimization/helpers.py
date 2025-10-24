from pyomo.environ import value
from pathlib import Path
import time
import logging 
import cloudpickle
import os 
import pandas as pd

from pyomo.common.tempfiles import TempfileManager
import tempfile

def log_problem_statistics(instance, logger):
    logger.info("----------------------Problem Statistics---------------------")
    logger.info("Nodes: %s", len(instance.Node))
    logger.info("Lines: %s", len(instance.BidirectionalArc))
    logger.info("")
    logger.info("GeneratorTypes: %s", len(instance.Generator))
    logger.info("TotalGenerators: %s", len(instance.GeneratorsOfNode))
    logger.info("StorageTypes: %s", len(instance.Storage))
    logger.info("TotalStorages: %s", len(instance.StoragesOfNode))
    logger.info("")
    logger.info("InvestmentUntil: %s", value(2020+int(len(instance.PeriodActive)*instance.LeapYearsInvestment.value)))
    logger.info("Scenarios: %s", len(instance.Scenario))
    logger.info("TotalOperationalHoursPerScenario: %s", len(instance.Operationalhour))
    logger.info("TotalOperationalHoursPerInvYear: %s", len(instance.Operationalhour)*len(instance.Scenario))
    logger.info("Seasons: %s", len(instance.Season))
    logger.info("RegularSeasons: %s", len(instance.FirstHoursOfRegSeason))
    logger.info("LengthRegSeason: %s", value(instance.lengthRegSeason))
    logger.info("PeakSeasons: %s", len(instance.FirstHoursOfPeakSeason))
    logger.info("LengthPeakSeason: %s", value(instance.lengthPeakSeason))
    logger.info("")
    logger.info("Discount rate: %s", value(instance.discountrate))
    logger.info("Operational discount scale: %s", value(instance.operationalDiscountrate))
    logger.info("--------------------------------------------------------------")
    return 


def pickle_instance(
        instance,
        instance_name: str, 
        use_temp_dir_flag: bool,
        logger: logging.Logger,
        temp_dir: None | Path = None,
        ):
    """Pickle the Pyomo model instance to a hardcoded location"""
    start = time.time()
    picklestring = f"instance{instance_name}.pkl"
    if use_temp_dir_flag:
        picklestring = temp_dir / picklestring
    with open(picklestring, mode='wb') as file:
        cloudpickle.dump(instance, file)
    end = time.time()
    logger.info("Pickling instance took [sec]: %d", end - start)
    return 


def prepare_temp_dir(use_temp_dir_flag, temp_dir):
    if use_temp_dir_flag:
        TempfileManager.tempdir = temp_dir

def prepare_results_dir(run_config):
    if not os.path.exists(run_config.results_path):
        os.makedirs(run_config.results_path)
