"""Internal Quantum Circuit Studio JSON importer for RATISS Studio Cloud.

The importer accepts the user's original ``quantum-circuit-studio/v0.1`` local
document. It compiles only a declared logical scaffold for local simulation;
nominal design fields remain visible as design context and are never treated as
calibration, geometry extraction or fabrication data.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import pi
from pathlib import Path
from typing import Any
import json

from .simulation import GateSpec, SimulationConfig, run_program


STUDIO_SCHEMA = "quantum-circuit-studio/v0.1"


@dataclass(frozen=True)
class CompiledStudioDesign:
    """A traceable logical scaffold obtained from one Studio design document."""

    n_qubits: int
    gates: list[GateSpec]
    positions: list[list[float]]
    design_context: dict[str, Any]


def _nodes_by_id(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = document.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("Studio document requires a nodes array")
    indexed: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            raise ValueError("Every Studio node must be an object with a string id")
        if node["id"] in indexed:
            raise ValueError(f"Duplicate Studio node id: {node['id']}")
        indexed[node["id"]] = node
    return indexed


def _normalised_positions(qubits: list[dict[str, Any]]) -> list[list[float]]:
    """Map Studio schematic coordinates to deterministic display coordinates.

    The z lift is a visual frequency offset around the circuit mean, not a
    physical elevation or a geometrical thickness.
    """

    frequencies = [float(node.get("frequency", 0.0)) for node in qubits]
    mean_frequency = sum(frequencies) / len(frequencies)
    positions = []
    for node, frequency in zip(qubits, frequencies):
        x = (float(node.get("x", 50.0)) - 50.0) / 18.0
        y = (50.0 - float(node.get("y", 50.0))) / 18.0
        z = (frequency - mean_frequency) * 0.55
        positions.append([round(x, 6), round(y, 6), round(z, 6)])
    return positions


def _frequency_overlay(qubits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for qubit in qubits:
        nearest: tuple[dict[str, Any], float] | None = None
        for candidate in qubits:
            if candidate["id"] == qubit["id"]:
                continue
            separation = abs(float(qubit.get("frequency", 0.0)) - float(candidate.get("frequency", 0.0)))
            if nearest is None or separation < nearest[1]:
                nearest = (candidate, separation)
        separation = nearest[1] if nearest else float("inf")
        risk = "collision" if separation < 0.08 else "watch" if separation < 0.20 else "stable"
        result.append({
            "studio_id": qubit["id"],
            "frequency": float(qubit.get("frequency", 0.0)),
            "unit": qubit.get("unit", "GHz"),
            "nearest_studio_id": nearest[0]["id"] if nearest else None,
            "separation": None if separation == float("inf") else round(separation, 9),
            "risk": risk,
            "scope": "nominal_studio_frequency_overlay_not_calibration",
        })
    return result


def _crosstalk_overlay(
    qubits: list[dict[str, Any]],
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    adjacency = {node_id: set() for node_id in nodes}
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    couplers = [node for node in nodes.values() if node.get("kind") == "coupler"]
    overlays = []
    for index, first in enumerate(qubits):
        for second in qubits[index + 1:]:
            shared = [coupler["id"] for coupler in couplers if first["id"] in adjacency[coupler["id"]] and second["id"] in adjacency[coupler["id"]]]
            direct = second["id"] in adjacency[first["id"]]
            distance = ((float(first.get("x", 50)) - float(second.get("x", 50))) ** 2 + (float(first.get("y", 50)) - float(second.get("y", 50))) ** 2) ** 0.5
            detuning = abs(float(first.get("frequency", 0.0)) - float(second.get("frequency", 0.0)))
            topology_factor = 0.9 if shared else 0.7 if direct else 0.15
            spatial_factor = max(0.0, min(1.0, (60.0 - distance) / 60.0))
            spectral_factor = max(0.0, min(1.0, (0.5 - detuning) / 0.5))
            score = round((0.5 * topology_factor + 0.32 * spectral_factor + 0.18 * spatial_factor) * 100)
            overlays.append({
                "first": first["id"], "second": second["id"], "adjacent": bool(shared or direct),
                "coupling_paths": shared, "distance": round(distance, 9), "detuning": round(detuning, 9),
                "score": score, "level": "high" if score >= 70 else "medium" if score >= 45 else "low",
                "scope": "nominal_studio_crosstalk_overlay_not_em_extraction",
            })
    return sorted(overlays, key=lambda item: item["score"], reverse=True)


def compile_studio_document(document: dict[str, Any]) -> CompiledStudioDesign:
    """Compile a Studio model into a declared local logical simulation scaffold."""

    if document.get("schema") != STUDIO_SCHEMA:
        raise ValueError(f"Expected Studio schema {STUDIO_SCHEMA!r}")
    nodes = _nodes_by_id(document)
    raw_edges = document.get("edges", [])
    if not isinstance(raw_edges, list):
        raise ValueError("Studio document requires an edges array")
    edges: list[tuple[str, str]] = []
    for edge in raw_edges:
        if not isinstance(edge, list) or len(edge) != 2 or not all(isinstance(item, str) for item in edge):
            raise ValueError("Studio edges must be [source, target] string pairs")
        first, second = edge
        if first not in nodes or second not in nodes:
            raise ValueError(f"Studio edge references an unknown component: {first!r}, {second!r}")
        edges.append((first, second))
    qubits = [node for node in document["nodes"] if node.get("kind") == "qubit"]
    if not qubits:
        raise ValueError("Studio design contains no qubit components")
    index_by_id = {node["id"]: index for index, node in enumerate(qubits)}
    neighbours = {node_id: set() for node_id in nodes}
    for first, second in edges:
        neighbours[first].add(second)
        neighbours[second].add(first)
    interactions: set[tuple[int, int]] = set()
    for coupler in (node for node in nodes.values() if node.get("kind") == "coupler"):
        attached = [index_by_id[node_id] for node_id in neighbours[coupler["id"]] if node_id in index_by_id]
        for first, second in zip(attached, attached[1:]):
            interactions.add(tuple(sorted((first, second))))
    for first, second in edges:
        if first in index_by_id and second in index_by_id:
            interactions.add(tuple(sorted((index_by_id[first], index_by_id[second]))))
    gates = [GateSpec("h", (index,)) for index in range(len(qubits))]
    gates.extend(GateSpec("cz", interaction) for interaction in sorted(interactions))
    design_context = {
        "source": {"schema": STUDIO_SCHEMA, "name": document.get("name", "unnamed-studio-design"), "mode": "internal_studio_import"},
        "qubit_map": [{"studio_id": node["id"], "ratiss_index": index} for index, node in enumerate(qubits)],
        "components": [{key: value for key, value in node.items() if key in {"id", "kind", "frequency", "unit", "x", "y", "notes"}} for node in document["nodes"]],
        "links": [{"source": first, "target": second} for first, second in edges],
        "frequency_overlay": _frequency_overlay(qubits),
        "crosstalk_overlay": _crosstalk_overlay(qubits, nodes, edges),
        "compilation": {
            "kind": "logical_scaffold",
            "hardware_calibrated": False,
            "preparation": "h on every declared Studio qubit",
            "interaction_gate": "cz inferred from coupler or direct qubit links",
            "interaction_count": len(interactions),
            "scope": "simulation_scaffold_not_pulse_or_fabrication_recipe",
        },
    }
    return CompiledStudioDesign(len(qubits), gates, _normalised_positions(qubits), design_context)


def run_studio_document(document: dict[str, Any], config: SimulationConfig | None = None) -> dict[str, Any]:
    """Simulate one Studio document through the RATISS internal design path."""

    compiled = compile_studio_document(document)
    config = config or SimulationConfig(n_qubits=compiled.n_qubits, scenario="studio_internal_logical_scaffold")
    if config.n_qubits != compiled.n_qubits:
        config = replace(config, n_qubits=compiled.n_qubits)
    return run_program(
        compiled.gates,
        config,
        positions=compiled.positions,
        design_context=compiled.design_context,
        provenance_mode="internal_studio_import",
        encoding={
            "profile": "quantum_circuit_studio_to_ratiss_topological_scaffold",
            "description": "Logical RATISS trajectory compiled from a Quantum Circuit Studio design document.",
            "hardware_claim": "none",
            "logical_core": {
                "source": "RATISS Experimental IA/decoherence-map:c67d2e7:ratis_net/lct_modules/topo_qubit.py",
                "interpretation": "Algorithmic topological-logical-qubit sidecar; separate from the Studio design model and density-matrix layer.",
            },
        },
    )


def run_studio_file(path: str | Path, config: SimulationConfig | None = None) -> dict[str, Any]:
    """Load one exported Studio JSON file and run the internal import path."""

    return run_studio_document(json.loads(Path(path).read_text(encoding="utf-8")), config=config)
