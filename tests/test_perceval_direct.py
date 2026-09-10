import pytest

from ratiss_topological_decoherence.correlation_import import run_perceval_circuit


def test_runs_a_local_perceval_circuit_when_optional_sdk_is_present():
    pcvl = pytest.importorskip("perceval")
    circuit = pcvl.Circuit(2)
    circuit.add(0, pcvl.BS())
    document = run_perceval_circuit(circuit, [1, 0], label="single_photon_beamsplitter")
    assert document["provenance"]["mode"] == "external_photonic_modes"
    assert document["provenance"]["simulation"] == "photonic_mode_association"
    assert document["design_context"]["source"]["declared_source"]["framework"] == "Perceval"
    assert len(document["steps"][0]["cube_slice"]) == 2
