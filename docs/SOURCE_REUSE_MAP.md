# Carte de réutilisation — branche RATISS `decoherence-map`

## Source contrôlée

La base de réutilisation est la branche `decoherence-map` de **RATISS Experimental IA**, clonée uniquement pour lecture et analyse sous le commit `c67d2e77a54537179b68bbc014fdb2a05fe9ec18` (`2026-08-22`, *pipeline décohérence Day 1*).

> Les dépôts RATISS sources ne sont ni modifiés, ni utilisés comme dépendance implicite au runtime. Le nouveau SDK contient des modules dérivés et testés, avec cette carte de provenance, afin de rester installable indépendamment.

| Source RATISS vérifiée | Capacité déjà présente | Décision dans le SDK | Évolution contrôlée |
|---|---|---|---|
| `ratis_net/lct_modules/topo_qubit.py` | API `TopologicalQubit` : anneau tordu, portes topologiques analogues, bruit, lecture `P_sig`, bit logique et protection | **Réutilisée comme noyau logique** sous `logical_qubit.py` | Conservation de l’encodage par anneau et des portes ; mesure rendue indépendante des imports NLP du dépôt parent |
| `ratis_net/lct_modules/grav_measure.py` | Persistance H1 d’un nuage, Betti et profil cohérence/décohérence | **Réutilisée conceptuellement** dans `PersistentTopologyMeasure` | Backend local transparent de Rips ; sortie stabilisée pour l’artefact timeline |
| `quantum_decoherence_map/circuit_builder.py` | Circuit Qiskit de démonstration à 5 qubits et portes progressives | **Scénario de compatibilité** à conserver dans les exemples | Extension vers matrice densité bruitée étape par étape |
| `quantum_decoherence_map/simulator.py` | Capture d’états à chaque porte et export de densité diagonale | **Contrat d’étapes réutilisé** | Matrice densité complète bruitée et référence idéale, plutôt que diagonale seule |
| `quantum_decoherence_map/topology_extractor.py` | Forme initiale de graphe par étape | **Structure d’export conservée** | Remplacement du proxy trigonométrique par information mutuelle, corrélations Pauli et concurrence calculées |
| `quantum_decoherence_map/psig_calculator.py` | Première route TSP et champ `psig` | **Route TSP conservée uniquement comme inspection** | Séparation stricte : `P_sig` vient désormais de Rips H1, jamais du TSP |
| `data/full_timeline.json` | Premier artefact 5 qubits, étapes, états, graphes et P_sig | **Compatibilité de lecture à prévoir dans l’atlas** | Nouveau schéma versionné enrichi, avec provenance et métriques par nœud/arête |

## Ce qui est validé versus ce qui est renforcé

L’API du qubit topologique existant est une **simulation algorithmique** : elle encode un bit logique dans un invariant topologique d’un réseau de nœuds et évalue sa survie face à un bruit logiciel. Elle est bien la fondation recherchée du SDK. Elle n’est pas une représentation de matériel topologique fabriqué, ni un surface code certifié.

La branche comprend également une première preuve de concept de cartographie à 5 qubits. Sa structure d’artefact, la capture par étapes et son scénario de circuit sont conservés. En revanche, ses deux proxies reconnus — corrélation trigonométrique fixe et `P_sig` dérivé d’une route TSP sur coordonnées triviales — sont remplacés dans le nouveau SDK par des calculs distincts et explicables. Cette évolution ne rejette pas le travail existant : elle le fait passer d’un **embryon de pipeline** à un contrat de simulation exploitable par un SDK et un visualiseur.

## Frontières que le code affichera systématiquement

| Niveau | Formulation autorisée |
|---|---|
| Noyau RATISS | « Qubit topologique logique simulé, encodé dans la persistance H1 d’un réseau. » |
| Cartographie | « Trajectoire de décohérence simulée et métriques topologiques dérivées. » |
| Bio-cohérence | « Profil de cohérence topologique appliqué à une structure ou à des données fournies ; pas une preuve biomédicale ou un diagnostic. » |
| Matériel/QPU | « Adaptateur futur ou données importées ; validation matérielle séparée et explicitement étiquetée. » |
