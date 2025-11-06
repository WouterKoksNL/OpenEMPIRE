
from dataclasses import dataclass

@dataclass
class OperationalInputParams: 
    Operationalhour: list[int]
    scenarios: list[str]
    gas_scenarios: list[str]
    Season: list[str]
    HoursOfSeason: list[tuple[str, int]]
    FirstHoursOfRegSeason: list[int]
    FirstHoursOfPeakSeason: list[int]
    length_reg_season: int
    length_peak_season: int
