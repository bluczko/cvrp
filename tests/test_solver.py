from pyomo.opt import check_optimal_termination

from cvrp.model import CVRPModel
from cvrp.solver import solve_model


def test_solve_cvrp_optimal(network):
    """
    Checks if solved model returns optimal solution flag.
    """

    model = CVRPModel(network)
    result = solve_model(model)

    assert check_optimal_termination(result), \
        "solve_cvrp should return optimal results for example network"


def test_solve_cvrp_sanity(network):
    """
    Checks if solved model returns logical and practically executable solution.
    """

    model = CVRPModel(network)
    solve_model(model)

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

    solve_model(model)

    vehicle_vars = model.vehicle_routes()

    for vehicle in network.vehicles:
        assert vehicle.slug_name in vehicle_vars, \
            f"Vehicle {vehicle} should be in vehicle_vars"
