# Index des preuves exécutables

Cette page relie chaque affirmation de fonctionnement à un fichier, un test ou une démonstration de ce dépôt. Elle ne remplace pas une validation externe ; elle rend le travail local consultable et reproductible.

| Sujet | Source exécutable | Test ou contrôle | Résultat documenté |
|---|---|---|---|
| Simulation densité | `simulation.py` | `tests/test_pipeline.py` | Timeline en étapes et cube de relations |
| Persistance et graphe | `topology.py` | `tests/test_topology.py` | Betti et `P_sig` calculés pour le graphe défini |
| Inspection de sous-ensemble | `tsp.py` | `tests/test_tsp.py` | Route exacte ou heuristique déterministe, séparée de `P_sig` |
| Noyau logique RATISS | `logical_qubit.py` | `tests/test_logical_qubit.py` | Signature logique logicielle séparée |
| Import Quantum Studio | `studio_import.py` | `tests/test_studio_import.py` | Design JSON compilé dans une timeline |
| Statevectors | `external_statevector.py` | `tests/test_external_statevector.py` | Fixture Bell convertie en timeline |
| Comptages | `correlation_import.py` | `tests/test_qiskit_counts.py` | Associations classiques déclarées |
| Photonique et corrélations | `correlation_import.py` | `tests/test_photonic_and_bio.py`, `tests/test_perceval_direct.py` | Entrées déclarées, sans inférence de densité absente |
| Ablation TTF | `ttf_stabilization.py` | `tests/test_ttf_stabilization.py`, `tests/test_ttf_ablation_cli.py` | Deux artefacts distincts, référence/régularisation |
| Démonstrations Cloud | `web/demos/` | Ouverture locale consignée dans `DEMO_CATALOG.md` | Replays WebGL à partir d’artefacts versionnés |

## Statut de validation

Toutes les lignes de cet index établissent une validation logicielle locale limitée au comportement de code et aux données fournies. Elles ne constituent pas une validation QPU, une caractérisation EM, un diagnostic physique ou une démonstration de correction matérielle.
