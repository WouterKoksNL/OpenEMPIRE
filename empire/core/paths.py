from pathlib import Path
from datetime import datetime

from empire.core.config import EmpireConfiguration
from empire.utils import create_if_not_exist


class PathsConfig:
    def __init__(
        self,
        run_name: str,
        dataset_path: Path | str,
        scenario_data_path: Path | str,
        stochastic_data_path: Path | str,
        results_path: Path | str,
        empire_path: Path | str = Path.cwd(),
    ):
        """
        Class containing configurations for running Empire simulations.

        :param run_name: Name of the run
        :param dataset_path: Folder containing the dataset.
        :param tab_path: Folder containing the .tab files.
        :param scenario_data_path: Folder containing the scenario data.
        :param results_path: Folder where the results should reside.
        :param empire_path: Path to empire project, default is current working directory.
        """

        self.run_name = run_name
        self.dataset_path = Path(dataset_path)
        self.scenario_data_path = Path(scenario_data_path)
        self.stochastic_data_path = Path(stochastic_data_path)
        self.results_path = Path(results_path)
        self.empire_path = Path(empire_path)

        # Validate the configuration
        self.validate()

    def validate(self):
        """
        Validates the configuration. Raises an error if the configuration is invalid.
        """
        if not self.empire_path.exists():
            raise ValueError(f"{self.empire_path} does not exists.")

    @classmethod
    def from_dict(cls, config: dict) -> "PathsConfig":
        """
        Constructs PathsConfig object from a dictionary.

        :param config: Dictionary with configurations.
        :returns: An instance of PathsConfig.
        """
        return cls(**config)


def setup_run_paths(
    version: str,
    empire_config: EmpireConfiguration,
    run_path: Path,
    empire_path: Path = Path.cwd(),
) -> PathsConfig:
    """
    Setup run paths for Empire.

    :param version: dataset version.
    :param empire_config: Empire configuration.
    :param run_path: Path containing input and output to the empire run.
    :param empire_path: Path to empire project, optional.
    :return: Empire run configuration.
    """


    # Input folders
    run_name = get_run_name(empire_config=empire_config, version=version)
    run_input_path = create_if_not_exist(run_path / "Input")
    scenario_data_path = create_if_not_exist(run_input_path / "ScenarioData")
    stochastic_data_path = create_if_not_exist(run_input_path / "Stochastic")

    subfolders = ["Sets", "Generator", "Node", "Transmission", "Storage", "General"]
    for sf in subfolders:
        create_if_not_exist(run_input_path / sf)
    # Output folders
    results_path = create_if_not_exist(run_path / "Output")

    return PathsConfig(
        run_name=run_name,
        dataset_path=run_input_path,
        scenario_data_path=scenario_data_path,
        stochastic_data_path=stochastic_data_path,
        results_path=results_path,
        empire_path=empire_path,
    )


def get_run_name(empire_config: EmpireConfiguration, version: str):
    name = (    
        f"{version}_reg{empire_config.length_regular_season}"
        + f"_peak{empire_config.length_peak_season}_sce{empire_config.number_of_scenarios}"
    )

    if not empire_config.fixed_sampling_key_flag and not empire_config.fixed_csv_sample_flag:
        name = name + "_randomSGR"
    else:
        name = name + "_noSGR"
    name = name + str(datetime.now().strftime("_%Y%m%d%H%M"))

    return name
