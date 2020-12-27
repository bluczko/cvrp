from slugify import slugify
from numpy import clip

from cvrp.exceptions import *
from cvrp.geo import geo_dist


class Place:
    __name: str
    __latitude: float
    __longitude: float
    __demand: float

    def __init__(self, name: str, lat: float, lon: float, demand: float = 0.0):
        self.name = name
        self.latitude = lat
        self.longitude = lon
        self.demand = demand

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Name can not be empty")

        self.__name = value

    @property
    def slug_name(self) -> str:
        return slugify(self.__name)

    @property
    def latitude(self) -> float:
        return self.__latitude

    @latitude.setter
    def latitude(self, value: float):
        # noinspection PyTypeChecker
        self.__latitude = float(clip(a=value, a_min=-180.0, a_max=180.0))

    @property
    def longitude(self) -> float:
        return self.__longitude

    @longitude.setter
    def longitude(self, value: float):
        # noinspection PyTypeChecker
        self.__longitude = float(clip(a=value, a_min=-90.0, a_max=90.0))

    @property
    def demand(self) -> float:
        return self.__demand

    @demand.setter
    def demand(self, value: float):
        self.__demand = max([0.0, value])

    @staticmethod
    def distance(a, b) -> float:
        if not isinstance(a, Place) or not isinstance(b, Place):
            raise ValueError("Both arguments must be instances of Place")

        if a == b:
            return 0.0

        return geo_dist(
            a.latitude, a.longitude,
            b.latitude, b.longitude
        )


class Vehicle:
    __name = ""
    __max_capacity = 0.0

    def __init__(self, name: str, max_capacity: float):
        self.name = name
        self.max_capacity = max_capacity

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Name can not be empty")

        self.__name = value

    @property
    def slug_name(self) -> str:
        return slugify(self.__name)

    @property
    def max_capacity(self) -> float:
        return self.__max_capacity

    @max_capacity.setter
    def max_capacity(self, value: float):
        self.__max_capacity = max([0.0, value])


class Network:
    def __init__(self):
        self.__depot = Place("Magazyn centralny", 0.0, 0.0)
        self.__clients = []
        self.__vehicles = []

    @property
    def depot(self) -> Place:
        return self.__depot

    @depot.setter
    def depot(self, value: Place):
        if not isinstance(value, Place):
            raise ValueError("Invalid depot")

        self.__depot = value

    @property
    def clients(self) -> [Place]:
        return self.__clients

    @property
    def all_places(self) -> [Place]:
        return [self.depot] + self.clients

    @property
    def vehicles(self) -> [Vehicle]:
        return self.__vehicles

    def add_client(self, client: Place):
        if client not in self.__clients and client is not self.__depot:
            self.__clients.append(client)

    def remove_client(self, client: Place):
        if client in self.__clients:
            self.__clients.remove(client)

    def add_vehicle(self, vehicle: Vehicle):
        if vehicle not in self.__vehicles:
            self.__vehicles.append(vehicle)

    def remove_vehicle(self, vehicle: Vehicle):
        if vehicle in self.__vehicles:
            self.__vehicles.remove(vehicle)

    def check_solvability(self):
        if len(self.clients) == 0:
            raise NoClientsException()

        if len(self.vehicles) == 0:
            raise NoVehiclesException()

        demands = [c.demand for c in self.clients]
        capacities = [v.max_capacity for v in self.vehicles]

        if sum(capacities) < sum(demands):
            raise SumCapacityOverloadException()

        if max(capacities) < max(demands):
            raise MaxCapacityOverloadException()

    def is_solvable(self):
        try:
            self.check_solvability()
        except CVRPException:
            return False

        return True
