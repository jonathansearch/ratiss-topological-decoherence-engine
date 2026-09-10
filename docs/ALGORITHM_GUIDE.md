# Guide des algorithmes du Studio Cloud

## 1. Une timeline, plusieurs niveaux d’interprétation

Le contrat `timeline.v1` existe pour qu’un résultat soit rejouable sans réexécuter la simulation. Une étape peut contenir un état simulé, un graphe dérivé, des attributs de criticité, une route d’inspection et une signature logique. Ces objets ne sont pas interchangeables.

| Champ | Nature | Mauvaise interprétation à éviter |
|---|---|---|
| `cube_slice[i][j]` | Relation normalisée à une étape de simulation densité | Appeler toute relation une mesure matérielle |
| `topology.psig` | Longueur H1 finie dans la filtration du graphe défini | Confondre avec la signature du noyau logique |
| `logical_topology.P_sig` | Signal du `TopologicalQubit` logiciel RATISS | Le présenter comme persistance du graphe de corrélations |
| `criticality` | Score de sélection transparent pour l’inspection | Diagnostic ou taux d’erreur d’un QPU |
| `tsp_inspection.path` | Ordre de parcours d’un sous-ensemble de nœuds | Contribution au calcul de `P_sig` |

## 2. Simulation à matrice densité

Le profil local utilise Qiskit Aer pour produire une référence et une trajectoire bruitée. Après chaque opération, le moteur réduit l’état global vers les systèmes à un et deux qubits. L’information mutuelle est ensuite normalisée pour remplir la tranche `M[k,:,:]`.

\[
I(A:B) = S(\rho_A) + S(\rho_B) - S(\rho_{AB})
\]

Cette relation organise la structure de graphe, mais elle n’établit pas par elle-même un mécanisme matériel de décohérence. Les détails d’Aer sont disponibles dans sa documentation officielle [1].

## 3. Graphe, Rips et persistance

Chaque tranche est convertie en un graphe pondéré dont les positions sont déterministes. Une filtration Rips est évaluée avec les distances entre profils de corrélation. Le moteur enregistre le nombre de composantes, les cycles H1 finis et la longueur maximale : `P_sig`.

> `P_sig = 0` signifie seulement qu’aucun cycle H1 **fini persistant** n’a été trouvé dans la filtration courante. Ce champ ne prouve pas à lui seul une décohérence complète.

## 4. Criticité et route TSP

La criticité combine les termes disponibles du scénario, par exemple une perte de fidélité, un déficit topologique ou une rupture de relation. Les nœuds dépassant le seuil déclaré constituent un ensemble d’inspection. `tsp_minimal` exécute Hold–Karp sur les petits ensembles ; une heuristique déterministe est utilisée au-delà. Sa route est conservée pour guider la lecture d’un graphe, sans influencer la persistance.

## 5. Noyau de qubit topologique logique RATISS

Le composant `TopologicalQubit` provient de la branche RATISS Experimental IA `decoherence-map`, référencée dans [`SOURCE_REUSE_MAP.md`](SOURCE_REUSE_MAP.md). Il fournit un anneau logique, une torsion, des opérations analogues aux portes et une injection de bruit logiciel. Son `P_sig` est exporté sous `logical_topology`, séparément de `topology.psig`.

## 6. Ablation de stabilisation TTF

L’ablation TTF ne modifie pas un état quantique ni une matrice densité. Elle applique un profil lisse et borné à des relations de graphe autour des nœuds de frontière exportés. Elle produit toujours deux artefacts : **référence** et **régularisation**. La comparaison de support est donc calculée et inspectable, mais son résultat n’est pas une preuve de correction d’erreur. Voir [`TTF_SMOOTH_STABILIZATION.md`](TTF_SMOOTH_STABILIZATION.md).

## 7. Entrées externes

Les imports préservent l’épistémologie de leurs données : statevector, comptages classiques, occupations photoniques et matrices de corrélation n’ont pas le même contenu informationnel. L’adaptateur inscrit cette différence dans `provenance`, `input_kind` et les métriques omises. Le contrat détaillé est dans [`INGESTION_CONTRACTS.md`](INGESTION_CONTRACTS.md).

## Référence

[1] [Qiskit Aer — AerSimulator](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html).
