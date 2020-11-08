import pytest
from cvrp.geo import geo_dist


def test_geo_dist():
    loc_a = (50.0559, 5.4253)
    loc_b = (58.3838, 3.0412)

    dist = geo_dist(*loc_a, *loc_b)

    assert dist == pytest.approx(938.74, 3)
