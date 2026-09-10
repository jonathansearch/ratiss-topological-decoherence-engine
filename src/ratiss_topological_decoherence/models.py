"""Typed, JSON-safe data structures for the shared timeline contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class QubitObservation:
    """Per-qubit values at one simulated gate boundary.

    ``psig`` is kept as a viewer-compatibility alias for ``topology_support``.
    It is not an individual H1 persistence: H1 persistence is a graph-level
    value in ``topology.psig``.
    """

    id: int
    position: list[float]
    fidelity_to_ideal: float
    local_decoherence: float
    purity: float
    topology_support: float
    psig: float
    degree: int
    criticality: float
    criticality_terms: dict[str, float]


@dataclass(frozen=True)
class EdgeObservation:
    """A visible correlation edge, derived from the exported cube values."""

    source: int
    target: int
    mutual_information: float
    pauli_correlation: float
    concurrence: float
    correlation: float
    type: str
    stability: float
    active: bool


@dataclass(frozen=True)
class StepArtifact:
    """The exact unit rendered by an atlas timeline cursor."""

    step: int
    gate: str
    qubits: list[QubitObservation]
    edges: list[EdgeObservation]
    avg_psig: float
    decoherence_detected: bool
    topology: dict[str, Any]
    logical_topology: dict[str, Any]
    tsp_inspection: dict[str, Any]
    cube_slice: list[list[float]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def timeline_document(
    *,
    steps: list[StepArtifact],
    config: dict[str, Any],
    encoding: dict[str, Any],
    design_context: dict[str, Any] | None = None,
    provenance_mode: str = "local",
    simulation_kind: str = "density_matrix",
    cube_metric: str = "normalized_mutual_information",
    cube_normalization: str = "min(1, I(rho_ij)/2)",
) -> dict[str, Any]:
    """Build the versioned interchange document consumed by the offline atlas."""

    document = {
        "schema": "ratiss.topological-decoherence.timeline.v1",
        "provenance": {
            "mode": provenance_mode,
            "engine": "ratiss-topological-decoherence-engine",
            "simulation": simulation_kind,
            "validated_on_hardware": False,
            "claim_boundary": (
                "Simulation and topological post-processing only; not a hardware "
                "topological-qubit certification or an error-correction command."
            ),
        },
        "encoding": encoding,
        "config": config,
        "cube": {
            "axes": ["step", "source_qubit", "target_qubit"],
            "metric": cube_metric,
            "normalization": cube_normalization,
        },
        "steps": [step.to_dict() if isinstance(step, StepArtifact) else step for step in steps],
    }
    if design_context is not None:
        document["design_context"] = design_context
    return document
