from itertools import combinations
from pyomo.environ import *
from pyomo.opt import SolverFactory, check_available_solvers

from cvrp.data import Network, Place


class CVRPModel(ConcreteModel):
    def __init__(self, network: Network):
        super(CVRPModel, self).__init__()

        self.network = network

        network.check_solvability()
        
        # Sets definitons #####################################

        self.clients = Set(initialize=[p.slug_name for p in network.clients], doc="Clients")
        self.places = Set(initialize=[p.slug_name for p in network.all_places], doc="Depot and clients")
        self.vehicles = Set(initialize=[v.slug_name for v in network.vehicles], doc="Available vehicles")

        # Parameters definitons #####################################

        self.d = Param(
            self.places,
            initialize={p.slug_name: p.demand for p in network.all_places},
            doc="All places demands (including depot.demand=0)"
        )

        self.q = Param(
            self.vehicles,
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

        self.c = Param(
            self.places, self.places,
            initialize=distance_map,
            doc="Travel costs matrix"
        )

        # Variables definiton #####################################

        # noinspection PyUnresolvedReferences
        self.x = Var(
            self.places, self.places, self.vehicles,
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

        self.obj_total_cost = Objective(
            rule=total_cost, sense=minimize,
            doc="Minimize total cost of routes taken by vehicles"
        )

        # Model constraints definitons #####################################

        self.con_cl_vh_serve = ConstraintList(doc="Each client must be served by exactly one vehicle")

        for j in self.clients:
            self.con_cl_vh_serve.add(
                sum(self.x[i, j, k] for i in self.places for k in self.vehicles) == 1
            )

        self.con_vh_depot = ConstraintList(doc="Each vehicle must leave central depot exactly once")

        _dpt = network.depot.slug_name

        for k in self.vehicles:
            self.con_vh_depot.add(sum(self.x[_dpt, j, k] for j in self.clients) == 1)

        self.con_route_cycle = ConstraintList(
            doc="Sum of arrivals and departures must be equal for each vehicle (ergo: route must be a cycle)"
        )

        for k in self.vehicles:
            for j in self.places:
                self.con_route_cycle.add(
                    sum(self.x[i, j, k] for i in self.places if i != j) ==
                    sum(self.x[j, i, k] for i in self.places)
                )

        self.con_max_load = ConstraintList(
            doc="Each vehicle's total load must be lesser or equal its maximum capacity"
        )

        for k in self.vehicles:
            self.con_max_load.add(
                sum(self.d[j] * self.x[i, j, k] for i in self.places for j in self.clients if j != i) <= self.q[k]
            )

        clients_num = len(network.clients)

        self.con_subtours = ConstraintList(
            doc="Subtour elimination - ensures no cycles disconnected from depot"
        )

        for r in range(2, clients_num + 1):
            for s in combinations(self.clients, r):
                self.con_subtours.add(
                    expr=sum(
                        self.x[i, j, k]
                        for i in s
                        for j in s if j != i
                        for k in self.vehicles
                    ) <= len(s) - 1
                )

    def results(self):
        # Get depot name
        _depot = self.network.depot.slug_name

        raw_vars = [v for v in self.x if self.x[v].value > 0]

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


def get_solvers(solvers_tried: [str] = None):
    # Supply default argument
    if not solvers_tried:
        solvers_tried = ["gurobi", "cplex", "glpk"]

    available_solvers = check_available_solvers(*solvers_tried)

    if len(available_solvers) == 0:
        raise EnvironmentError("No solvers available")

    return available_solvers


def solve(model: CVRPModel, solvers_tried: [str] = None):
    available_solvers = get_solvers(solvers_tried)
    solver = SolverFactory(available_solvers[0])
    return solver.solve(model)
