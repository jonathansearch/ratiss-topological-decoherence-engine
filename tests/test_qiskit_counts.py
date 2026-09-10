import json
from pathlib import Path

from ratiss_topological_decoherence.correlation_import import run_qiskit_counts_trajectory


def counts_fixture() -> dict:
    return json.loads((Path(__file__).parent.parent / "examples" / "qiskit-counts-trajectory.json").read_text())


def test_imports_counts_as_classical_association_not_density_tomography():
    document = run_qiskit_counts_trajectory(counts_fixture())
    assert document["provenance"]["mode"] == "external_qiskit_counts"
    assert document["provenance"]["simulation"] == "classical_counts_association"
    assert document["cube"]["metric"] == "classical_count_cooccurrence_association"
    assert document["steps"][-1]["cube_slice"][0][1] > 0.99
    assert document["steps"][-1]["qubits"][0]["fidelity_to_ideal"] is None
    assert document["steps"][-1]["metric_scope"]["density_metrics_available"] is False
