from ratiss_topological_decoherence.simulation import SimulationConfig, run_local_demo


def test_local_pipeline_exports_real_cubic_slices_and_declares_its_boundary():
    document = run_local_demo(SimulationConfig())
    assert document["schema"] == "ratiss.topological-decoherence.timeline.v1"
    assert document["provenance"]["mode"] == "local"
    assert document["provenance"]["validated_on_hardware"] is False
    assert document["config"]["scenario"] == "accelerated_decoherence_stress_demo"
    assert len(document["steps"]) == 11
    first = document["steps"][0]
    assert len(first["cube_slice"]) == 5
    assert len(first["cube_slice"][0]) == 5
    assert first["topology"]["psig"] >= 0.0
    assert first["logical_topology"]["scope"] == "algorithmic_topological_logical_qubit_simulation"
    assert document["encoding"]["logical_core"]["source"].startswith("RATISS Experimental IA/decoherence-map")
    assert any(len(step["tsp_inspection"]["path"]) >= 3 for step in document["steps"])
