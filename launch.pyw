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

        network.depot.latitude = random.randint(-180, 180),
        network.depot.longitude = random.randint(-90, 90),

        # Add clients
        for i in range(10):
            network.add_client(Place(
                name=f"Klient {i + 1}",
                lat=random.randint(-180, 180),
                lon=random.randint(-90, 90),
                demand=random.randint(6, 10)
            ))

        # Add vehicles
        for k in range(5):
            network.add_vehicle(Vehicle(
                name=f"Pojazd {string.ascii_uppercase[k]}",
                max_capacity=random.randint(18, 24)
            ))

    launch_ui(network)
