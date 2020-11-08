from numpy import sin, cos, sqrt, power, arctan2, deg2rad

# Approximate mean earth radius
EARTH_RADIUS = 6.371E+3


def geo_dist(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    """
    Geographic distance calculated using Haversine formula.

    Implementation translated from JS code as seen on:
    https://www.movable-type.co.uk/scripts/latlong.html

    :param lat_a: First latitude
    :param lon_a: First longitude
    :param lat_b: Second latitude
    :param lon_b: Second longitude
    :returns:
    """

    fi_a = deg2rad(float(lat_a))
    fi_b = deg2rad(float(lat_b))

    d_fi = deg2rad(lat_b - lat_a) * 0.5  # delta fi
    d_lm = deg2rad(lon_b - lon_a) * 0.5  # delta lambda

    d_fi_sq, d_lm_sq = power(sin(d_fi), 2), power(sin(d_lm), 2)  # sin squared

    a = d_fi_sq + cos(fi_a) * cos(fi_b) * d_lm_sq

    c = 2 * arctan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS * c
