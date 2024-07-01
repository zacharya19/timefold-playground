from typing import Generator
from datetime import date, datetime, time, timedelta
from enum import Enum
from random import Random
from dataclasses import dataclass

from .domain import *


FIRST_NAMES = ("Amy", "Beth", "Chad", "Dan", "Elsa", "Flo", "Gus", "Hugo", "Ivy", "Jay")
LAST_NAMES = ("Cole", "Fox", "Green", "Jones", "King", "Li", "Poe", "Rye", "Smith", "Watt")


@dataclass
class _DemoDataProperties:
    seed: int
    visit_count: int
    technician_count: int
    min_demand: int
    max_demand: int
    min_technician_capacity: int
    max_technician_capacity: int
    south_west_corner: Location
    north_east_corner: Location

    def __post_init__(self):
        if self.min_demand < 1:
            raise ValueError(f"minDemand ({self.min_demand}) must be greater than zero.")
        if self.max_demand < 1:
            raise ValueError(f"maxDemand ({self.max_demand}) must be greater than zero.")
        if self.min_demand >= self.max_demand:
            raise ValueError(f"maxDemand ({self.max_demand}) must be greater than minDemand ({self.min_demand}).")
        if self.min_technician_capacity < 1:
            raise ValueError(f"Number of mintechnicianCapacity ({self.min_technician_capacity}) must be greater than zero.")
        if self.max_technician_capacity < 1:
            raise ValueError(f"Number of maxtechnicianCapacity ({self.max_technician_capacity}) must be greater than zero.")
        if self.min_technician_capacity >= self.max_technician_capacity:
            raise ValueError(f"maxtechnicianCapacity ({self.max_technician_capacity}) must be greater than "
                             f"mintechnicianCapacity ({self.min_technician_capacity}).")
        if self.visit_count < 1:
            raise ValueError(f"Number of visitCount ({self.visit_count}) must be greater than zero.")
        if self.technician_count < 1:
            raise ValueError(f"Number of technicianCount ({self.technician_count}) must be greater than zero.")
        if self.north_east_corner.latitude <= self.south_west_corner.latitude:
            raise ValueError(f"northEastCorner.getLatitude ({self.north_east_corner.latitude}) must be greater than "
                             f"southWestCorner.getLatitude({self.south_west_corner.latitude}).")
        if self.north_east_corner.longitude <= self.south_west_corner.longitude:
            raise ValueError(f"northEastCorner.getLongitude ({self.north_east_corner.longitude}) must be greater than "
                             f"southWestCorner.getLongitude({self.south_west_corner.longitude}).")


class DemoData(Enum):
    SYDNEY = _DemoDataProperties(3, 85, 7, 1, 3, 25, 50,
                                 Location(latitude=-33.868820, longitude=151.209296),
                                 Location(latitude=-33.700001, longitude=151.300003))

    MELBOURNE = _DemoDataProperties(4, 78, 8, 2, 4, 30, 60,
                                    Location(latitude=-37.813629, longitude=144.963058),
                                    Location(latitude=-37.500000, longitude=145.000000))

    BRISBANE = _DemoDataProperties(5, 70, 5, 1, 2, 20, 40,
                                   Location(latitude=-27.469770, longitude=153.025124),
                                   Location(latitude=-27.200000, longitude=153.100006))


def doubles(random: Random, start: float, end: float) -> Generator[float, None, None]:
    while True:
        yield random.uniform(start, end)


def ints(random: Random, start: int, end: int) -> Generator[int, None, None]:
    while True:
        yield random.randrange(start, end)


def generate_names(random: Random) -> Generator[str, None, None]:
    while True:
        yield f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'


def generate_demo_data(demo_data_enum: DemoData) -> TechnicianRoutePlan:
    name = "demo"
    demo_data = demo_data_enum.value
    random = Random(demo_data.seed)
    latitudes = doubles(random, demo_data.south_west_corner.latitude, demo_data.north_east_corner.latitude)
    longitudes = doubles(random, demo_data.south_west_corner.longitude, demo_data.north_east_corner.longitude)

    demands = ints(random, demo_data.min_demand, demo_data.max_demand + 1)
    technician_capacities = ints(random, demo_data.min_technician_capacity,
                              demo_data.max_technician_capacity + 1)

    technicians = [Technician(id=str(i),
                        capacity=next(technician_capacities),
                        home_location=Location(
                            latitude=next(latitudes),
                            longitude=next(longitudes)))
                for i in range(demo_data.technician_count)]

    names = generate_names(random)
    visits = [
        Visit(
             id=str(i),
             name=next(names),
             location=Location(latitude=next(latitudes), longitude=next(longitudes)),
             demand=next(demands)
         ) for i in range(demo_data.visit_count)
    ]

    return TechnicianRoutePlan(name=name,
                            south_west_corner=demo_data.south_west_corner,
                            north_east_corner=demo_data.north_east_corner,
                            technicians=technicians,
                            visits=visits)


def tomorrow_at(local_time: time) -> datetime:
    return datetime.combine(date.today(), local_time)
