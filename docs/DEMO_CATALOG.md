# Catalogue des démonstrations WebGL — Studio Cloud

Le Studio Cloud contient deux démonstrations interactives servies localement avec `ratiss-studio-cloud`. Elles chargent uniquement des artefacts JSON produits dans ce dépôt ; aucune source réseau, donnée décorative ou soumission distante n’est impliquée.

| Démonstration | URL locale | Artefact | Ce qui est rejoué |
|---|---|---|---|
| Trajectoire de conception → topologie | `/demos/decoherence-trajectory.html` | `artifacts/studio_transmon_microcell_timeline.json` | Import interne Quantum Circuit Studio, compilation logique, observation par étape, nœuds, arêtes et route TSP calculés |
| Ablation TTF | `/demos/ttf-comparison.html` | `artifacts/ttf_smooth_ablation/timeline_baseline.json` et `timeline_regularized.json` | Deux scénarios distincts, frontière de variation, support structurel et route TSP ciblée |

Les deux pages ont été ouvertes avec le serveur local. La première a affiché l’artefact `internal_studio_import`, ses nœuds, son arête et la timeline de conception. La seconde a affiché les deux jeux de données TTF séparés, les boutons de comparaison, la frontière de variation et la clause de portée de l’ablation.

> Une démonstration WebGL visualise les valeurs de l’artefact chargé. Elle ne réalise pas de validation QPU, de calibration, de correction d’erreur matérielle ou de fabrication de composant.

## Médias visibles dans le README

Les aperçus animés sont construits à partir de captures du rendu réel des pages, et non à partir de diagrammes dessinés pour la documentation. Ils permettent de voir la démonstration directement dans GitHub Markdown, où une page WebGL interactive ne peut pas être exécutée de façon sûre.

| Démonstration | Aperçu Markdown | Vidéo versionnée | États réellement capturés |
|---|---|---|---|
| Trajectoire | [`cloud-trajectory-webgl-preview.gif`](media/cloud-trajectory-webgl-preview.gif) | [`cloud-trajectory-webgl.webm`](media/cloud-trajectory-webgl.webm) | Étapes `1 / 3`, `2 / 3` et `3 / 3` de `internal_studio_import` |
| Ablation TTF | [`cloud-ttf-webgl-preview.gif`](media/cloud-ttf-webgl-preview.gif) | [`cloud-ttf-webgl.webm`](media/cloud-ttf-webgl.webm) | `ttf_smooth_baseline`, puis `ttf_smooth_regularized` |

La capture de l’espace de travail complet est conservée dans [`media/cloud-studio-workspace.webp`](media/cloud-studio-workspace.webp). Les conditions de contrôle visuel, les éléments effectivement visibles et les limites de portée sont consignés dans [`DEMO_VISUAL_AUDIT.md`](DEMO_VISUAL_AUDIT.md).
