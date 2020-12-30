from pyomo.opt import check_available_solvers, SolverFactory

from cvrp.exceptions import CVRPException
from cvrp.model import CVRPModel, check_optimal_termination


def get_solvers(solvers_tried: [str] = None):
    if not solvers_tried:
        solvers_tried = ["gurobi", "cplex", "glpk"]

    available_solvers = check_available_solvers(*solvers_tried)

    if len(available_solvers) == 0:
        raise EnvironmentError("No solvers available")

    return available_solvers


def solve_model(model: CVRPModel, solvers_tried: [str] = None):
    available_solvers = get_solvers(solvers_tried)
    solver = SolverFactory(available_solvers[0])
    result = solver.solve(model)

    if not check_optimal_termination(result):
        raise CVRPException()

    return result
