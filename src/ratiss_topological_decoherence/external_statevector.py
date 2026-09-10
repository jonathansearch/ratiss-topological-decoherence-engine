"""External Qiskit Statevector ingestion for RATISS Studio Cloud.

This adapter accepts an already exported statevector trajectory. It performs no
backend submission and does not turn imported simulation data into a hardware
claim. Each statevector is converted to a density matrix locally, then passed
through the same correlation, topology, criticity and timeline contract as the
internal Studio path.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from math import log2
from pathlib import Path
from typing import Any
import json
import numpy as np

from .logical_qubit import TopologicalQubit
from .models import StepArtifact, timeline_document
from .simulation import SimulationConfig, _step_artifact, deterministic_positions


def _complex_value(value: Any) -> complex:
    if isinstance(value, (int, float)):
        return complex(float(value), 0.0)
    if isinstance(value, str):
        return complex(value.replace("i", "j"))
    if isinstance(value, dict) and {"real", "imag"}.issubset(value):
        return complex(float(value["real"]), float(value["imag"]))
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return complex(float(value[0]), float(value[1]))
    raise ValueError("Statevector amplitudes must be numbers, complex strings, [real, imag], or {real, imag}.")


def _density_from_statevector(raw: Any) -> tuple[np.ndarray, int]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("A trajectory statevector must be a non-empty array.")
    vector = np.asarray([_complex_value(value) for value in raw], dtype=complex)
    n_qubits = round(log2(vector.size))
    if 2**n_qubits != vector.size:
        raise ValueError("Statevector length must be a power of two.")
    norm = float(np.vdot(vector, vector).real)
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("Statevector norm must be positive and finite.")
    if not np.isclose(norm, 1.0, atol=1e-8):
        vector = vector / np.sqrt(norm)
    return np.outer(vector, vector.conj()), n_qubits


def run_qiskit_statevector_trajectory(payload: dict[str, Any], config: SimulationConfig | None = None) -> dict[str, Any]:
    """Normalize a Qiskit-compatible statevector trajectory to ``timeline.v1``.

    Expected payload form::

        {"source": {"backend": "Aer"}, "trajectory": [
          {"step": 0, "gate": "initial", "statevector": [[1, 0], ...]}
        ]}

    ``gate`` is retained as a label only. The adapter does not infer a physical
    operation or advance the source-derived logical-qubit sidecar from an
    unlabeled external statevector.
    """

    trajectory = payload.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory:
        raise ValueError("External Qiskit payload requires a non-empty trajectory array.")
    first_density, n_qubits = _density_from_statevector(trajectory[0].get("statevector"))
    # Un statevector externe est une entrée exacte : on désactive le bruit de
    # corrélation synthétique pour ne pas corrompre une corrélation connue.
    config = config or SimulationConfig(n_qubits=n_qubits, scenario="external_qiskit_statevector_import", correlation_noise=0.0)
    if config.n_qubits != n_qubits or config.correlation_noise != 0.0:
        config = replace(config, n_qubits=n_qubits, correlation_noise=0.0)
    positions = payload.get("positions") or deterministic_positions(n_qubits)
    if len(positions) != n_qubits:
        raise ValueError("External positions must contain one coordinate per statevector qubit.")
    steps: list[StepArtifact] = []
    previous_edges: set[tuple[int, int]] = set()
    sidecar = TopologicalQubit(seed=42)
    for index, record in enumerate(trajectory):
        if not isinstance(record, dict):
            raise ValueError("Each trajectory entry must be an object.")
        density, step_n_qubits = _density_from_statevector(record.get("statevector"))
        if step_n_qubits != n_qubits:
            raise ValueError("All statevectors in one trajectory must have the same qubit count.")
        label = str(record.get("gate", f"external_statevector({index})"))
        logical = {
            **sidecar.measure_state(),
            "circuit_coupling": {
                "event": label,
                "mapping": "external_statevector_label_only_no_logical_gate_inference",
                "software_noise_budget": 0.0,
            },
        }
        artifact, previous_edges = _step_artifact(
            step=int(record.get("step", index)), gate=label, rho_noisy=density, rho_ideal=density,
            positions=positions, config=config, previous_edges=previous_edges, logical_topology=logical,
        )
        steps.append(artifact)
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    return timeline_document(
        steps=steps,
        config=asdict(config),
        provenance_mode="external_qiskit_statevector",
        encoding={
            "profile": "qiskit_statevector_external_import",
            "description": "Statevectors supplied externally and converted locally to density matrices for RATISS analysis.",
            "hardware_claim": "none",
            "logical_core": {
                "source": "RATISS Experimental IA/decoherence-map:c67d2e7:ratis_net/lct_modules/topo_qubit.py",
                "interpretation": "Unadvanced topological-logical-qubit sidecar; external labels are not inferred as logical operations.",
            },
        },
        design_context={
            "source": {"mode": "external_qiskit_statevector", "declared_source": source},
            "compilation": {"kind": "external_statevector_import", "hardware_calibrated": False, "scope": "imported_statevector_simulation_not_hardware_execution"},
        },
    )


def run_qiskit_statevector_file(path: str | Path, config: SimulationConfig | None = None) -> dict[str, Any]:
    return run_qiskit_statevector_trajectory(json.loads(Path(path).read_text(encoding="utf-8")), config=config)
