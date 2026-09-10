import numpy as np

from ratiss_topological_decoherence.topology import rips_persistence


def test_rips_detects_a_finite_h1_cycle_before_triangles_fill_it():
    # Square: side edges at 1, diagonals at sqrt(2). The cycle is born at 1
    # and filled by triangles when the diagonal becomes available.
    distance = np.array(
        [
            [0.0, 1.0, np.sqrt(2), 1.0],
            [1.0, 0.0, 1.0, np.sqrt(2)],
            [np.sqrt(2), 1.0, 0.0, 1.0],
            [1.0, np.sqrt(2), 1.0, 0.0],
        ]
    )
    outcome = rips_persistence(distance, max_edge=2.0)
    assert outcome["psig"] > 0.3
    assert outcome["n_finite_h1"] >= 1
