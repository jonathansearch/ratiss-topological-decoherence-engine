# Contrat des deux studios RATISS

## But commun

Les deux produits sont des studios installables individuellement. Dans les deux cas, le modèle Quantum Circuit Studio devient la couche de conception interne : un utilisateur décrit un circuit et sa topologie, puis le pipeline RATISS produit des représentations de corrélations, de structure topologique, de criticité et de trajectoires d’inspection.

> La fonction du studio est d’explorer des scénarios, rendre les hypothèses auditées et préparer des priorités expérimentales. Une simulation n’est jamais présentée comme la démonstration d’une correction de décohérence sur un processeur physique.

| Dimension | RATISS Quantum Topology Studio Cloud | RATISS Quantum Topology Studio Personal |
|---|---|---|
| Dépôt actuel transformé | `ratiss-topological-decoherence-engine` | `ratiss-decoherence-atlas` |
| Public | Recherche, audit de circuit, expérimentations intensives et intégrations | Développement personnel, démonstration, audit visuel local et formation |
| Installation | Un dépôt unique contenant conception, moteur Python, UI, artefacts et adaptateurs | Un dépôt unique contenant éditeur local, runtime de simulation léger et WebGL hors ligne |
| Calcul | Exécution locale possible ; prêt pour une machine Linux/CPU multi-cœur ou GPU choisi par l’utilisateur | CPU personnel et navigateur ; petit nombre de qubits et algorithmes frugaux |
| Conception | Modèle complet Quantum Circuit Studio : composants, topologie, couches, fréquence, collision, diaphonie et exports | Sous-ensemble JSON compatible : qubits, liens, positions, fréquences nominales et risques visibles |
| Topologie RATISS | Matrice densité, cube `M[k,i,j]`, Rips, `P_sig`, noyau logique, criticité, TSP et importeurs externes | Lecture/production légère d’artefacts compatibles, noyau logique, carte WebGL et import/export JSON |
| Entrées externes | Qiskit statevector d’abord ; interfaces dédiées pour photonique et autres sources | Import de `timeline.v1` et de circuits Studio exportés par le Studio Cloud |
| Dépendance entre dépôts | Aucune au runtime | Aucune au runtime |

## Contrat de compatibilité

Les deux studios partagent deux documents JSON versionnés :

1. `quantum-circuit-studio/v0.1` pour la conception des composants et leurs relations.
2. `ratiss.topological-decoherence.timeline.v1` pour les trajectoires et leurs métriques calculées.

Le Studio Cloud produit les deux. Le Studio Personal sait importer, éditer dans sa portée, simuler les profils légers déclarés et rejouer la timeline. Un utilisateur ne doit jamais devoir cloner les deux dépôts pour effectuer une tâche de base.

## Hypothèses de mitigation

Le Studio peut comparer des **scénarios de mitigation logiciels** : variation déclarée d’un profil de bruit, changement de topologie logique, modification d’ordre de portes, déplacement de l’attention vers une zone critique, ou comparaison de deux designs Studio. Chaque scénario conserve son jeu de paramètres, son artefact et son résultat.

Les résultats classent des hypothèses dans le cadre du modèle choisi. Ils ne constituent ni une instruction de contrôle matériel, ni une correction d’erreur, ni une performance attendue sur un QPU. Une validation matérielle nécessite ensuite le backend, le calibrage, les mesures, les shots et les identifiants de jobs correspondants.

## Profil de puissance

Le mot « Cloud » désigne ici un profil d’exécution séparé et extensible, pas une dépendance obligatoire à un fournisseur. Le Studio Cloud sera conçu pour se lancer localement, puis être déplacé vers une machine Linux plus puissante lorsque la taille de matrice densité, le nombre de scénarios ou les adaptateurs le nécessitent. Les secrets d’adaptateurs restent hors des artefacts et hors du navigateur.
