from itertools import combinations
from pyomo.environ import *

from cvrp.data import Network, Place


class CVRPModel(ConcreteModel):
    def __init__(self, network: Network, auto_init=True):
        super(CVRPModel, self).__init__()
        self.network = network

        if auto_init:
            self.init_data()

    def init_data(self):
        self._init_sets()
        self._init_parameters()
        self._init_variables()
        self._init_constraints()
        self._init_objective()

    def _init_sets(self):
        self.clients = Set(initialize=[p.slug_name for p in self.network.clients], doc="Clients")
        self.places = Set(initialize=[p.slug_name for p in self.network.all_places], doc="Depot and clients")
        self.vehicles = Set(initialize=[v.slug_name for v in self.network.vehicles], doc="Available vehicles")

    def _init_parameters(self):
        self.d = Param(
            self.places,
            initialize={p.slug_name: p.demand for p in self.network.all_places},
            doc="All places demands (including depot.demand=0)"
        )

        self.q = Param(
            self.vehicles,
            initialize={v.slug_name: v.max_capacity for v in self.network.vehicles},
            doc="Vehicle maximum capacities"
        )

        # flattened distance matrix in form: {(from, to): distance}
        dist_map = {}

        # NOTE: distances are assumed to be symmetrical,
        # meaning: dist(a, b) == dist(b, a)
        for p_a in self.network.all_places:
            i = p_a.slug_name

            for p_b in self.network.all_places:
                j = p_b.slug_name

                dist_map[(i, j)] = Place.distance(p_a, p_b)

        self.c = Param(
            self.places, self.places,
            initialize=dist_map,
            doc="Travel costs matrix"
        )

    def _init_variables(self):
        # noinspection PyUnresolvedReferences
        self.x = Var(
            self.places, self.places, self.vehicles,
            within=Binary,
            doc="1 if taken route from i-th to j-th place taken by k-th vehicle, 0 otherwise"
        )

    def _init_objective(self):
        self.obj_total_cost = Objective(
            sense=minimize,
            expr=sum(
                self.c[i, j] * self.x[i, j, k]
                for i in self.places
                for j in self.places if j != i
                for k in self.vehicles
            ),
            doc="Minimize total cost of routes taken by vehicles"
        )

    def _init_constraints(self):
        self.con_cl_vh_serve = ConstraintList(doc="Each client must be served by exactly one vehicle")

        for j in self.clients:
            self.con_cl_vh_serve.add(
                sum(
                    self.x[i, j, k]
                    for i in self.places
                    for k in self.vehicles
                ) == 1
            )

        self.con_vh_depot = ConstraintList(doc="Each vehicle must leave central depot exactly once")

        _dpt = self.network.depot.slug_name

        for k in self.vehicles:
            self.con_vh_depot.add(
                sum(
                    self.x[_dpt, j, k]
                    for j in self.clients
                ) == 1
            )

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
                sum(
                    self.d[j] * self.x[i, j, k]
                    for i in self.places
                    for j in self.clients if j != i
                ) <= self.q[k]
            )

        clients_num = len(self.network.clients)

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

    def vehicle_routes(self):
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
