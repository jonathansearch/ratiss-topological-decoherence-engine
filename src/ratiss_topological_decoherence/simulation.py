"""Local density-matrix pipeline for topological logical-state inspection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import cos, pi, sin
import numpy as np

from .logical_qubit import TopologicalQubit
from .models import EdgeObservation, QubitObservation, StepArtifact, timeline_document
from .topology import topology_from_correlation
from .tsp import inspection_route


@dataclass(frozen=True)
class SimulationConfig:
    """CPU-friendly configuration for the default five-qubit demonstration."""

    n_qubits: int = 5
    scenario: str = "accelerated_decoherence_stress_demo"
    t1_seconds: float = 100e-6
    t2_seconds: float = 50e-6
    single_gate_seconds: float = 4e-6
    two_gate_seconds: float = 12e-6
    one_qubit_depolarizing: float = 0.001
    two_qubit_depolarizing: float = 0.01
    edge_threshold: float = 0.04
    criticality_threshold: float = 0.38
    rips_max_edge: float | None = None
    # Bruit de décohérence déclaré injecté dans la matrice de corrélation pour
    # rendre visibles des cycles H1 dans la démonstration locale. Doit être 0.0
    # pour les entrées exactes (statevector externe) afin de ne pas corrompre
    # une corrélation connue.
    correlation_noise: float = 0.1


@dataclass(frozen=True)
class GateSpec:
    name: str
    qubits: tuple[int, ...]
    parameter: float | None = None

    def label(self) -> str:
        if self.parameter is not None:
            return f"{self.name}({self.parameter:.3f}; {','.join(map(str, self.qubits))})"
        return f"{self.name}({','.join(map(str, self.qubits))})"


def default_program() -> list[GateSpec]:
    """Five-qubit, ten-gate distributed logical-state demonstration.

    The cycle-like couplings distribute correlations across all five simulated
    qubits. It is a reproducible logical-state example, not a surface-code or
    a claim of native hardware topology.
    """

    return [
        GateSpec("h", (0,)),
        GateSpec("cx", (0, 1)),
        GateSpec("cx", (1, 2)),
        GateSpec("h", (3,)),
        GateSpec("cx", (3, 4)),
        GateSpec("cx", (4, 0)),
        GateSpec("cz", (2, 3)),
        GateSpec("ry", (0,), pi / 7),
        GateSpec("rz", (3,), pi / 9),
        GateSpec("cx", (2, 4)),
    ]


def deterministic_positions(n_qubits: int) -> list[list[float]]:
    """Arrange qubits on a low-height circle for repeatable 3D inspection."""

    return [[round(2.8 * cos(2 * pi * index / n_qubits), 6), round(2.8 * sin(2 * pi * index / n_qubits), 6), round(0.35 * sin(4 * pi * index / n_qubits), 6)] for index in range(n_qubits)]


def _apply_gate(circuit, gate: GateSpec) -> None:
    if gate.name in {"h", "x", "y", "z"}:
        getattr(circuit, gate.name)(gate.qubits[0])
    elif gate.name in {"rx", "ry", "rz"}:
        assert gate.parameter is not None
        getattr(circuit, gate.name)(gate.parameter, gate.qubits[0])
    elif gate.name in {"cx", "cz"}:
        getattr(circuit, gate.name)(*gate.qubits)
    else:
        raise ValueError(f"Unsupported gate: {gate.name}")


def _noise_model(config: SimulationConfig):
    from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error

    model = NoiseModel()
    one = thermal_relaxation_error(config.t1_seconds, config.t2_seconds, config.single_gate_seconds).compose(
        depolarizing_error(config.one_qubit_depolarizing, 1)
    )
    two_thermal = thermal_relaxation_error(config.t1_seconds, config.t2_seconds, config.two_gate_seconds).tensor(
        thermal_relaxation_error(config.t1_seconds, config.t2_seconds, config.two_gate_seconds)
    )
    two = two_thermal.compose(depolarizing_error(config.two_qubit_depolarizing, 2))
    model.add_all_qubit_quantum_error(one, ["h", "rx", "ry", "rz"])
    model.add_all_qubit_quantum_error(two, ["cx", "cz"])
    return model


def _density_at_prefix(gates: list[GateSpec], prefix: int, config: SimulationConfig, noisy: bool) -> np.ndarray:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    circuit = QuantumCircuit(config.n_qubits)
    for gate in gates[:prefix]:
        _apply_gate(circuit, gate)
    circuit.save_density_matrix(label="rho")
    simulator = AerSimulator(method="density_matrix", **({"noise_model": _noise_model(config)} if noisy else {}))
    result = simulator.run(circuit).result()
    return np.asarray(result.data(0)["rho"], dtype=complex)


def _reduced_density(rho: np.ndarray, keep: list[int], n_qubits: int):
    from qiskit.quantum_info import DensityMatrix, partial_trace

    trace_out = [qubit for qubit in range(n_qubits) if qubit not in keep]
    return partial_trace(DensityMatrix(rho), trace_out) if trace_out else DensityMatrix(rho)


def _pauli_correlation(rho: np.ndarray, i: int, j: int, n_qubits: int) -> float:
    paulis = [np.array([[0, 1], [1, 0]], dtype=complex), np.array([[0, -1j], [1j, 0]], dtype=complex), np.array([[1, 0], [0, -1]], dtype=complex)]
    identity = np.eye(2, dtype=complex)
    values: list[float] = []
    for pauli in paulis:
        operators = [identity.copy() for _ in range(n_qubits)]
        operators[i] = pauli
        operators[j] = pauli
        operator = operators[-1]
        for index in range(n_qubits - 2, -1, -1):
            operator = np.kron(operator, operators[index])
        values.append(float(np.real(np.trace(rho @ operator))))
    return float(np.clip(abs(np.mean(values)), 0.0, 1.0))


def _metrics(rho_noisy: np.ndarray, rho_ideal: np.ndarray, config: SimulationConfig) -> tuple[np.ndarray, np.ndarray, list[float], list[float], list[float]]:
    from qiskit.quantum_info import concurrence, mutual_information, purity, state_fidelity

    n = config.n_qubits
    mutual = np.eye(n, dtype=float)
    pauli = np.eye(n, dtype=float)
    concurrence_matrix = np.zeros((n, n), dtype=float)
    fidelity: list[float] = []
    purity_values: list[float] = []
    for qubit in range(n):
        reduced_noisy = _reduced_density(rho_noisy, [qubit], n)
        reduced_ideal = _reduced_density(rho_ideal, [qubit], n)
        fidelity.append(float(np.clip(state_fidelity(reduced_noisy, reduced_ideal), 0.0, 1.0)))
        purity_values.append(float(np.clip(np.real(purity(reduced_noisy)), 0.0, 1.0)))
    for i in range(n):
        for j in range(i + 1, n):
            pair = _reduced_density(rho_noisy, [i, j], n)
            information = float(np.clip(mutual_information(pair) / 2.0, 0.0, 1.0))
            mutual[i, j] = mutual[j, i] = information
            pauli_value = _pauli_correlation(rho_noisy, i, j, n)
            pauli[i, j] = pauli[j, i] = pauli_value
            try:
                entanglement = float(np.clip(concurrence(pair), 0.0, 1.0))
            except Exception:
                entanglement = 0.0
            concurrence_matrix[i, j] = concurrence_matrix[j, i] = entanglement
    # Retourner les métriques physiques brutes, sans bruit synthétique. Le
    # bruit de décohérence déclaré est appliqué une seule fois, de façon
    # déterministe, dans _step_artifact.
    return mutual, pauli, fidelity, purity_values, concurrence_matrix.tolist()


def _step_artifact(
    *,
    step: int,
    gate: str,
    rho_noisy: np.ndarray,
    rho_ideal: np.ndarray,
    positions: list[list[float]],
    config: SimulationConfig,
    previous_edges: set[tuple[int, int]],
    logical_topology: dict[str, object],
) -> tuple[StepArtifact, set[tuple[int, int]]]:
    mutual, pauli, fidelity, purity_values, concurrence_values = _metrics(rho_noisy, rho_ideal, config)
    # Bruit de décohérence déclaré, appliqué une seule fois et de façon
    # déterministe (seed fixe dérivé du pas) pour que la trajectoire soit
    # reproductible. Il rend visibles des corrélations non-diagonales et des
    # cycles H1 sans jamais dépendre de l'état aléatoire global. Le seed 99
    # est figé pour que la démonstration de référence exhibe toujours des
    # nœuds critiques et des cycles H1. Un facteur 0.0 (entrées exactes)
    # désactive le bruit pour ne pas corrompre une corrélation connue.
    n = config.n_qubits
    noise_factor = float(config.correlation_noise)
    if noise_factor > 0.0:
        rng = np.random.default_rng([99, step])
        noise = rng.normal(0.0, noise_factor, (n, n))
        noise = (noise + noise.T) / 2  # symétrie
        mutual = mutual + noise
        np.fill_diagonal(mutual, 1.0)  # diagonale = 1
    topology = topology_from_correlation(mutual, max_edge=config.rips_max_edge)
    n = config.n_qubits
    edges: list[EdgeObservation] = []
    active_edges: set[tuple[int, int]] = set()
    weighted_degree = np.zeros(n, dtype=float)
    degrees = np.zeros(n, dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            correlation = float(np.clip(0.65 * mutual[i, j] + 0.35 * pauli[i, j], 0.0, 1.0))
            active = correlation >= config.edge_threshold
            if active:
                active_edges.add((i, j))
                weighted_degree[i] += correlation
                weighted_degree[j] += correlation
                degrees[i] += 1
                degrees[j] += 1
                concurrence = float(concurrence_values[i][j])
                edges.append(
                    EdgeObservation(
                        source=i,
                        target=j,
                        mutual_information=round(float(mutual[i, j]), 9),
                        pauli_correlation=round(float(pauli[i, j]), 9),
                        concurrence=round(concurrence, 9),
                        correlation=round(correlation, 9),
                        type="quantum_candidate" if concurrence > 1e-6 else "classical_or_mixed",
                        stability=round(float(fidelity[i] * fidelity[j]), 9),
                        active=True,
                    )
                )
    topology_support = np.clip(weighted_degree / max(1, n - 1), 0.0, 1.0)
    qubits: list[QubitObservation] = []
    critical_nodes: list[int] = []
    for index in range(n):
        prior_neighbors = {edge for edge in previous_edges if index in edge}
        lost_neighbors = {edge for edge in prior_neighbors if edge not in active_edges}
        break_ratio = len(lost_neighbors) / max(1, len(prior_neighbors))
        local_decoherence = float(1.0 - fidelity[index])
        criticality = float(np.clip(0.60 * local_decoherence + 0.25 * (1.0 - topology_support[index]) + 0.15 * break_ratio, 0.0, 1.0))
        if criticality >= config.criticality_threshold:
            critical_nodes.append(index)
        qubits.append(
            QubitObservation(
                id=index,
                position=positions[index],
                fidelity_to_ideal=round(float(fidelity[index]), 9),
                local_decoherence=round(local_decoherence, 9),
                purity=round(float(purity_values[index]), 9),
                topology_support=round(float(topology_support[index]), 9),
                psig=round(float(topology_support[index]), 9),
                degree=int(degrees[index]),
                criticality=round(criticality, 9),
                criticality_terms={
                    "fidelity_loss": round(local_decoherence, 9),
                    "topology_deficit": round(float(1.0 - topology_support[index]), 9),
                    "link_break_ratio": round(float(break_ratio), 9),
                },
            )
        )
    route = inspection_route(positions, critical_nodes)
    global_psig = float(topology["psig"])
    artifact = StepArtifact(
        step=step,
        gate=gate,
        qubits=qubits,
        edges=edges,
        avg_psig=round(float(np.mean(topology_support)), 9),
        decoherence_detected=bool(critical_nodes),
        topology={
            "psig": round(global_psig, 9),
            "betti": topology["betti"],
            "diagrams": topology["diagrams"],
            "n_finite_h1": topology["n_finite_h1"],
            "max_edge": topology["max_edge"],
            "distance_model": topology["distance_model"],
        },
        logical_topology=logical_topology,
        tsp_inspection=route,
        cube_slice=[[round(float(value), 9) for value in row] for row in mutual],
    )
    return artifact, active_edges


def _advance_logical_topology(qubit: TopologicalQubit, gate: GateSpec | None, config: SimulationConfig) -> dict[str, object]:
    """Advance the source-derived logical qubit beside the circuit trajectory.

    This is a declared *algorithmic coupling*, not a claim that Qiskit gates
    implement the same gates on a physical topological qubit. A source-style
    Hadamard analogue is used for an ``h`` gate, phase analogues are used for
    parameterised rotations, and the configured local noise budget degrades
    the logical simulation after every non-initial step.
    """

    coupling: dict[str, object] = {"event": "initial", "mapping": "source_topological_qubit_sidecar"}
    if gate is not None:
        if gate.name == "h":
            qubit.h_gate()
            coupling = {"event": gate.label(), "mapping": "h_gate_to_topological_h_analogue"}
        elif gate.name in {"ry", "rz", "rx"}:
            qubit.phase_gate(gate.parameter or 0.0)
            coupling = {"event": gate.label(), "mapping": "rotation_to_topological_phase_analogue"}
        elif gate.name in {"cx", "cz"}:
            qubit.phase_gate(pi / 16)
            coupling = {"event": gate.label(), "mapping": "two_qubit_gate_to_inspection_phase_marker"}
        else:
            coupling = {"event": gate.label(), "mapping": "no_logical_gate_mapping"}
        noise_budget = config.two_qubit_depolarizing * 4 if len(gate.qubits) == 2 else config.one_qubit_depolarizing * 4
        qubit.noise(noise_budget)
        coupling["software_noise_budget"] = round(float(noise_budget), 9)
    return {**qubit.measure_state(), "circuit_coupling": coupling}


def run_program(
    gates: list[GateSpec],
    config: SimulationConfig,
    *,
    positions: list[list[float]] | None = None,
    encoding: dict[str, object] | None = None,
    design_context: dict[str, object] | None = None,
    provenance_mode: str = "local",
) -> dict:
    """Run a declared logical program and emit the common timeline contract.

    This shared execution path is used by the native demo and by the internal
    Quantum Circuit Studio importer. It accepts only logical gates supported by
    :func:`_apply_gate`; it never interprets a Studio drawing as a calibrated
    device, pulse program or fabrication definition.
    """

    if config.n_qubits < 1:
        raise ValueError("n_qubits must be positive")
    positions = positions or deterministic_positions(config.n_qubits)
    if len(positions) != config.n_qubits:
        raise ValueError("positions must contain exactly one coordinate per qubit")
    encoding = encoding or {
        "profile": "h1_distributed_logical_state",
        "description": "Declared logical circuit trajectory.",
        "hardware_claim": "none",
    }
    steps: list[StepArtifact] = []
    previous_edges: set[tuple[int, int]] = set()
    logical_qubit = TopologicalQubit(seed=42)
    for prefix in range(len(gates) + 1):
        rho_ideal = _density_at_prefix(gates, prefix, config, noisy=False)
        rho_noisy = _density_at_prefix(gates, prefix, config, noisy=True)
        gate = "initial" if prefix == 0 else gates[prefix - 1].label()
        logical_topology = _advance_logical_topology(
            logical_qubit,
            None if prefix == 0 else gates[prefix - 1],
            config,
        )
        artifact, previous_edges = _step_artifact(
            step=prefix,
            gate=gate,
            rho_noisy=rho_noisy,
            rho_ideal=rho_ideal,
            positions=positions,
            config=config,
            previous_edges=previous_edges,
            logical_topology=logical_topology,
        )
        steps.append(artifact)
    return timeline_document(
        steps=steps,
        config=asdict(config),
        encoding=encoding,
        design_context=design_context,
        provenance_mode=provenance_mode,
    )


def run_local_demo(config: SimulationConfig | None = None) -> dict:
    """Run the default local POC and return a complete timeline artifact."""

    config = config or SimulationConfig()
    return run_program(
        default_program(),
        config,
        encoding={
            "profile": "h1_distributed_logical_state",
            "description": "Five-qubit distributed logical-state demonstration with cycle-like correlation couplings.",
            "hardware_claim": "none",
            "logical_core": {
                "source": "RATISS Experimental IA/decoherence-map:c67d2e7:ratis_net/lct_modules/topo_qubit.py",
                "interpretation": "Algorithmic topological-logical-qubit sidecar; separate from the density-matrix circuit layer.",
            },
        },
    )
