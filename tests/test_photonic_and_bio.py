import json
from pathlib import Path

from ratiss_topological_decoherence.correlation_import import run_bio_correlation_trajectory, run_photonic_mode_trajectory


def fixture(name: str) -> dict:
    return json.loads((Path(__file__).parent.parent / "examples" / name).read_text())


def test_imports_declared_photonic_mode_association_without_density_claim():
    document = run_photonic_mode_trajectory(fixture("photonic-mode-trajectory.json"))
    assert document["provenance"]["mode"] == "external_photonic_modes"
    assert document["provenance"]["simulation"] == "photonic_mode_association"
    assert document["steps"][-1]["cube_slice"][0][1] > 0.99
    assert document["steps"][-1]["logical_topology"]["P_sig"] is None


def test_imports_normalized_bio_matrix_without_bio_diagnosis():
    document = run_bio_correlation_trajectory(fixture("bio-correlation-trajectory.json"))
    assert document["provenance"]["mode"] == "external_bio_correlation"
    assert document["cube"]["metric"] == "declared_bio_correlation"
    assert document["steps"][0]["metric_scope"]["density_metrics_available"] is False
    assert document["design_context"]["labels"] == ["signal_0", "signal_1", "signal_2"]
