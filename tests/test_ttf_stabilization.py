import numpy as np

from ratiss_topological_decoherence.simulation import run_local_demo
from ratiss_topological_decoherence.ttf_stabilization import SmoothStabilizationConfig, apply_smooth_regularization, correlation_variation, run_ttf_smooth_ablation, variation_boundary


def test_variation_boundary_and_smooth_profile_are_bounded_and_symmetric():
    previous = np.eye(3)
    current = np.array([[1.0, 0.1, 0.0], [0.1, 1.0, 0.7], [0.0, 0.7, 1.0]])
    settings = SmoothStabilizationConfig(variation_threshold=0.05, strength=0.3)
    variation = correlation_variation(current, previous)
    boundary = variation_boundary(variation, settings)
    regularized, activation = apply_smooth_regularization(current, variation, settings)
    assert boundary == [1, 2, 0]
    assert np.allclose(regularized, regularized.T)
    assert np.allclose(np.diag(regularized), 1.0)
    assert np.all((regularized >= 0) & (regularized <= 1))
    assert np.all((activation >= 0) & (activation <= 1))


def test_ablation_exports_separate_baseline_and_regularized_timelines_with_targeted_tsp():
    baseline, regularized = run_ttf_smooth_ablation(run_local_demo())
    assert baseline["provenance"]["mode"] == "ttf_smooth_baseline"
    assert regularized["provenance"]["mode"] == "ttf_smooth_correlation_regularization"
    assert len(baseline["steps"]) == len(regularized["steps"])
    assert all(step["tsp_scope"] == "variation_boundary" for step in regularized["steps"])
    assert all("ttf_smooth_ablation" in step for step in regularized["steps"])
