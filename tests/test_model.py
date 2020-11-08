import pytest

from pyomo.core import ConcreteModel
from pyomo.opt import check_optimal_termination

from cvrp.data import Place
from cvrp.model import compose_cvrp_model, solve_cvrp, cvrp_results


def test_compose_cvrp_model(network):
    model = compose_cvrp_model(network)
    assert isinstance(model, ConcreteModel), \
        "compose_cvrp_model should return instance of ConcreteModel"


def test_unsolvable_model(network):
    overdemanding_clients = [Place(f"whatever-{i}", 0.0, 0.0, 10000) for i in range(3)]

    for client in overdemanding_clients:
        network.add_client(client)

    with pytest.raises(ValueError):
        compose_cvrp_model(network)


def test_solve_cvrp(network):
    model, result = solve_cvrp(network)
    assert check_optimal_termination(result), \
        "solve_cvrp should return optimal results for network"


def test_cvrp_results(network):
    vehicle_vars = cvrp_results(network)

    for vehicle in network.vehicles:
        assert vehicle.slug_name in vehicle_vars, \
            f"Vehicle {vehicle} should be in vehicle_vars"
