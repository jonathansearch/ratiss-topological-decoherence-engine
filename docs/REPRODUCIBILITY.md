# Reproductibilité et validation locale

## Préparation

Utilisez un environnement Python isolé, puis installez le paquet en mode éditable. Les versions déclarées dans `pyproject.toml` constituent la source de vérité des dépendances.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Recette minimale

```bash
ratiss-topo-demo --output artifacts/reproduced_full_timeline.json
PYTHONPATH=src pytest
```

Le premier appel produit un contrat `ratiss.topological-decoherence.timeline.v1`. Le second exécute les tests de persistance, TSP, pipeline densité, noyau logique, importer Studio, statevectors, comptages, photonique, corrélations et ablation TTF.

| Vérification | Commande | Signal de réussite |
|---|---|---|
| Simulation locale | `ratiss-topo-demo --output …` | Un JSON avec `steps`, `provenance` et `config` |
| Tests Python | `PYTHONPATH=src pytest` | Toutes les assertions réussissent |
| Interface Cloud | `ratiss-studio-cloud` | `GET /api/health` répond avec le profil local/self-hosted |
| Démo trajectoire | Ouvrir `/demos/decoherence-trajectory.html` | Timeline interne et scène WebGL affichées |
| Démo TTF | Ouvrir `/demos/ttf-comparison.html` | Bascule référence/régularisation fonctionnelle |

## Artefacts de référence

Les artefacts committés sont des exemples reproductibles et non des résultats QPU. Ils permettent de vérifier la compatibilité avec le Studio Personnel.

| Artefact | Origine | Rôle |
|---|---|---|
| `artifacts/full_timeline.json` | POC densité local | Référence de cartographie temporelle |
| `artifacts/studio_transmon_microcell_timeline.json` | Modèle Quantum Circuit Studio interne | Démo de conception → timeline |
| `artifacts/external_bell_timeline.json` | Fixture Statevector Bell | Contrat Statevector |
| `artifacts/qiskit_counts_timeline.json` | Fixture de comptages | Associations classiques déclarées |
| `artifacts/photonic_modes_timeline.json` | Fixture de modes | Co-occupations déclarées |
| `artifacts/bio_correlation_timeline.json` | Fixture de corrélations | Entrée générique sans diagnostic |
| `artifacts/ttf_smooth_ablation/*` | Ablation locale | Référence/régularisation de graphe |

## Critères de lecture

Une reproduction est correcte si le schéma du JSON, les nombres d’étapes, les marqueurs de provenance et les limites de chaque entrée sont conservés. Les petites différences numériques dues à une dépendance, une plateforme ou une version doivent être consignées ; elles ne doivent pas être silencieusement normalisées.
