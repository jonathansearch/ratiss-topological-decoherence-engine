"""RATISS simulated topological logical-qubit core.

Derived from Jonathan Evina's RATISS Experimental IA `decoherence-map` branch,
commit c67d2e77a54537179b68bbc014fdb2a05fe9ec18. The original design encodes a
logical bit in persistent topology of a node network. This standalone variant
keeps that API while removing the original repository's NLP-only imports.

It is an algorithmic simulation, not a claim of hardware topological qubits,
surface-code fault tolerance, or a fabrication model.
"""

from __future__ import annotations

import math

import numpy as np

from .topology import rips_persistence


class PersistentTopologyMeasure:
    """Measure finite H1 persistence and Betti values of a point network."""

    def __init__(self, max_edge: float = 2.5):
        self.max_edge = float(max_edge)

    def measure_density(self, points: np.ndarray) -> dict[str, object]:
        points = np.asarray(points, dtype=float)
        delta = points[:, None, :] - points[None, :, :]
        distances = np.linalg.norm(delta, axis=2)
        np.fill_diagonal(distances, 0.0)
        persistence = rips_persistence(distances, max_edge=self.max_edge)
        return {
            "P_sig": float(persistence["psig"]),
            "n_cycles": int(persistence["n_finite_h1"]),
            "betti": persistence["betti"],
            "diagrams": persistence["diagrams"],
        }

    def oscillation_profile(self, points: np.ndarray, n_steps: int = 8) -> list[dict[str, object]]:
        """Reproduce the source branch’s coherence/decoherence profile scan."""

        points = np.asarray(points, dtype=float)
        norms = np.linalg.norm(points, axis=1)
        curve: list[dict[str, object]] = []
        for step in range(n_steps):
            theta = (math.pi / 2) * step / max(1, n_steps - 1)
            coherence = abs(math.cos(theta))
            quantile = min(0.5, 0.5 * coherence)
            threshold = np.quantile(norms, 1 - quantile) if quantile > 0 else norms.min()
            kept = points[norms <= threshold] if quantile > 0 else points
            if len(kept) < 4:
                curve.append({"theta": theta, "C": coherence, "P_sig": 0.0, "n_kept": int(len(kept))})
                continue
            measurement = self.measure_density(kept)
            curve.append({"theta": theta, "C": coherence, "P_sig": measurement["P_sig"], "betti": measurement["betti"], "n_kept": int(len(kept))})
        return curve


class TopologicalQubit:
    """A simulated RATISS logical bit encoded in a topological network.

    The internal ring, twist gates, noise and protection rule intentionally
    mirror the source branch’s existing algorithmic qubit implementation.
    """

    def __init__(self, n_nodes: int = 12, protection: float = 0.5, seed: int = 42):
        if n_nodes < 4:
            raise ValueError("n_nodes must be at least four for an H1-capable network")
        self.n_nodes = int(n_nodes)
        self.protection = float(protection)
        self.rng = np.random.RandomState(seed)
        self.measure = PersistentTopologyMeasure(max_edge=2.5)
        self._theta = 0.0
        self._twist = 0.0
        self._coherence = 1.0

    def _network(self) -> np.ndarray:
        """Build the source algorithm’s twisted-ring logical-state geometry."""

        points = []
        for index in range(self.n_nodes):
            angle = 2 * math.pi * index / self.n_nodes
            # twist dilate le cycle H1 : |0> = anneau compact (petit P_sig),
            # |1> = anneau étendu (grand P_sig). Contraste ~3× pour le seuil.
            deformation = self._twist / math.pi
            radius = 0.15 + deformation * 1.0 + deformation * 0.1 * math.sin(3 * angle)
            points.append(
                [
                    radius * math.cos(angle),
                    radius * math.sin(angle),
                    (self._twist / math.pi) * 0.3 * math.cos(3 * angle),
                ]
            )
        return np.asarray(points, dtype=float)

    def x_gate(self) -> "TopologicalQubit":
        """Topological NOT analogue: swap the untwisted and twisted residual."""

        self._twist = math.pi - self._twist
        return self

    def h_gate(self) -> "TopologicalQubit":
        """Topological Hadamard analogue: a deliberately intermediate twist."""

        self._twist = math.pi / 2
        self._theta = math.pi / 4
        return self

    def phase_gate(self, delta_theta: float) -> "TopologicalQubit":
        """Apply a phase analogue without altering the topological network."""

        self._theta = (self._theta + float(delta_theta)) % (2 * math.pi)
        return self

    def noise(self, strength: float) -> "TopologicalQubit":
        """Apply software noise; negative noise is invalid and is rejected."""

        if strength < 0:
            raise ValueError("noise strength must be non-negative")
        self._coherence = max(0.0, self._coherence - float(strength))
        return self

    def measure_state(self) -> dict[str, object]:
        """Return the non-destructive simulated topological signature."""

        points = self._network()
        # bruit proportionnel à la décohérence : assez fort pour que la
        # protection topologique soit réellement mise à l'épreuve
        points = points + self.rng.normal(0, (1 - self._coherence) * 0.2, points.shape)
        measured = self.measure.measure_density(points)
        protected = float(measured["P_sig"]) > self.protection
        return {
            **measured,
            "twist": self._twist,
            "phase": self._theta,
            "coherence": self._coherence,
            "protected": bool(protected),
            "logical_bit": int(protected),
            "scope": "algorithmic_topological_logical_qubit_simulation",
        }

    def fidelity_vs_ideal(self) -> float:
        """Source-compatible coherence proxy, explicitly not quantum fidelity."""

        return float(self._coherence)
