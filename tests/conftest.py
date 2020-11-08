from math import ceil

import pytest
import random
from faker import Faker

from cvrp.data import Place, Vehicle, Network


fake = Faker()


@pytest.fixture
def client_place():
    return Place(
        name=f"{fake.company()} at {fake.street_address()}",
        lat=fake.latitude(),
        lon=fake.longitude(),
        demand=random.randrange(20, 30)
    )


@pytest.fixture
def depot_place():
    return Place(
        name="Central depot",
        lat=fake.latitude(),
        lon=fake.longitude()
    )


@pytest.fixture
def vehicle():
    return Vehicle(
        name=f"Vehicle {fake.license_plate()}",
        max_capacity=random.choice([30, 35])
    )


@pytest.fixture
def network():
    net = Network()

    net.depot = Place(
        name="Central Depot",
        lat=fake.latitude(),
        lon=fake.longitude()
    )

    num_clients = 8

    for i in range(num_clients):
        net.add_client(Place(
            name=fake.city(),
            lat=fake.latitude(),
            lon=fake.longitude(),
            demand=20 + 5 * (i % 2)
        ))

    num_vehicles = 4

    for i in range(num_vehicles):
        net.add_vehicle(Vehicle(
            name=fake.license_plate(),
            max_capacity=(30 + 5 * (i % 2)) * (num_clients // num_vehicles)
        ))

    return net
