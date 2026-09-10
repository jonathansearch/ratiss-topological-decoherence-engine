# Référence d’API

## API Python

| Objet | API | Résultat |
|---|---|---|
| Configuration | `SimulationConfig(...)` | Paramètres du circuit, bruit, seuil de graphe, seuil de criticité et scénario |
| Démonstration | `run_local_demo(config=None)` | Document `timeline.v1` JSON-sérialisable |
| Qubit logique | `TopologicalQubit(n_nodes=12, protection=0.15, seed=42)` | Noyau topologique logique logiciel dérivé de RATISS |
| Porte logique | `x_gate()`, `h_gate()`, `phase_gate(delta_theta)` | Mutent le réseau topologique simulé et retournent l’instance |
| Bruit logique | `noise(strength)` | Dégrade la cohérence logicielle ; refuse les valeurs négatives |
| Mesure logique | `measure_state()` | `P_sig`, Betti, cycles, phase, torsion, cohérence, état protégé et bit logique |
| Mesure de structure | `PersistentTopologyMeasure.measure_density(points)` | Persistance H1 finie et Betti d’un nuage de points |
| Route | `inspection_route(coordinates, node_ids)` | Cycle TSP fermé, coût et méthode |

## `SimulationConfig`

```python
SimulationConfig(
  n_qubits=5,
  scenario="accelerated_decoherence_stress_demo",
  t1_seconds=100e-6,
  t2_seconds=50e-6,
  single_gate_seconds=4e-6,
  two_gate_seconds=12e-6,
  one_qubit_depolarizing=0.001,
  two_qubit_depolarizing=0.01,
  edge_threshold=0.04,
  criticality_threshold=0.38,
)
```

Le scénario fourni doit être considéré comme un profil de visualisation stressé. Les durées de porte sont exportées avec le résultat et doivent être remplacées pour tout protocole de comparaison spécifique.

## Contrat `ratiss.topological-decoherence.timeline.v1`

| Champ | Type | Sens |
|---|---|---|
| `schema` | chaîne | Version du contrat : `ratiss.topological-decoherence.timeline.v1` |
| `provenance` | objet | Mode, moteur, simulation, limite de revendication et booléen de validation matérielle |
| `encoding` | objet | Profil logique et source du noyau RATISS |
| `config` | objet | Paramètres effectifs du run |
| `cube` | objet | Axes et normalisation de la matrice cubique |
| `steps[]` | tableau | Une observation par porte, plus l’état initial |
| `steps[].cube_slice` | matrice | `M[k,:,:]` normalisée à partir de l’information mutuelle |
| `steps[].qubits[]` | tableau | Mesures et criticité par qubit |
| `steps[].edges[]` | tableau | Corrélation, concurrence, type, stabilité et statut de lien |
| `steps[].topology` | objet | Topologie issue du graphe de corrélations, dont `psig` et Betti |
| `steps[].logical_topology` | objet | Signature du noyau logique RATISS, distincte du graphe |
| `steps[].tsp_inspection` | objet | Route d’inspection calculée sur nœuds critiques, distincte de la persistance |

Un producteur doit exporter `provenance.validated_on_hardware=false` lorsque la trajectoire vient d’un simulateur. Un consommateur doit afficher la provenance au lieu de déduire une validation matérielle de la présence de valeurs quantiques.

## Algorithmes et complexité

| Fonction | Taille recommandée | Complexité dominante | Stratégie |
|---|---:|---:|---|
| Matrice densité dense | ≤ 10–12 qubits sur machine modeste | Mémoire `O(4^n)` | Démonstration livrée : 5 qubits |
| Réductions et information mutuelle | `n(n-1)/2` paires | Croît avec les réductions de densité | Exporter seulement les métriques nécessaires |
| Rips local | 5–20 nœuds | Combinatoire en triangles | Transparence privilégiée ; backend spécialisé futur possible |
| TSP exact | ≤ 10 nœuds critiques | `O(2^m m²)` | Hold–Karp exact |
| TSP large | > 10 nœuds critiques | Heuristique | Voisin le plus proche + 2-opt, méthode exportée |

## Compatibilité d’artefact

L’atlas accepte ce contrat directement. Son adaptateur lit aussi l’ancien artefact `decoherence-map` `{timeline, states, graphs, n_qubits}`. Les champs absents dans cet ancien format restent absents : l’atlas ne les invente pas.
