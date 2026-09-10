from ratiss_topological_decoherence.logical_qubit import TopologicalQubit


def test_source_derived_topological_qubit_exposes_a_complete_logical_signature():
    qubit = TopologicalQubit(protection=0.10, seed=42)
    initial = qubit.measure_state()
    after_gate = qubit.x_gate().measure_state()
    for state in (initial, after_gate):
        assert {"P_sig", "betti", "protected", "logical_bit", "coherence", "scope"}.issubset(state)
        assert state["scope"] == "algorithmic_topological_logical_qubit_simulation"
    assert initial["P_sig"] != after_gate["P_sig"] or initial["logical_bit"] != after_gate["logical_bit"]


def test_source_derived_noise_reduces_the_explicit_coherence_proxy():
    qubit = TopologicalQubit(seed=42)
    before = qubit.fidelity_vs_ideal()
    after = qubit.noise(0.30).fidelity_vs_ideal()
    assert before == 1.0
    assert after == 0.70
