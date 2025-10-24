#!/usr/bin/env python
import json
import logging
from pathlib import Path

from empire import run_empire
from empire.core.config import (EmpireConfiguration, EmpireRunConfiguration, OperationalInputParams,
                                read_config_file)
from empire.core.scenario_random import generate_random_scenario
from empire.input_data_manager import IDataManager
from empire.utils import (copy_csv_dataset, copy_scenario_data,
                          create_if_not_exist, get_run_name)
from empire.core.benders.algorithm import run_benders


logger = logging.getLogger(__name__)


def define_operational_input_params(empire_config: EmpireConfiguration):
    FirstHoursOfRegSeason = [empire_config.length_of_regular_season * i + 1 for i in range(empire_config.n_reg_season)]
    FirstHoursOfPeakSeason = [empire_config.length_of_regular_season * empire_config.n_reg_season + empire_config.len_peak_season * i + 1 for i in range(empire_config.n_peak_seasons)]
    
    scenarios = ["scenario" + str(i + 1) for i in range(empire_config.number_of_scenarios)]
    peak_seasons = ["peak" + str(i + 1) for i in range(empire_config.n_peak_seasons)]
    Season = empire_config.regular_seasons + peak_seasons
    Operationalhour = [i + 1 for i in range(FirstHoursOfPeakSeason[-1] + empire_config.len_peak_season - 1)]
    HoursOfRegSeason = [
        (s, h)
        for s in empire_config.regular_seasons
        for h in Operationalhour
        if h
        in list(
            range(
                empire_config.regular_seasons.index(s) * empire_config.length_of_regular_season + 1,
                empire_config.regular_seasons.index(s) * empire_config.length_of_regular_season + empire_config.length_of_regular_season + 1,
            )
        )
    ]
    HoursOfPeakSeason = [
        (s, h)
        for s in peak_seasons
        for h in Operationalhour
        if h
        in list(
            range(
                empire_config.length_of_regular_season * len(empire_config.regular_seasons) + peak_seasons.index(s) * empire_config.len_peak_season + 1,
                empire_config.length_of_regular_season * len(empire_config.regular_seasons) + peak_seasons.index(s) * empire_config.len_peak_season + empire_config.len_peak_season + 1,
            )
        )
    ]
    HoursOfSeason = HoursOfRegSeason + HoursOfPeakSeason

    operational_input_params = OperationalInputParams(
        Operationalhour=Operationalhour,
        scenarios=scenarios,
        Season=Season,
        HoursOfSeason=HoursOfSeason,
        FirstHoursOfRegSeason=FirstHoursOfRegSeason,
        FirstHoursOfPeakSeason=FirstHoursOfPeakSeason,
        lengthRegSeason=empire_config.length_of_regular_season,
        lengthPeakSeason=empire_config.len_peak_season,
    )

    return operational_input_params


def run_empire_model(
    empire_config: EmpireConfiguration,
    run_config: EmpireRunConfiguration,
    data_managers: list[IDataManager],
    test_run: bool,
    OUT_OF_SAMPLE: bool = False, 
    sample_file_path: Path | None = None
    ) -> None | float:
    for manager in data_managers:
        manager.apply()



    #############################
    ##Non configurable settings##
    #############################


    #######
    ##RUN##
    #######
    periods_active = [i + 1 for i in range(int((empire_config.forecast_horizon_year - 2020) / empire_config.leap_years_investment))]
    operational_input_params = define_operational_input_params(empire_config)


    with open(run_config.empire_path / "config/countries.json", "r", encoding="utf-8") as file:
        dict_countries = json.load(file)

    logger.info("++++++++")
    logger.info("+EMPIRE+")
    logger.info("++++++++")
    logger.info("Solver: %s", empire_config.optimization_solver)
    logger.info("Scenario Generation: %s", str(empire_config.use_scenario_generation))
    logger.info("++++++++")
    logger.info("ID: %s", run_config.run_name)
    logger.info("++++++++")

    if empire_config.use_scenario_generation:
        if empire_config.use_fixed_sample and not (run_config.scenario_data_path / "sampling_key.csv").exists():
            raise ValueError("Missing 'sampling_key.csv' in ScenarioData folder.")
        else:
            stochastic_data_path = run_config.dataset_path / "Stochastic"
            generate_random_scenario(
                empire_config=empire_config,
                dict_countries=dict_countries,
                scenario_data_path=run_config.scenario_data_path,
                output_path=stochastic_data_path,
            )

    else:
        if not empire_config.use_fixed_sample:
            logger.warning(
                "Both 'empire_config.use_scenario_generation' and 'use_fixed_sample' are set to False. "
                "Existing scenarios will be used, thus 'use_fixed_sample' should be True."
            )


    obj_value = None
    if not test_run:
        if not empire_config.benders_flag:
            obj_value, _ = run_empire(
                run_config=run_config,
                empire_config=empire_config,
                periods_active=periods_active,
                operational_input_params=operational_input_params,
                sample_file_path=sample_file_path,
                out_of_sample_flag=OUT_OF_SAMPLE,
            )
        else:
            obj_value, _ = run_benders(
                run_config=run_config,
                empire_config=empire_config,
                operational_input_params=operational_input_params,
                periods_active=periods_active,
            )


        
    config_path = run_config.dataset_path / "config.txt"
    logger.info("Writing config to: %s", config_path)
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(empire_config.to_dict(), file, ensure_ascii=False, indent=4)
    return obj_value

def setup_run_paths(
    version: str,
    empire_config: EmpireConfiguration,
    run_path: Path,
    empire_path: Path = Path.cwd(),
    input_data_dir: str = "input_data",
) -> EmpireRunConfiguration:
    """
    Setup run paths for Empire.

    :param version: dataset version.
    :param empire_config: Empire configuration.
    :param run_path: Path containing input and output to the empire run.
    :param empire_path: Path to empire project, optional.
    :return: Empire run configuration.
    """

    # Original dataset
    base_dataset = empire_path / input_data_dir / version

    # Input folders
    run_name = get_run_name(empire_config=empire_config, version=version)
    input_path = create_if_not_exist(run_path / "Input")
    input_data_path = create_if_not_exist(input_path / "csv")
    scenario_data_path = create_if_not_exist(input_data_path / "ScenarioData")


    copy_csv_dataset(base_dataset, input_data_path)

    copy_scenario_data(
        base_dataset=base_dataset,
        scenario_data_path=scenario_data_path,
        use_scenario_generation=empire_config.use_scenario_generation,
        use_fixed_sample=empire_config.use_fixed_sample,
    )

    # Output folders
    results_path = create_if_not_exist(run_path / "Output")

    return EmpireRunConfiguration(
        run_name=run_name,
        dataset_path=input_data_path,
        scenario_data_path=scenario_data_path,
        results_path=results_path,
        empire_path=empire_path,
    )


def runner(data_managers):
    ## Read config and setup folders ##
    version = "europe_v51"
    # version = "test"

    if version == "test":
        config = read_config_file(Path("config/testmyrun.yaml"))
    elif version == "europe_agg_v50":
        config = read_config_file(Path("config/aggrun.yaml"))
    else:
        config = read_config_file(Path("config/myrun.yaml"))

    empire_config = EmpireConfiguration.from_dict(config=config)

    run_config = setup_run_paths(version=version, empire_config=empire_config)

    ## Edit input data
    for manager in data_managers:
        manager.apply()

    ## Run empire
    run_empire_model(empire_config=empire_config, run_config=run_config)


if __name__ == "__main__":
    pass
