# Contrats d’ingestion restants

Chaque adaptateur produit `ratiss.topological-decoherence.timeline.v1`, mais la provenance conserve le type de mesure ou de relation source. Le Studio Personnel rejoue ces artefacts sans interpréter leur origine comme une matrice densité ou une validation matérielle.

## Comptages Qiskit

```json
{
  "source": {"backend": "declared-backend", "job_id": "optional-job-id"},
  "bit_order": "qiskit_little_endian",
  "trajectory": [
    {"step": 0, "gate": "measurement", "counts": {"00": 510, "11": 490}}
  ]
}
```

Les comptages sont convertis en une matrice d’**association classique de co-occurrence**. L’adaptateur ne reconstruit pas des phases ou une matrice densité à partir d’une seule base de mesure. Sa provenance est `external_qiskit_counts` et l’artefact porte `density_matrix_available=false`.

## Distributions photoniques

```json
{
  "source": {"framework": "declared-photonic-source"},
  "mode_labels": ["m0", "m1", "m2"],
  "trajectory": [
    {
      "step": 0,
      "label": "declared-mode-distribution",
      "outcomes": [
        {"occupation": [1, 1, 0], "probability": 0.5},
        {"occupation": [0, 0, 1], "probability": 0.5}
      ]
    }
  ]
}
```

L’occupation est un vecteur de modes non négatifs. L’adaptateur normalise les probabilités puis calcule une association de co-occupation de modes. Il ne prétend pas inférer une matrice densité photonique, une interférence non observée ou une validation de dispositif. Sa provenance est `external_photonic_modes`.

## Matrices de corrélation bio

```json
{
  "source": {"dataset": "declared-dataset", "measurement_protocol": "required-description"},
  "labels": ["signal_0", "signal_1"],
  "trajectory": [
    {
      "step": 0,
      "label": "window-0",
      "correlation_matrix": [[1.0, 0.42], [0.42, 1.0]]
    }
  ]
}
```

La matrice doit être carrée, symétrique, finie et normalisée dans `[0,1]`, avec diagonale à `1`. Le moteur traite cette matrice comme une structure de relations déclarée ; aucune cohérence quantique, causalité biologique ou conclusion médicale n’est calculée. Sa provenance est `external_bio_correlation`.

## Champs communs d’artefact

Les trois adaptateurs exportent des nœuds, arêtes, Betti, `P_sig` de graphe, criticité structurelle et route TSP. Les champs de fidélité, pureté et signature logique qui nécessiteraient une matrice densité restent `null` et portent une interprétation dans `metric_scope`. Un consommateur ne doit pas transformer ces valeurs absentes en zéro ni en résultat de décohérence quantique.
