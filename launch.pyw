from math import ceil
from environ import Env
from cvrp.ui.main import launch_ui

if __name__ == "__main__":
    env = Env()
    network = None

    # If in debug mode, generate random data for testing
    if env.bool("DEBUG", False):
        from cvrp.data import Network, Place, Vehicle
        from numpy import random
        import string

        network = Network()
        random.seed(42)

        # Set the depot's location
        network.depot.latitude = 52
        network.depot.longitude = 20

        # Parameters for generating clients and vehicles
        num_clients = 10               # Number of clients
        avg_cl_per_vh = 4              # Average clients per vehicle
        d_min, d_max = 6, 12           # Minimum and maximum demand for clients

        # Add clients
        for i in range(num_clients):
            network.add_client(Place(
                name=f"Client {i + 1}",
                lat=random.randint(4900, 5400) / 100,  # Random latitude
                lon=random.randint(1500, 2300) / 100,  # Random longitude
                demand=random.randint(d_min * 100, d_max * 100) / 100  # Random demand
            ))

        # Determine the number of vehicles needed
        num_vehicles = ceil(num_clients / avg_cl_per_vh)
        c_min, c_max = d_min * avg_cl_per_vh, d_max * avg_cl_per_vh  # Min and max vehicle capacity

        # Add vehicles
        for k in range(num_vehicles):
            network.add_vehicle(Vehicle(
                name=f"Vehicle {string.ascii_uppercase[k]}",  # Assign vehicle name as a letter
                max_capacity=random.randint(c_min * 10, c_max * 10) / 10  # Random max capacity
            ))

    # Launch the UI with the generated network (if in debug mode)
    launch_ui(network)
