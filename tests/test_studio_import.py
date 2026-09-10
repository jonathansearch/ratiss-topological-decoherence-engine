import json
from pathlib import Path

from ratiss_topological_decoherence.studio_import import compile_studio_document, run_studio_document


def studio_demo() -> dict:
    return json.loads((Path(__file__).parent.parent / "examples" / "transmon-microcell.studio.json").read_text())


def test_compiles_studio_components_into_a_declared_logical_scaffold():
    compiled = compile_studio_document(studio_demo())
    assert compiled.n_qubits == 2
    assert [gate.name for gate in compiled.gates] == ["h", "h", "cz"]
    assert compiled.gates[-1].qubits == (0, 1)
    assert compiled.design_context["source"]["mode"] == "internal_studio_import"
    assert compiled.design_context["compilation"]["hardware_calibrated"] is False
    assert len(compiled.design_context["frequency_overlay"]) == 2
    assert compiled.design_context["crosstalk_overlay"][0]["first"] == "q0"


def test_runs_a_studio_document_through_the_common_timeline_contract():
    document = run_studio_document(studio_demo())
    assert document["provenance"]["mode"] == "internal_studio_import"
    assert document["config"]["n_qubits"] == 2
    assert document["design_context"]["qubit_map"] == [{"studio_id": "q0", "ratiss_index": 0}, {"studio_id": "q1", "ratiss_index": 1}]
    assert document["steps"][-1]["gate"] == "cz(0,1)"
    assert all("cube_slice" in step for step in document["steps"])
