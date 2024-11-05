import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt

from pyhtml import *

from pyomo.opt.results import SolverResults, check_optimal_termination

from cvrp.model import CVRPModel
from cvrp.solver import get_solvers
from cvrp.data import Place


def generate_network_vis(network, routes):
    plt.figure(figsize=(8, 8))
    plt.axis("off")

    # Draw edges
    for p_a in network.all_places:
        for p_b in network.all_places:
            if p_a == p_b:
                continue

            lon = [p_a.longitude, p_b.longitude]
            lat = [p_a.latitude, p_b.latitude]

            plt.plot(lon, lat, color="grey", linewidth=0.5, alpha=0.33)

    # Draw selected routes
    for vehicle_slug, route in routes.items():
        vehicle = network.get_vehicle(vehicle_slug)

        lon = [network.depot.longitude]
        lat = [network.depot.latitude]

        for src_slug, dest_slug in route:
            dest = network.get_place(dest_slug)
            lon += [dest.longitude]
            lat += [dest.latitude]

        plt.plot(lon, lat, label=vehicle.name)

    # Draw place vertices
    longitudes = [place.longitude for place in network.all_places]
    latitudes = [place.latitude for place in network.all_places]

    plt.scatter(longitudes, latitudes, color="yellow")

    for place in network.all_places:
        plt.annotate(place.name, (place.longitude, place.latitude))

    # Save figure to bytes stream
    io_bytes = io.BytesIO()
    plt.savefig(io_bytes, format="png")
    io_bytes.seek(0)

    # Encode as base64 image
    return "data:image/png;base64," + base64.b64encode(io_bytes.read()).decode("utf-8").replace("\n", "")


# noinspection PyUnresolvedReferences
def generate_report(model: CVRPModel, result: SolverResults):

    # noinspection PyUnresolvedReferences
    def place_rows(ctx):
        depot = ctx.get("network").depot
        demand_sum = 0

        for i, place in enumerate(ctx.get("network").all_places):
            h = "E" if place.longitude > 0 else "W"
            v = "N" if place.latitude > 0 else "S"

            demand_sum += place.demand

            yield tr(
                td(strong(place.name) if place is depot else place.name),
                td("-" if place is depot else place.demand),
                td(f"{abs(place.longitude):.2f} {h}, {abs(place.latitude):.2f} {v}")
            )

        yield tr(
            td(strong("TOTAL")),
            td(f"{demand_sum:.2f}"),
            td("-")
        )

    # noinspection PyUnresolvedReferences
    def vehicle_rows(ctx):
        max_cap_sum = 0

        for i, vehicle in enumerate(ctx.get("network").vehicles):
            max_cap_sum += vehicle.max_capacity

            yield tr(
                td(vehicle.name),
                td(vehicle.max_capacity),
            )

        yield tr(
            td(strong("TOTAL")),
            td(f"{max_cap_sum:.2f}")
        )

    # noinspection PyUnresolvedReferences
    def route_vehicles(ctx):
        network = ctx.get("network")
        routes = ctx.get("routes")

        for vehicle in network.vehicles:
            place_names = ["Departure from depot"]
            vehicle_distance = 0

            for vehicle_route in routes[vehicle.slug_name]:
                place_from = network.get_place(vehicle_route[0])
                place_dest = network.get_place(vehicle_route[1])

                route_name = place_dest.name

                if place_dest is network.depot:
                    route_name = "Return to depot"

                distance = Place.distance(place_from, place_dest)
                vehicle_distance += distance

                place_names.append(f"{route_name} (+ {distance:.2f} km)")

            yield div(
                h2(f"{vehicle.name} ({vehicle_distance:.2f} km)"),
                ol(*[li(name) for name in place_names]),
            )

    body_sections = [
        section(
            h2("Input Data"),
            div(
                h3("Places"),
                table(
                    thead(td("Name"), td("Demand"), td("Geo Position")),
                    tbody(place_rows)
                )
            ),
            div(
                h3("Vehicles"),
                table(
                    thead(td("Name"), td("Max Capacity")),
                    tbody(vehicle_rows)
                )
            ),
        )
    ]

    if check_optimal_termination(result):
        body_sections.append(
            section(
                h2("Selected Routes"),
                div(route_vehicles),
                p(strong("Total Distance Covered: "), span(f"{model.obj_total_cost():.2f} km"))
            )
        )

        body_sections.append(
            section(
                h2("Visualization"),
                lambda ctx: img(src=generate_network_vis(ctx.get("network"), ctx.get("routes")))
            )
        )

    body_sections.append(
        section(
            h2("Solver"),
            div(table(tbody(
                tr(td(strong("Used Solver:")), td(get_solvers()[0])),
                tr(td(strong("Solve Time:")), td(result.solver.time)),
                tr(td(strong("Status:")), td(str(result.solver.status))),
                tr(td(strong("Termination Condition:")), td(str(result.solver.termination_condition))),
                tr(td(strong("Return Code:")), td(str(result.solver.return_code))),
                tr(td(strong("Message:")), td(str(result.solver.message))),
            ))),
            h2("Problem"),
            div(table(tbody(*[
                tr(td(p(strong(k + ":")), td(v.value)))
                for k, v in result.problem[0].items()
            ])))
        )
    )

    template = html(
        head(
            title("Route Planning - Report"),
            style(
                "table, th, td { border: 1px solid black; border-collapse: collapse; }" +
                "section { margin-left: 2em; }"
            ),
        ),
        body(
            header(h1("Route Planning Report")),
            *body_sections,
            footer(hr, f"Generated: {datetime.now()}"),
        ),
    )

    return template.render(
        network=model.network,
        routes=model.vehicle_routes(),
        result=result
    )
