from pprint import pprint

import pytest

from pyomo.core import ConcreteModel
from pyomo.opt import check_optimal_termination

from cvrp.data import Place
from cvrp.exceptions import CVRPException
from cvrp.model import CVRPModel, solve


def test_compose_cvrp_model(network):
    """
    Checks if compose_cvrp_model returns a valid Pyomo model of type ConcreteModel
    """

    model = CVRPModel(network)
    assert isinstance(model, ConcreteModel), \
        "compose_cvrp_model should return instance of ConcreteModel"


def test_unsolvable_model(network):
    """
    Checks if compose_cvrp_model raises exception, when user tries to solve logically impossible problem.
    """

    overdemanding_clients = [Place(f"whatever-{i}", 0.0, 0.0, 10000) for i in range(3)]

    for client in overdemanding_clients:
        network.add_client(client)

    with pytest.raises(CVRPException):
        CVRPModel(network)


def test_solve_cvrp_optimal(network):
    """
    Checks if solved model returns optimal solution flag.
    """

    result = solve(CVRPModel(network))
    assert check_optimal_termination(result), \
        "solve_cvrp should return optimal results for example network"


def test_solve_cvrp_sanity(network):
    """
    Checks if solved model returns logical and practically executable solution.
    """

    model = CVRPModel(network)
    result = solve(model)

    _depot = network.depot.slug_name

    # Is every place visited?
    all_places = [c.slug_name for c in network.all_places]
    visited_places = [v[1] for v in model.x]

    assert set(visited_places) == set(all_places), \
        "Every place should be visited"

    # Is vehicle capacity limit satisfied?
    for vehicle in network.vehicles:
        load = sum(p.demand for p in network.clients if p.slug_name in network.clients)

        assert load <= vehicle.max_capacity, \
            "Every vehicle should have load less or equal its max capacity"


def test_cvrp_results(network):
    """
    Checks if cvrp_results returns valid dict structure containing vehicle routes.
    """

    model = CVRPModel(network)

    solve(model)

    vehicle_vars = model.results()

    for vehicle in network.vehicles:
        assert vehicle.slug_name in vehicle_vars, \
            f"Vehicle {vehicle} should be in vehicle_vars"

    pprint(vehicle_vars)
