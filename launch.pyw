from math import ceil

from environ import Env

from cvrp.ui.main import launch_ui


if __name__ == "__main__":
    env = Env()

    network = None

    if env.bool("DEBUG", False):
        from cvrp.data import Network, Place, Vehicle
        from numpy import random
        import string

        network = Network()

        random.seed(42)

        network.depot.latitude = 52,
        network.depot.longitude = 20,

        num_clients = 10
        avg_cl_per_vh = 4
        d_min, d_max = 6, 12

        # Add clients
        for i in range(num_clients):
            network.add_client(Place(
                name=f"Klient {i + 1}",
                lat=random.randint(4900, 5400) / 100,
                lon=random.randint(1500, 2300) / 100,
                demand=random.randint(d_min * 100, d_max * 100) / 100
            ))

        num_vehicles = ceil(num_clients / avg_cl_per_vh)
        c_min, c_max = d_min * avg_cl_per_vh, d_max * avg_cl_per_vh

        # Add vehicles
        for k in range(num_vehicles):
            network.add_vehicle(Vehicle(
                name=f"Pojazd {string.ascii_uppercase[k]}",
                max_capacity=random.randint(c_min * 10, c_max * 10) / 10
            ))

    launch_ui(network)
