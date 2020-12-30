from cvrp.model import CVRPModel


def test_compose_cvrp_model(network):
    """
    Checks if compose_cvrp_model returns a valid Pyomo model of type ConcreteModel
    """

    model = CVRPModel(network)
    assert isinstance(model, CVRPModel), \
        "compose_cvrp_model should return instance of CVRPModel"
