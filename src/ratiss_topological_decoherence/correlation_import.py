"""Adapters for declared correlation-like external trajectories.

They deliberately keep classical counts, photonic mode associations and supplied
bio correlation matrices separate from the density-matrix simulation path.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from math import sqrt
from pathlib import Path
from typing import Any
import json
import numpy as np

from .models import EdgeObservation, QubitObservation, StepArtifact, timeline_document
from .simulation import SimulationConfig, deterministic_positions
from .topology import topology_from_correlation
from .tsp import inspection_route


def _matrix(raw: Any) -> np.ndarray:
    matrix = np.asarray(raw, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 1:
        raise ValueError("Correlation matrices must be non-empty and square.")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("Correlation matrices must contain only finite values.")
    if not np.allclose(matrix, matrix.T, atol=1e-8):
        raise ValueError("Correlation matrices must be symmetric.")
    if np.any(matrix < -1e-8) or np.any(matrix > 1 + 1e-8):
        raise ValueError("Correlation matrices must be normalized in [0, 1].")
    matrix = np.clip(matrix, 0.0, 1.0)
    np.fill_diagonal(matrix, 1.0)
    return matrix


def _external_step(
    matrix: np.ndarray,
    *,
    step: int,
    label: str,
    positions: list[list[float]],
    config: SimulationConfig,
    previous_edges: set[tuple[int, int]],
    scope: str,
    inspection_nodes: list[int] | None = None,
) -> tuple[dict[str, Any], set[tuple[int, int]]]:
    n_qubits = config.n_qubits
    topology = topology_from_correlation(matrix, max_edge=config.rips_max_edge)
    degrees = np.zeros(n_qubits, dtype=int)
    support = np.zeros(n_qubits, dtype=float)
    active: set[tuple[int, int]] = set()
    edges: list[EdgeObservation] = []
    for first in range(n_qubits):
        for second in range(first + 1, n_qubits):
            association = float(matrix[first, second])
            if association >= config.edge_threshold:
                active.add((first, second)); degrees[first] += 1; degrees[second] += 1
                support[first] += association; support[second] += association
                edges.append(EdgeObservation(
                    source=first, target=second, mutual_information=round(association, 9), pauli_correlation=0.0,
                    concurrence=0.0, correlation=round(association, 9), type="declared_association",
                    stability=1.0, active=True,
                ))
    support = np.clip(support / max(1, n_qubits - 1), 0.0, 1.0)
    qubits: list[QubitObservation] = []
    priority: list[int] = []
    for index in range(n_qubits):
        prior = {edge for edge in previous_edges if index in edge}
        lost = {edge for edge in prior if edge not in active}
        break_ratio = len(lost) / max(1, len(prior))
        structural_criticality = float(np.clip(.75 * (1 - support[index]) + .25 * break_ratio, 0.0, 1.0))
        if structural_criticality >= config.criticality_threshold:
            priority.append(index)
        qubits.append(QubitObservation(
            id=index, position=positions[index], fidelity_to_ideal=0.0, local_decoherence=0.0, purity=0.0,
            topology_support=round(float(support[index]), 9), psig=round(float(support[index]), 9), degree=int(degrees[index]),
            criticality=round(structural_criticality, 9), criticality_terms={
                "structural_support_deficit": round(float(1 - support[index]), 9), "link_break_ratio": round(float(break_ratio), 9)
            },
        ))
    artifact = StepArtifact(
        step=step, gate=label, qubits=qubits, edges=edges, avg_psig=round(float(np.mean(support)), 9),
        decoherence_detected=bool(priority), topology={
            "psig": round(float(topology["psig"]), 9), "betti": topology["betti"], "diagrams": topology["diagrams"],
            "n_finite_h1": topology["n_finite_h1"], "max_edge": topology["max_edge"], "distance_model": topology["distance_model"],
            "metric_scope": scope,
        },
        logical_topology={"P_sig": None, "scope": "not_applicable_external_non_density_input"},
        tsp_inspection=inspection_route(positions, inspection_nodes if inspection_nodes is not None else priority),
        cube_slice=[[round(float(value), 9) for value in row] for row in matrix],
    ).to_dict()
    artifact["metric_scope"] = {
        "density_metrics_available": False,
        "fidelity": "not_available", "purity": "not_available", "concurrence": "not_available",
        "criticality": "structural_priority_from_declared_association_not_quantum_decoherence", "association": scope,
    }
    artifact["tsp_scope"] = "variation_boundary" if inspection_nodes is not None else "criticality_nodes"
    for qubit in artifact["qubits"]:
        qubit["fidelity_to_ideal"] = None; qubit["local_decoherence"] = None; qubit["purity"] = None
    return artifact, active


def _association_timeline(
    payload: dict[str, Any], *, provenance_mode: str, metric: str, scope: str, source_kind: str,
) -> dict[str, Any]:
    trajectory = payload.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory:
        raise ValueError("External association payload requires a non-empty trajectory array.")
    first = trajectory[0]
    if not isinstance(first, dict):
        raise ValueError("Each trajectory entry must be an object.")
    first_matrix = _matrix(first.get("correlation_matrix"))
    n_qubits = first_matrix.shape[0]
    config = SimulationConfig(n_qubits=n_qubits, scenario=provenance_mode)
    positions = payload.get("positions") or deterministic_positions(n_qubits)
    if len(positions) != n_qubits:
        raise ValueError("External positions must contain one coordinate per node.")
    steps: list[dict[str, Any]] = []
    previous: set[tuple[int, int]] = set()
    for index, record in enumerate(trajectory):
        if not isinstance(record, dict):
            raise ValueError("Each trajectory entry must be an object.")
        correlation = _matrix(record.get("correlation_matrix"))
        if correlation.shape[0] != n_qubits:
            raise ValueError("All trajectory matrices must have the same size.")
        artifact, previous = _external_step(
            correlation, step=int(record.get("step", index)), label=str(record.get("label", record.get("gate", f"external_association({index})"))),
            positions=positions, config=config, previous_edges=previous, scope=scope,
        )
        steps.append(artifact)
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    return timeline_document(
        steps=steps, config=asdict(config), provenance_mode=provenance_mode, simulation_kind=source_kind,
        cube_metric=metric, cube_normalization="declared association normalized to [0, 1]",
        encoding={"profile": provenance_mode, "description": scope, "hardware_claim": "none"},
        design_context={"source": {"mode": provenance_mode, "declared_source": source}, "labels": payload.get("labels") or payload.get("mode_labels"),
                        "compilation": {"kind": "external_association_import", "hardware_calibrated": False, "scope": scope}},
    )


def _counts_matrix(counts: dict[str, Any], *, bit_order: str) -> np.ndarray:
    if not isinstance(counts, dict) or not counts:
        raise ValueError("Counts must be a non-empty bitstring-to-count mapping.")
    parsed: list[tuple[list[int], float]] = []
    width: int | None = None
    for raw, weight in counts.items():
        token = str(raw).replace(" ", "")
        if not token or any(bit not in "01" for bit in token):
            raise ValueError("Counts keys must be binary bitstrings.")
        if width is None: width = len(token)
        if len(token) != width: raise ValueError("All count bitstrings must have the same length.")
        numeric = float(weight)
        if not np.isfinite(numeric) or numeric < 0: raise ValueError("Counts must be finite and non-negative.")
        bits = [int(bit) for bit in (token[::-1] if bit_order == "qiskit_little_endian" else token)]
        parsed.append((bits, numeric))
    total = sum(weight for _, weight in parsed)
    if total <= 0: raise ValueError("At least one count must be positive.")
    n = width or 0; marginal = np.zeros(n); joint = np.zeros((n, n))
    for bits, weight in parsed:
        vector = np.asarray(bits, dtype=float); probability = weight / total; marginal += probability * vector; joint += probability * np.outer(vector, vector)
    matrix = np.eye(n)
    for first in range(n):
        for second in range(first + 1, n):
            denominator = sqrt(float(marginal[first] * marginal[second]))
            matrix[first, second] = matrix[second, first] = 0.0 if denominator == 0 else float(np.clip(joint[first, second] / denominator, 0.0, 1.0))
    return matrix


def run_qiskit_counts_trajectory(payload: dict[str, Any]) -> dict[str, Any]:
    trajectory = payload.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory: raise ValueError("Qiskit counts payload requires a non-empty trajectory array.")
    bit_order = payload.get("bit_order", "qiskit_little_endian")
    if bit_order not in {"qiskit_little_endian", "left_to_right"}: raise ValueError("bit_order must be qiskit_little_endian or left_to_right.")
    normalized = {**payload, "trajectory": []}
    for index, record in enumerate(trajectory):
        if not isinstance(record, dict): raise ValueError("Each counts trajectory entry must be an object.")
        normalized["trajectory"].append({"step": record.get("step", index), "label": record.get("gate", record.get("label", f"counts({index})")), "correlation_matrix": _counts_matrix(record.get("counts"), bit_order=bit_order).tolist()})
    return _association_timeline(normalized, provenance_mode="external_qiskit_counts", metric="classical_count_cooccurrence_association", scope="Diagonal probability association computed from declared Qiskit counts; not density-matrix tomography or entanglement.", source_kind="classical_counts_association")


def run_qiskit_counts_file(path: str | Path) -> dict[str, Any]:
    return run_qiskit_counts_trajectory(json.loads(Path(path).read_text(encoding="utf-8")))


def _cooccupation_matrix(outcomes: Any, n_modes: int) -> np.ndarray:
    if not isinstance(outcomes, list) or not outcomes:
        raise ValueError("Photonic outcomes must be a non-empty array.")
    total = 0.0
    marginal = np.zeros(n_modes, dtype=float)
    joint = np.zeros((n_modes, n_modes), dtype=float)
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            raise ValueError("Each photonic outcome must be an object.")
        occupation = np.asarray(outcome.get("occupation"), dtype=float)
        if occupation.shape != (n_modes,) or not np.all(np.isfinite(occupation)) or np.any(occupation < 0):
            raise ValueError("Photonic occupation must contain one non-negative finite value per mode.")
        probability = float(outcome.get("probability", -1))
        if not np.isfinite(probability) or probability < 0:
            raise ValueError("Photonic probabilities must be finite and non-negative.")
        active = (occupation > 0).astype(float)
        total += probability; marginal += probability * active; joint += probability * np.outer(active, active)
    if total <= 0: raise ValueError("At least one photonic outcome probability must be positive.")
    marginal /= total; joint /= total
    matrix = np.eye(n_modes)
    for first in range(n_modes):
        for second in range(first + 1, n_modes):
            denominator = sqrt(float(marginal[first] * marginal[second]))
            matrix[first, second] = matrix[second, first] = 0.0 if denominator == 0 else float(np.clip(joint[first, second] / denominator, 0.0, 1.0))
    return matrix


def run_photonic_mode_trajectory(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize declared mode occupation distributions to co-occupation timelines."""

    labels = payload.get("mode_labels")
    if not isinstance(labels, list) or not labels or not all(isinstance(label, str) and label for label in labels):
        raise ValueError("Photonic payload requires non-empty string mode_labels.")
    trajectory = payload.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory: raise ValueError("Photonic payload requires a non-empty trajectory array.")
    normalized = {**payload, "trajectory": []}
    for index, record in enumerate(trajectory):
        if not isinstance(record, dict): raise ValueError("Each photonic trajectory entry must be an object.")
        normalized["trajectory"].append({"step": record.get("step", index), "label": record.get("label", f"mode_distribution({index})"), "correlation_matrix": _cooccupation_matrix(record.get("outcomes"), len(labels)).tolist()})
    return _association_timeline(normalized, provenance_mode="external_photonic_modes", metric="mode_cooccupation_association", scope="Mode co-occupation association from declared photonic outcome probabilities; not a reconstructed photonic density matrix or an unmeasured interference claim.", source_kind="photonic_mode_association")


def run_photonic_mode_file(path: str | Path) -> dict[str, Any]:
    return run_photonic_mode_trajectory(json.loads(Path(path).read_text(encoding="utf-8")))


def run_perceval_distribution(distribution: Any, *, label: str = "perceval_distribution", source: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert a local Perceval ``BSDistribution`` into a RATISS mode timeline.

    This function consumes only the declared output distribution. It does not
    infer unobserved phases, a density matrix, device calibration or a hardware
    result. It deliberately delegates the structural conversion to the same
    photonic mode contract used for serialized external outcomes.
    """

    outcomes: list[dict[str, Any]] = []
    n_modes: int | None = None
    for state, probability in distribution.items():
        width = int(state.m)
        if n_modes is None: n_modes = width
        if width != n_modes: raise ValueError("Perceval distribution contains inconsistent mode widths.")
        outcomes.append({"occupation": [int(state[index]) for index in range(width)], "probability": float(probability)})
    if n_modes is None: raise ValueError("Perceval distribution is empty.")
    return run_photonic_mode_trajectory({
        "source": {"framework": "Perceval", "backend": "declared_local_backend", **(source or {})},
        "mode_labels": [f"m{index}" for index in range(n_modes)],
        "trajectory": [{"step": 0, "label": label, "outcomes": outcomes}],
    })


def run_perceval_circuit(circuit: Any, input_occupation: list[int], *, label: str = "perceval_local_circuit") -> dict[str, Any]:
    """Run a Perceval circuit locally through its Naive backend and normalize its output.

    Perceval is imported lazily so that JSON-based photonic ingestion stays
    usable even when the optional SDK is absent from a consumer environment.
    """

    try:
        from perceval.backends import NaiveBackend
        from perceval.utils import BasicState
    except ImportError as error:
        raise RuntimeError("Perceval is optional. Install `perceval-quandela` to run a Perceval circuit directly.") from error
    backend = NaiveBackend()
    backend.set_circuit(circuit)
    backend.set_input_state(BasicState(input_occupation))
    return run_perceval_distribution(
        backend.prob_distribution(), label=label,
        source={"backend": "Naive", "execution": "local_perceval_simulation", "hardware_claim": "none"},
    )


def run_bio_correlation_trajectory(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize supplied biological correlation matrices without diagnosis or causality inference."""

    source = payload.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("measurement_protocol"), str) or not source["measurement_protocol"].strip():
        raise ValueError("Bio correlation payload requires source.measurement_protocol.")
    labels = payload.get("labels")
    if not isinstance(labels, list) or not labels or not all(isinstance(label, str) and label for label in labels):
        raise ValueError("Bio correlation payload requires non-empty string labels.")
    trajectory = payload.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory: raise ValueError("Bio correlation payload requires a non-empty trajectory array.")
    for record in trajectory:
        if not isinstance(record, dict): raise ValueError("Each bio trajectory entry must be an object.")
        raw = np.asarray(record.get("correlation_matrix"), dtype=float)
        if raw.shape != (len(labels), len(labels)) or not np.allclose(np.diag(raw), 1.0, atol=1e-8):
            raise ValueError("Each bio correlation matrix must match labels and have a unit diagonal.")
    return _association_timeline(payload, provenance_mode="external_bio_correlation", metric="declared_bio_correlation", scope="Supplied normalized biological correlation structure; no quantum-coherence, causal, clinical or biological-diagnostic inference.", source_kind="declared_bio_correlation")


def run_bio_correlation_file(path: str | Path) -> dict[str, Any]:
    return run_bio_correlation_trajectory(json.loads(Path(path).read_text(encoding="utf-8")))
