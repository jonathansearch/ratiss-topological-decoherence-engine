"""RATISS Topological Decoherence Engine.

Local SDK for producing traceable, topological inspection artifacts from
simulated (or explicitly imported) quantum-state trajectories.
"""

from .simulation import GateSpec, SimulationConfig, run_local_demo, run_program
from .studio_import import compile_studio_document, run_studio_document, run_studio_file
from .external_statevector import run_qiskit_statevector_file, run_qiskit_statevector_trajectory
from .correlation_import import run_bio_correlation_file, run_bio_correlation_trajectory, run_perceval_circuit, run_perceval_distribution, run_photonic_mode_file, run_photonic_mode_trajectory, run_qiskit_counts_file, run_qiskit_counts_trajectory

__all__ = ["GateSpec", "SimulationConfig", "compile_studio_document", "run_bio_correlation_file", "run_bio_correlation_trajectory", "run_local_demo", "run_perceval_circuit", "run_perceval_distribution", "run_photonic_mode_file", "run_photonic_mode_trajectory", "run_program", "run_qiskit_counts_file", "run_qiskit_counts_trajectory", "run_qiskit_statevector_file", "run_qiskit_statevector_trajectory", "run_studio_document", "run_studio_file"]
__version__ = "0.1.0"
