# Ingestion externe

Le Studio Cloud normalise quatre chemins externes vers `ratiss.topological-decoherence.timeline.v1`. Aucun adaptateur ne soumet de travail à un fournisseur, ne récupère de secret, ni ne transforme une donnée déclarée en validation matérielle.

```bash
# Statevectors externes
ratiss-topo-demo --statevector-input examples/qiskit-bell-statevector-trajectory.json --output artifacts/external_bell_timeline.json

# Comptages externes
ratiss-topo-demo --counts-input examples/qiskit-counts-trajectory.json --output artifacts/qiskit_counts_timeline.json

# Distributions de modes photoniques
ratiss-topo-demo --photon-input examples/photonic-mode-trajectory.json --output artifacts/photonic_modes_timeline.json

# Matrices de corrélation bio déclarées
ratiss-topo-demo --bio-input examples/bio-correlation-trajectory.json --output artifacts/bio_correlation_timeline.json
```

| Source | Statut | Conversion appliquée | Frontière codée |
|---|---|---|---|
| Statevector Qiskit | Fonctionnelle | Statevector → matrice densité → cube / graphe / topologie | Trajectoire déclarée ; aucune exécution QPU déduite |
| Comptages Qiskit | Fonctionnelle | Comptages → association classique de co-occurrence | Pas de phases, tomographie, entanglement ou matrice densité inférés |
| Modes photoniques | Fonctionnelle | Distributions d’occupation → association de co-occupation de modes | Pas de matrice densité photonique ni interférence non mesurée inférées |
| Corrélations bio | Fonctionnelle | Matrices normalisées déclarées → structure de relations | Pas de cohérence quantique, causalité, diagnostic ou conclusion biologique inférés |

Le contrat de chaque entrée, ses champs requis et ses contraintes de validation sont dans [`INGESTION_CONTRACTS.md`](INGESTION_CONTRACTS.md). Les trois adaptateurs non-densité attribuent `density_metrics_available=false` à chaque étape. Le Studio Personnel affiche alors les routes et criticités comme des structures importées, et non comme une décohérence quantique mesurée.

Lorsque `perceval-quandela` est installé, l’API Python `run_perceval_circuit(circuit, input_occupation)` exécute aussi localement un circuit Perceval via son backend `Naive`, récupère sa distribution de modes, puis applique le même contrat photonique. Cette voie reste une simulation locale ; elle n’envoie aucun calcul vers un processeur distant.
