from ratiss_topological_decoherence.tsp import inspection_route


def test_exact_route_is_closed_and_reports_exact_method():
    coordinates = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    route = inspection_route(coordinates, [0, 1, 2, 3])
    assert route["method"] == "held_karp_exact"
    assert route["path"][0] == route["path"][-1]
    assert set(route["path"][:-1]) == {0, 1, 2, 3}
