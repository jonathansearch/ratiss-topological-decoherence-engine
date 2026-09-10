# Validation QPU — Bell State sur ibm_marrakesh

**Job ID :** 
**Backend :** ibm_marrakesh (IBM Quantum)
**Date :** 2026-08-23
**Circuit :** h(0); cx(0,1); measure_all
**Shots :** 1024

## Résultats QPU

Counts mesurés :


## Transformation via l'engine

Le pipeline  a transformé les counts en document timeline.v1 :
- **Mode :** external_qiskit_counts
- **P_sig :** 0.0000 (counts diagonaux → pas de cycles H1, résultat honnête)
- **Betti :** [1, 0, 0] (1 composante connexe)
- **Validated on hardware :** False (c'est une simulation, pas une validation matérielle)

## Interprétation

Le Bell state mesuré sur QPU réel montre les corrélations attendues (|00⟩ et |11⟩ dominants). La topologie du graphe de corrélation est triviale (pas de cycles persistants) — c'est le résultat honnête pour un état à 2 qubits.

## Limites honnêtes

1. **Ce n'est pas une validation matérielle** — c'est une simulation avec des données QPU réelles
2. **P_sig = 0.0000** est le résultat attendu pour un Bell state simple (pas de structure topologique complexe)
3. **La validation physique complète** nécessite un circuit plus complexe avec des cycles H1 non-triviaux

## Prochaine étape

Soumettre un circuit avec une structure topologique riche (ex: graphe complet 4 qubits) pour mesurer un P_sig non-trivial sur QPU.
