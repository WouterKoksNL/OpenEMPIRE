from argparse import ArgumentParser
from pathlib import Path

from empire.core.config import EmpireConfiguration, read_config_file
from empire.core.model_runner import run_empire_model
from empire.core.paths import setup_run_paths
from empire.utils import copy_csv_dataset

from empire.input_client.csv_client import EmpireInputClient 
from empire.logger import get_empire_logger

parser = ArgumentParser(description="A CLI script to run the Empire model.")

parser.add_argument("-t", "--test-run", help="Test run without optimization", action="store_true")
parser.add_argument(
    "-d",
    "--dataset",
    help="Specify the required dataset",
    default="europe_v51",
)
parser.add_argument("-f", "--force", help="Force new run if old exist.", action="store_true")
parser.add_argument("-c", "--config-file", help="Path to config file.", default="config/run.yaml")

args = parser.parse_args()

## Read config and setup folders ##
if args.dataset == "test":
    config = read_config_file(Path("config/testrun.yaml"))
else:
    config = read_config_file(Path(args.config_file))

empire_config = EmpireConfiguration.from_dict(config=config)

run_path = Path(f"Results/basic_run/dataset_{args.dataset}")

if (run_path / "Output/results_objective.csv").exists() and not args.force:
    raise ValueError("There already exists results for this analysis run.")

paths = setup_run_paths(version=args.dataset, empire_config=empire_config, run_path=run_path)


base_dataset = Path("input_data") / args.dataset
copy_csv_dataset(base_dataset, paths.dataset_path) 
    # Copy base dataset to inputs.input_data_path 
logger = get_empire_logger(paths=paths)

logger.info("Running EMPIRE Model")

client = EmpireInputClient(dataset_path=paths.dataset_path)

data_managers = [
    # Add input data managers to alter the dataset
]

## Run empire model
run_empire_model(
    empire_config=empire_config, paths=paths, data_managers=data_managers, test_run=args.test_run
)
