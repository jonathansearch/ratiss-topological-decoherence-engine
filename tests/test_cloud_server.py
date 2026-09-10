from ratiss_topological_decoherence.cloud_server import create_app


def test_cloud_studio_serves_a_design_and_simulates_it():
    client = create_app().test_client()
    example = client.get("/api/studio/example")
    assert example.status_code == 200
    result = client.post("/api/simulate/studio", json=example.get_json())
    assert result.status_code == 200
    timeline = result.get_json()
    assert timeline["provenance"]["mode"] == "internal_studio_import"
    assert timeline["design_context"]["source"]["schema"] == "quantum-circuit-studio/v0.1"
