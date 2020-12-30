import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt

from pyhtml import *

from pyomo.opt.results import SolverResults, check_optimal_termination

from cvrp.model import CVRPModel
from cvrp.solver import get_solvers


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

        for i, place in enumerate(ctx.get("network").all_places):
            h = "E" if place.longitude > 0 else "W"
            v = "N" if place.latitude > 0 else "S"

            yield tr(
                td(strong(place.name) if place is depot else place.name),
                td("-" if place is depot else place.demand),
                td(f"{abs(place.longitude):.4f} {h}, {abs(place.latitude):.4f} {v}")
            )

    # noinspection PyUnresolvedReferences
    def vehicle_rows(ctx):
        for i, vehicle in enumerate(ctx.get("network").vehicles):
            yield tr(
                td(vehicle.name),
                td(vehicle.max_capacity),
            )

    # noinspection PyUnresolvedReferences
    def route_vehicles(ctx):
        network = ctx.get("network")
        routes = ctx.get("routes")

        for vehicle in network.vehicles:
            place_names = ["Wyjazd z magazynu"]

            for vehicle_route in routes[vehicle.slug_name]:
                place = network.get_place(vehicle_route[1])
                place_names.append("Powrót do magazynu" if place is network.depot else place.name)

            yield div(h2(vehicle.name + ":"), ol(*[li(name) for name in place_names]))

    body_sections = [
        section(
            h2("Dane wejściowe"),
            div(
                h3("Miejsca"),
                table(
                    thead(td("Nazwa"), td("Zapotrzebowanie"), td("Położenie geo.")),
                    tbody(place_rows)
                )
            ),
            div(
                h3("Pojazdy"),
                table(
                    thead(td("Nazwa"), td("Maks. pojemność")),
                    tbody(vehicle_rows)
                )
            ),
        )
    ]

    if check_optimal_termination(result):
        body_sections.append(
            section(
                h2("Wybrane trasy"),
                div(route_vehicles)
            )
        )

        body_sections.append(
            section(
                h2("Wizualizacja"),
                lambda ctx: img(src=generate_network_vis(ctx.get("network"), ctx.get("routes")))
            )
        )

    body_sections.append(
        section(
            h2("Solver"),
            div(table(tbody(
                tr(td(strong("Użyty solver:")), td(get_solvers()[0])),
                tr(td(strong("Czas rozwiązywania:")), td(result.solver.time)),
                tr(td(strong("Status:")), td(str(result.solver.status))),
                tr(td(strong("Stan zakończenia:")), td(str(result.solver.termination_condition))),
                tr(td(strong("Kod zwrotny:")), td(str(result.solver.return_code))),
                tr(td(strong("Wiadomość:")), td(str(result.solver.message))),
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
            title("Problem marszrutyzacji - Raport"),
            style(
                "table, th, td { border: 1px solid black; border-collapse: collapse; }" +
                "section { margin-left: 2em; }"
            ),
        ),
        body(
            header(h1("Raport marszrutyzacji")),
            *body_sections,
            footer(hr, f"Wygenerowano: {datetime.now()}"),
        ),
    )

    return template.render(
        network=model.network,
        routes=model.vehicle_routes(),
        result=result
    )
