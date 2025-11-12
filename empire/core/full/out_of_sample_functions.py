import os 
from pathlib import Path
from empire.utils import get_name_of_last_folder_in_path


def set_out_of_sample_path(result_file_path, sample_file_path) -> Path:
    """Update result_file_path to output for given out_of_sample tree"""
    sample_tree = get_name_of_last_folder_in_path(sample_file_path)
    result_file_path = result_file_path / f"OutOfSample/{sample_tree}"
    if not os.path.exists(result_file_path):
        os.makedirs(result_file_path)
    return result_file_path


def run_operational_model(
    instance, 
    opt,
    result_file_path,
    instance_name,
    logger
    ):

    logger.info("Computing operational dual values by fixing investment variables and resolving.")

    logger.info("Fixing investment variables")
    for (n,g) in instance.GeneratorsOfNode:
        for i in instance.Period:
            instance.genInvCap[n,g,i].fix()

    for (n1,n2) in instance.BidirectionalArc:
        for i in instance.Period:        
            instance.transmissionInvCap[n1,n2,i].fix()

    for (n,b) in instance.StoragesOfNode:
        for i in instance.Period:
            instance.storPWInvCap[n,b,i].fix()
            instance.storENInvCap[n,b,i].fix()

    logger.info("Resolving")

    opt.solve(instance, tee=True, logfile=result_file_path / f"logfile_{instance_name}_resolved.log")
    return 