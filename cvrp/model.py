from itertools import combinations
from pyomo.environ import *
from pyomo.opt import SolverFactory, check_available_solvers

from cvrp.data import Network, Place


def compose_cvrp_model(network: Network):
    # Check if problem is solvable at all
    if sum(v.max_capacity for v in network.vehicles) < sum(c.demand for c in network.clients):
        raise ValueError("Problem not solvable: sum of vehicle capacities is lesser than sum of clients demands")

    model = ConcreteModel()

    # Sets definitons #####################################

    model.clients = Set(initialize=[p.slug_name for p in network.clients], doc="Clients")
    model.places = Set(initialize=[p.slug_name for p in network.all_places], doc="Depot and clients")
    model.vehicles = Set(initialize=[v.slug_name for v in network.vehicles], doc="Available vehicles")

    # Parameters definitons #####################################

    model.d = Param(
        model.places,
        initialize={p.slug_name: p.demand for p in network.all_places},
        doc="All places demands (including depot.demand=0)"
    )

    model.q = Param(
        model.vehicles,
        initialize={v.slug_name: v.max_capacity for v in network.vehicles},
        doc="Vehicle maximum capacities"
    )

    # flattened distance matrix in form: {(from, to): distance}
    distance_map = {}

    # NOTE: distances are assumed to be symmetrical,
    # meaning: dist(a, b) == dist(b, a)
    for p_a in network.all_places:
        for p_b in network.all_places:
            distance_map[(p_a.slug_name, p_b.slug_name)] = Place.distance(p_a, p_b)

    model.c = Param(
        model.places, model.places,
        initialize=distance_map,
        doc="Travel costs matrix"
    )

    # Variables definiton #####################################

    # noinspection PyUnresolvedReferences
    model.x = Var(
        model.places, model.places, model.vehicles,
        within=Binary,
        doc="1 if taken route from i-th to j-th place taken by k-th vehicle, 0 otherwise"
    )

    # Model objective function definiton #####################################

    def total_cost(mdl):
        return sum(
            mdl.c[i, j] * mdl.x[i, j, k]
            for i in mdl.places
            for j in mdl.places if j != i
            for k in mdl.vehicles
        )

    model.obj_total_cost = Objective(
        rule=total_cost, sense=minimize,
        doc="Minimize total cost of routes taken by vehicles"
    )

    # Model constraints definitons #####################################

    model.con_cl_vh_serve = ConstraintList(doc="Each client must be served by exactly one vehicle")

    for j in model.clients:
        model.con_cl_vh_serve.add(
            sum(model.x[i, j, k] for i in model.places for k in model.vehicles) == 1
        )

    model.con_vh_depot = ConstraintList(doc="Each vehicle must leave central depot exactly once")

    _dpt = network.depot.slug_name

    for k in model.vehicles:
        model.con_vh_depot.add(sum(model.x[_dpt, j, k] for j in model.clients) == 1)

    model.con_route_cycle = ConstraintList(
        doc="Sum of arrivals and departures must be equal for each vehicle (ergo: route must be a cycle)"
    )

    for k in model.vehicles:
        for j in model.places:
            model.con_route_cycle.add(
                sum(model.x[i, j, k] for i in model.places if i != j) ==
                sum(model.x[j, i, k] for i in model.places)
            )

    model.con_max_load = ConstraintList(
        doc="Each vehicle's total load must be lesser or equal its maximum capacity"
    )

    for k in model.vehicles:
        model.con_max_load.add(
            sum(model.d[j] * model.x[i, j, k] for i in model.places for j in model.clients if j != i) <= model.q[k]
        )

    clients_num = len(network.clients)

    model.con_subtours = ConstraintList(
        doc="Subtour elimination - ensures no cycles disconnected from depot"
    )

    for r in range(2, clients_num + 1):
        for s in combinations(model.clients, r):
            model.con_subtours.add(
                expr=sum(
                    model.x[i, j, k]
                    for i in s
                    for j in s if j != i
                    for k in model.vehicles
                ) <= len(s) - 1
            )

    return model


def solve_cvrp(network: Network, solvers_tried: [str] = None):

    # Supply default argument
    if not solvers_tried:
        solvers_tried = ["gurobi", "cplex", "glpk"]

    available_solvers = check_available_solvers(*solvers_tried)

    if len(available_solvers) == 0:
        raise EnvironmentError("No solvers available")

    # Get first available solver and solve the model
    solver = SolverFactory(available_solvers[0])
    model = compose_cvrp_model(network)

    result = solver.solve(model)

    return model, result


def cvrp_results(network: Network):
    # Solve the model for given network
    model, result = solve_cvrp(network)

    # Get depot name
    _depot = network.depot.slug_name

    raw_vars = [v for v in model.x if model.x[v].value > 0]

    vehicle_vars = {}

    # Categorize variables by vehicle (last slug name in index tuple)
    for place_from, place_to, vehicle in raw_vars:
        if vehicle not in vehicle_vars:
            vehicle_vars[vehicle] = []

        vehicle_vars[vehicle].append((place_from, place_to))

    # Order list of routes
    for vehicle, route_list in vehicle_vars.items():
        sorted_list = []

        last_from = _depot

        # Repeat until last appended route ends in depot (break cond inside loop)
        while True:
            # Find candidates (should always find exactly one continuation)
            next_candidates = [route for route in route_list if route[0] == last_from]

            if len(next_candidates) != 1:
                raise ValueError("Invalid amount of possible route continuations")

            # Continue last route
            next_route = next_candidates[0]

            # Append found route
            sorted_list.append(next_route)

            _, last_from = next_route

            # Route back to depot found
            if sorted_list[-1][1] == _depot:
                break

        vehicle_vars[vehicle] = sorted_list

    return vehicle_vars
