#!/usr/bin/env python
import json
import logging
from pathlib import Path

from empire.core.optimization.empire import run_empire
from empire.core.config import (EmpireConfiguration, read_config_file)

from empire.core.paths import setup_run_paths, PathsConfig
from empire.core.scenario_random import generate_random_scenario
from empire.input_data_manager import IDataManager
from empire.utils import copy_csv_dataset, load_json
from empire.core.benders.algorithm import run_benders
from empire.core.optimization.operational import OperationalInputParams


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


def stochastic_input_setup(empire_config: EmpireConfiguration, paths: PathsConfig):
        if empire_config.fixed_sampling_key_flag:
            assert (paths.scenario_data_path / "sampling_key.csv").exists(), "Missing 'sampling_key.csv' in ScenarioData folder."
        elif empire_config.fixed_csv_sample_flag:
            raise NotImplementedError("Fixed CSV sampling using .csv input data files not yet implemented.")
        else:
            stochastic_data_path = paths.dataset_path / "Stochastic"
            dict_countries = load_json(paths.empire_path / "config/countries.json")
            generate_random_scenario(
                empire_config=empire_config,
                dict_countries=dict_countries,
                scenario_data_path=paths.scenario_data_path,
                output_path=stochastic_data_path,
            )

def run_empire_model(
    empire_config: EmpireConfiguration,
    paths: PathsConfig,
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

 
    logger.info("++++++++")
    logger.info("+EMPIRE+")
    logger.info("++++++++")
    logger.info("Solver: %s", empire_config.optimization_solver)
    logger.info("Fixed sample: %s", str(empire_config.fixed_sampling_key_flag))
    logger.info("++++++++")
    logger.info("ID: %s", paths.run_name)
    logger.info("++++++++")

    
    stochastic_input_setup(empire_config, paths)


    obj_value = None
    if not test_run:
        if not empire_config.benders_flag:
            obj_value, _ = run_empire(
                paths=paths,
                empire_config=empire_config,
                periods_active=periods_active,
                operational_input_params=operational_input_params,
                sample_file_path=sample_file_path,
                out_of_sample_flag=OUT_OF_SAMPLE,
            )
        else:
            obj_value, _ = run_benders(
                paths=paths,
                empire_config=empire_config,
                operational_input_params=operational_input_params,
                periods_active=periods_active,
            )


        
    config_path = paths.dataset_path / "config.txt"
    logger.info("Writing config to: %s", config_path)
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(empire_config.to_dict(), file, ensure_ascii=False, indent=4)
    return obj_value



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
    paths = setup_run_paths(version=version, empire_config=empire_config)

    # Copy base dataset to inputs.input_data_path 
    base_dataset = "input_data" / version
    copy_csv_dataset(base_dataset, paths.dataset_path) 
    

    ## Edit input data
    for manager in data_managers:
        manager.apply()

    ## Run empire
    run_empire_model(empire_config=empire_config, paths=paths)


if __name__ == "__main__":
    pass
