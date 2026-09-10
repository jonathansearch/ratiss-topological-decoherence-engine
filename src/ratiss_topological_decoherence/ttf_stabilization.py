"""Experimental TTF-inspired smooth graph regularization.

The module is an ablation on exported correlation matrices. It does not modify
the density matrix, issue an error-correction operation or make a hardware
protection claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import numpy as np

from .correlation_import import _external_step
from .models import timeline_document
from .simulation import SimulationConfig, deterministic_positions


@dataclass(frozen=True)
class SmoothStabilizationConfig:
    variation_threshold: float = 0.025
    slope: float = 18.0
    strength: float = 0.30
    max_boundary_nodes: int = 6


def correlation_variation(current: np.ndarray, previous: np.ndarray | None = None) -> np.ndarray:
    """Return mean absolute off-diagonal change per node."""
    if previous is None:
        return np.zeros(current.shape[0], dtype=float)
    delta = np.abs(current - previous).astype(float)
    np.fill_diagonal(delta, 0.0)
    return delta.sum(axis=1) / max(1, current.shape[0] - 1)


def variation_boundary(variation: np.ndarray, config: SmoothStabilizationConfig) -> list[int]:
    candidates = [int(index) for index, value in enumerate(variation) if float(value) >= config.variation_threshold]
    return sorted(candidates, key=lambda index: (-float(variation[index]), index))[: config.max_boundary_nodes]


def apply_smooth_regularization(matrix: np.ndarray, variation: np.ndarray, config: SmoothStabilizationConfig) -> tuple[np.ndarray, np.ndarray]:
    """Apply a bounded tanh profile to relation strengths near a variation frontier."""
    activation = 0.5 * (1.0 + np.tanh(config.slope * (variation - config.variation_threshold)))
    gain = np.maximum.outer(activation, activation)
    updated = np.asarray(matrix, dtype=float).copy()
    for first in range(updated.shape[0]):
        for second in range(first + 1, updated.shape[0]):
            value = updated[first, second]
            regularized = value + config.strength * gain[first, second] * (1.0 - value)
            updated[first, second] = updated[second, first] = float(np.clip(regularized, 0.0, 1.0))
    np.fill_diagonal(updated, 1.0)
    return updated, activation


def _scenario_timeline(
    source: dict[str, Any], *, smooth: bool, smooth_config: SmoothStabilizationConfig,
) -> dict[str, Any]:
    raw_steps = source.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("TTF ablation requires a non-empty timeline.v1 source artifact.")
    first_matrix = np.asarray(raw_steps[0].get("cube_slice"), dtype=float)
    n_qubits = first_matrix.shape[0]
    if first_matrix.shape != (n_qubits, n_qubits):
        raise ValueError("TTF ablation requires square cube slices.")
    raw_config = source.get("config") if isinstance(source.get("config"), dict) else {}
    config = SimulationConfig(**{field: raw_config[field] for field in SimulationConfig.__dataclass_fields__ if field in raw_config})
    if config.n_qubits != n_qubits:
        config = SimulationConfig(**{**asdict(config), "n_qubits": n_qubits})
    positions = raw_steps[0].get("qubits") and [node.get("position") for node in raw_steps[0]["qubits"]]
    positions = positions if isinstance(positions, list) and len(positions) == n_qubits else deterministic_positions(n_qubits)
    steps: list[dict[str, Any]] = []
    previous_matrix: np.ndarray | None = None
    previous_edges: set[tuple[int, int]] = set()
    for index, source_step in enumerate(raw_steps):
        matrix = np.asarray(source_step.get("cube_slice"), dtype=float)
        if matrix.shape != (n_qubits, n_qubits): raise ValueError("Every TTF ablation cube slice must have the same size.")
        matrix = (matrix + matrix.T) / 2.0; np.fill_diagonal(matrix, 1.0)
        variation = correlation_variation(matrix, previous_matrix)
        boundary = variation_boundary(variation, smooth_config)
        regularized, activation = apply_smooth_regularization(matrix, variation, smooth_config) if smooth else (matrix, np.zeros(n_qubits, dtype=float))
        artifact, previous_edges = _external_step(
            regularized, step=int(source_step.get("step", index)), label=str(source_step.get("gate", f"source_step({index})")),
            positions=positions, config=config, previous_edges=previous_edges,
            scope="TTF-inspired smooth correlation regularization ablation; no density-matrix, error-correction or hardware-protection claim.",
            inspection_nodes=boundary,
        )
        artifact["ttf_smooth_ablation"] = {
            "enabled": smooth,
            "variation": [round(float(value), 9) for value in variation],
            "boundary_nodes": boundary,
            "activation": [round(float(value), 9) for value in activation],
            "parameters": asdict(smooth_config),
            "interpretation": "algorithmic_correlation_regularization_only",
        }
        steps.append(artifact)
        previous_matrix = matrix
    return timeline_document(
        steps=steps, config={**asdict(config), "ttf_smooth_ablation": asdict(smooth_config), "ttf_smooth_enabled": smooth},
        provenance_mode="ttf_smooth_correlation_regularization" if smooth else "ttf_smooth_baseline",
        simulation_kind="correlation_graph_ablation",
        cube_metric="normalized_mutual_information_then_smooth_regularization" if smooth else "normalized_mutual_information_baseline_replay",
        cube_normalization="input relation values remain bounded in [0,1]",
        encoding={
            "profile": "ttf_smooth_correlation_ablation",
            "description": "Before/after correlation-graph regularization inspired by relation-first TTF analysis.",
            "hardware_claim": "none",
            "preprint_reference": {"shell_ttf_psig_recorded": 2.0524951073, "fixed_graph_psig_recorded": 1.4639, "interpretation": "recorded values retained as protocol references, not targets"},
        },
        design_context={"source_timeline_provenance": source.get("provenance"), "ablation": {"enabled": smooth, "scope": "software correlation graph only"}},
    )


def run_ttf_smooth_ablation(source: dict[str, Any], config: SmoothStabilizationConfig | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return separate baseline and regularized timelines for the same source trajectory."""
    settings = config or SmoothStabilizationConfig()
    return _scenario_timeline(source, smooth=False, smooth_config=settings), _scenario_timeline(source, smooth=True, smooth_config=settings)
