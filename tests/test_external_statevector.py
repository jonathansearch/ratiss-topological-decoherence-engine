import json
from pathlib import Path

from ratiss_topological_decoherence.external_statevector import run_qiskit_statevector_trajectory


def bell_fixture() -> dict:
    return json.loads((Path(__file__).parent.parent / "examples" / "qiskit-bell-statevector-trajectory.json").read_text())


def test_imports_external_qiskit_statevectors_into_a_traceable_timeline():
    document = run_qiskit_statevector_trajectory(bell_fixture())
    assert document["provenance"]["mode"] == "external_qiskit_statevector"
    assert document["provenance"]["validated_on_hardware"] is False
    assert document["config"]["n_qubits"] == 2
    assert len(document["steps"]) == 3
    assert document["steps"][-1]["gate"] == "cx q0,q1"
    assert document["steps"][-1]["cube_slice"][0][1] > 0.99
    assert document["design_context"]["compilation"]["kind"] == "external_statevector_import"
