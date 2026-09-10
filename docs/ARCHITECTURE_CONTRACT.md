# Contrat d’architecture — RATISS Topological Decoherence Engine

## 1. Objet précis du SDK

RATISS Topological Decoherence Engine est un **SDK de simulation et d’inspection**. Il construit des trajectoires quantiques bruitées, dérive des matrices de corrélation à trois axes, identifie la structure topologique des graphes associés et produit des artefacts rejouables localement.

> Le SDK simule un **encodage logique topologique expérimental** sur un graphe de qubits. Il ne prétend pas fabriquer, calibrer ou certifier un qubit topologique matériel. Un futur adaptateur QPU peut alimenter le même contrat de données, mais une validation matérielle reste une expérience distincte.

Le terme « qubit topologique RATISS » désigne donc dans la première version un **objet logique simulé** : une information distribuée sur plusieurs qubits dont la stabilité est inspectée par les invariants et la persistance d’un graphe de corrélations.

| Couche | Rôle | Ce qu’elle produit | Ne prétend pas faire |
|---|---|---|---|
| Simulation | Évolution dense locale avec bruit, idéal vs bruité | Matrices densité et trajectoire par porte | Reproduire un QPU donné sans calibration |
| Encodage logique | Préparation d’un état distribué à deux clusters / cycle H1 | Support logique composé de plusieurs qubits | Implémenter un surface code ou une protection matérielle démontrée |
| Topologie | Rips sur représentation de corrélation, Betti et persistance | `P_sig`, diagrammes, indicateurs de cycle | Mesurer directement un observable matériel appelé « topologie » |
| Inspection | Criticité, rupture de liens et route TSP | Zones et chemin d’inspection | Corriger automatiquement une erreur quantique réelle |
| Visualisation | Artefact JSON, atlas WebGL et rapport | Relecture explicable et portable | Substituer une simulation ou une mesure |

## 2. Profils d’exécution

Le même SDK expose deux profils. Aucune connexion n’est obligatoire pour le fonctionnement principal.

| Profil | Exécution | Cas d’usage | Politique de dépendance |
|---|---|---|---|
| `local` | Qiskit Aer + NumPy/SciPy sur CPU | POC, tests, génération d’artefacts, machine modeste | Par défaut ; sans réseau ni secret |
| `adapter` | Import de résultats ou soumission explicite via un adaptateur installé par l’utilisateur | Comparer une trajectoire locale avec des résultats d’un simulateur ou QPU externe | Désactivé par défaut ; aucun jeton dans le dépôt ; aucune soumission implicite |

Les adaptateurs ne modifient pas l’analyse topologique. Ils convertissent seulement des résultats mesurés en une version documentée du même artefact `timeline.v1`.

Le scénario de démonstration livré par défaut est nommé `accelerated_decoherence_stress_demo`. Il conserve `T1=100 μs` et `T2=50 μs`, mais emploie volontairement des fenêtres de porte effectives longues (`4 μs` et `12 μs`) pour créer, sur onze étapes, des ruptures visibles et donc exercer le visualiseur. Cette accélération est exportée dans `config.scenario`; elle n’est ni une durée de porte revendiquée pour un QPU donné, ni une calibration matérielle.

## 3. Matrice topologique cubique

À l’étape `k`, le moteur obtient la matrice densité bruitée globale `ρ_k` et l’état idéal de référence `ρ*_k`. Pour chaque paire de qubits `(i,j)`, il construit :

\[
M[k,i,j] = \min\left(1, \frac{I(\rho_{ij})}{2}\right)
\]

où `ρij` est la réduction sur `(i,j)` et `I(ρij)=S(ρi)+S(ρj)-S(ρij)` est l’information mutuelle quantique, en bits. Pour deux qubits, la normalisation par 2 rend cette couche comparable dans `[0,1]`.

La matrice `M` décrit des **corrélations totales** (quantique et classique) ; elle ne doit pas être présentée comme une mesure d’intrication à elle seule. Le moteur exporte donc en parallèle :

| Champ | Définition | Usage |
|---|---|---|
| `mutual_information` | `M[k,i,j]` normalisée | Poids initial du graphe |
| `pauli_correlation` | moyenne des corrélations XX, YY et ZZ | Signature structurale complémentaire |
| `fidelity_to_ideal[i]` | fidélité entre réductions bruitée et idéale | Détection locale de dérive dans la simulation |
| `local_decoherence[i]` | `1 - fidelity_to_ideal[i]` | Couleur et criticité du nœud |
| `topology_support[i]` | support local dérivé du graphe et de la participation aux liens persistants | Taille/score du nœud, pas une persistance H1 individuelle |

## 4. Graphe, persistance et criticité

À chaque étape, le graphe `G_k=(V,E_k)` conserve une arête lorsque la combinaison de corrélation a franchi un seuil traçable. Son poids est exporté, sans que la visualisation ne fabrique de lien supplémentaire.

La persistance globale `P_sig[k]` est la durée de vie du cycle H1 fini le plus long dans la filtration de Rips. Elle est donc calculée **indépendamment** de la route TSP. Les nombres de Betti et les diagrammes sont associés à la même filtration.

La criticité exportée est un score d’inspection configurable, pas une grandeur physique universelle :

\[
\mathrm{criticality}_i = 0.60(1-F_i) + 0.25(1-\bar M_i) + 0.15\,\mathrm{break}_i
\]

avec `Fi` la fidélité locale simulée, `M̄i` la force moyenne des liens et `break_i` l’indicateur de rupture de voisinage. Le détail des coefficients et de chaque terme est exporté pour permettre la contestation ou le remplacement de la politique.

Pour le scénario de stress fourni, le seuil configurable est fixé à `0,38`. Il ne représente pas un seuil matériel universel : il est choisi pour transformer les scores de criticité calculés du POC en un petit ensemble d’inspection non trivial et donc exercer la route TSP dans l’atlas.

## 5. Route TSP : fonction et frontière

La route TSP est une **route d’inspection** des nœuds critiques ou des événements mémorisés. Elle est calculée sur leurs coordonnées déterministes avec Hold–Karp pour les petits ensembles, puis voisin le plus proche + 2-opt pour les ensembles plus grands. Elle ne participe ni au calcul de `P_sig`, ni à la dynamique quantique, ni à une correction d’erreur matérielle.

| Calcul | Entrée | Sortie | Finalité |
|---|---|---|---|
| Persistance H1 | Filtration Rips du graphe | `P_sig`, Betti, diagrammes | Mesurer une structure topologique dérivée |
| TSP | Sous-ensemble de nœuds critiques et coordonnées | Ordre de visite, coût, méthode | Rendre le parcours d’inspection lisible et reproductible |

## 6. Contrat d’artefact partagé

Le fichier principal suit le type `ratiss.topological-decoherence.timeline.v1`. Il est l’interface stricte entre le moteur lourd et l’atlas léger.

```json
{
  "schema": "ratiss.topological-decoherence.timeline.v1",
  "provenance": {
    "mode": "local",
    "engine": "ratiss-topological-decoherence-engine",
    "simulation": "density_matrix",
    "validated_on_hardware": false
  },
  "encoding": {
    "profile": "h1_distributed_logical_state",
    "description": "Encodage logique simulé sur plusieurs qubits."
  },
  "cube": {"axes": ["step", "source_qubit", "target_qubit"], "metric": "normalized_mutual_information"},
  "steps": [
    {
      "step": 0,
      "gate": "initial",
      "qubits": [{"id": 0, "position": [0, 0, 0], "fidelity_to_ideal": 1.0, "local_decoherence": 0.0, "topology_support": 1.0, "criticality": 0.0}],
      "edges": [{"source": 0, "target": 1, "mutual_information": 0.8, "pauli_correlation": 0.7, "type": "correlation"}],
      "topology": {"psig": 0.0, "betti": [1, 0, 0], "method": "rips_persistence"},
      "tsp_inspection": {"path": [], "cost": 0.0, "method": "trivial"}
    }
  ]
}
```

Les versions successives doivent conserver le préfixe de schéma. Un consommateur ne doit jamais interpréter un artefact sans afficher au moins `mode`, `simulation` et `validated_on_hardware`.

## 7. Primitives vérifiées dans les dépôts lus en lecture seule

| Primitive disponible | Usage prévu dans le nouveau SDK | Statut de provenance |
|---|---|---|
| État 6-qubits à deux clusters + rotation `Ry` | Profil d’encodage de démonstration, reformulé et réimplémenté | Concept vérifié dans un script RATISS existant |
| Corrélations XX/YY/ZZ depuis comptes | Adaptateur facultatif de résultats mesurés | Concept vérifié dans un script QPU existant |
| Tomographie par ombres et matrice de corrélation | Mode d’estimation à faible nombre de snapshots, optionnel | Concept vérifié dans le module local existant |
| Rips, Betti et `P_sig` H1 fini | Analyse topologique de graphe de corrélations | Concept vérifié dans le noyau TTF existant |
| Hold–Karp et voisin + 2-opt | Route d’inspection séparée | Concept vérifié dans le noyau TTF existant |

Ces briques sont **réimplémentées** dans le dépôt nouveau avec des tests dédiés. Aucun fichier des dépôts existants n’est modifié ni importé comme dépendance cachée.

## 8. Références externes

La simulation locale dense s’appuie sur le mode `density_matrix` de Qiskit Aer. L’API permet également de sauvegarder les matrices densité à des étapes choisies. Les définitions d’entropie, d’information mutuelle, de trace partielle et de fidélité employées ici sont fournies par `qiskit.quantum_info`. [1] [2] [3]

## Références

[1]: https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html "Qiskit Aer — AerSimulator"
[2]: https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.library.save_density_matrix.html "Qiskit Aer — save_density_matrix"
[3]: https://quantum.cloud.ibm.com/docs/api/qiskit/quantum_info "Qiskit — quantum_info"
